# app/workers/pipeline_worker.py
import asyncio
from pathlib import Path

from sqlalchemy.ext.asyncio import AsyncSession

from app.database import AsyncSessionLocal
from app.core.status import RequestStatus
from app.repositories import (
    request_repository,
    lecture_repository,
    presentation_repository,
    transcript_repository,
    summary_repository,
)
from app.services.parser_service import ParserService
from app.services.speech_service import SpeechService
from app.services.summary_service import SummaryService
from app.services.pdf_service import PdfService

from app.logger import setup_logger, logger

# initialize module logger
setup_logger("pipeline_worker")


class PipelineWorker:
    PATH_FILES = Path("./data")

    def __init__(self) -> None:
        self.parser_service = ParserService()
        self.speech_service = SpeechService()
        self.summary_service = SummaryService()
        self.pdf_service = PdfService()

    async def run(self) -> None:
        """Запускает цикл воркера; периодически проверяет наличие новых заявок."""
        logger.info("Воркер пайплайна запущен")
        while True:
            try:
                await self.process_next_job()
            except Exception as err:
                logger.exception("Неожиданная ошибка в воркере")
            await asyncio.sleep(10)

    async def process_next_job(self) -> None:
        """Получает следующую заявку со статусом PENDING и прогоняет её через этапы."""
        async with AsyncSessionLocal() as db:
            request = await request_repository.get_next_pending_request(db)
            if request is None:
                return

            logger.info(f"Обработка заявки {request.id}")
            await request_repository.start_processing(db, request.id)

            lecture = await lecture_repository.get_lecture(db, request.lecture_id)
            if lecture is None:
                logger.warning(f"Lecture {request.lecture_id} not found for request {request.id}")
                await request_repository.update_request_status(db, request.id, RequestStatus.FAILED)
                return

            try:
                # Убедиться, что папка для лекции существует
                lecture_path = self.PATH_FILES / str(lecture.id)
                lecture_path.mkdir(parents=True, exist_ok=True)

                transcript = await self.run_parser(db, lecture)
                path_to_transcript = await self.run_speech(db, lecture, transcript)
                await self.run_summary(db, lecture.id, path_to_transcript)
                await self.run_pdf(db, lecture.id)

                await request_repository.finish_request(db, request.id)
            except Exception:
                logger.exception(f"Пайплайн не удалось выполнить для заявки {request.id}")
                await request_repository.update_request_status(db, request.id, RequestStatus.FAILED)

    async def run_parser(self, db: AsyncSession, lecture) -> object:
        logger.info(f"Этап парсинга для лекции {lecture.id}")

        presentation_dir = await self.parser_service.download_slides(lecture.url, lecture.id)
        # generate simple timing map: index**2 -> index
        slides = list(presentation_dir.glob("slide*.svg"))
        slides_timings = {i * i: i for i in range(1, len(slides) + 1)}

        # TODO: позже заменить на реальный алгоритм получения таймингов; сейчас временно квадратичная функция
        if lecture.url == "https://bbb.ssau.ru:8443/playback/presentation/2.3/097c80a16ee9277077ca6a347f6e8f9c597b9a62-1759998690614":
            slides_timings = {"0": 23, "216": 24, "360": 25, "534": 26, "769": 27, "862": 28, "903": 29, "980": 30, "1091": 31, "1241": 32, "1386": 33, "1533": 34, "1607": 35, "1729": 36, "1773": 37, "1792": 38, "1822": 39, "2007": 40, "2140": 41, "2185": 42}

        audio_path = await self.parser_service.download_audio(lecture.url, lecture.id)

        await presentation_repository.create_presentation(
            db=db,
            lecture_id=lecture.id,
            slides_timings=slides_timings,
            presentation_path=str(presentation_dir),
        )

        transcript = await transcript_repository.create_transcript(
            db=db,
            lecture_id=lecture.id,
            audio_path=str(audio_path),
        )
        return transcript

    async def run_speech(self, db: AsyncSession, lecture, transcript) -> Path:
        logger.info(f"Этап распознавания речи для лекции {lecture.id}")

        uri = await self.speech_service.upload_file(transcript.audio_path)
        operation_id = await self.speech_service.start_recognition(uri)
        await transcript_repository.set_transcript_path(
            db=db, transcript=transcript, transcript_path=operation_id
        )

        await self.speech_service.wait_operation(operation_id)
        text = await self.speech_service.get_result(operation_id)
        formatted = await self.speech_service.parse_result(text)

        transcript_file = self.PATH_FILES / str(lecture.id) / "transcript.txt"
        saved_path = await self.speech_service.save_to_file(formatted, transcript_file)

        await transcript_repository.set_transcript_path(
            db=db, transcript=transcript, transcript_path=saved_path
        )
        return saved_path

    async def run_summary(self, db: AsyncSession, lecture_id: int, path_to_transcript: Path) -> None:
        logger.info(f"Этап обобщения для лекции {lecture_id}")

        presentation = await presentation_repository.get_presentation_by_lecture_id(db, lecture_id)
        slide_timings = presentation.slides_timings

        summary_file = self.PATH_FILES / str(lecture_id) / "summary.txt"
        saved_path = await self.summary_service.summarize_from_file(
            transcript_path=path_to_transcript,
            slide_timings=slide_timings,
            output_path=str(summary_file),
        )

        annotation = await self.summary_service.generate_annotation(saved_path)
        await summary_repository.create_summary(
            db=db,
            lecture_id=lecture_id,
            annotation=annotation,
            summary_path=saved_path,
        )

    async def run_pdf(self, db: AsyncSession, lecture_id: int) -> None:
        logger.info(f"Этап генерации PDF для лекции {lecture_id}")

        summary = await summary_repository.get_summary_by_lecture_id(db, lecture_id)
        presentation = await presentation_repository.get_presentation_by_lecture_id(db, lecture_id)

        pdf_file = self.PATH_FILES / str(lecture_id) / "lecture.pdf"
        saved_path = await self.pdf_service.generate_pdf_from_summary(
            summary_path=summary.summary_path,
            slides_dir=presentation.presentation_path,
            output_path=str(pdf_file),
        )

        await summary_repository.set_summary_path(
            db=db, summary=summary, summary_path=saved_path
        )
