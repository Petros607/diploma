# app/workers/pipeline_worker.py
import asyncio
from sqlalchemy import select

from app.database import AsyncSessionLocal
from app.models.request import Request
from app.core.status import RequestStatus
from app.repositories import lecture_repository, request_repository
from app.services.parser_service import ParserService
from app.services.speech_service import SpeechService
from app.services.summary_service import SummaryService


class PipelineWorker:
    def __init__(self):
        self.parser_service = ParserService()
        self.speech_service = SpeechService()
        self.summary_service = SummaryService()

    async def run(self):
        print("Worker started")
        while True:
            try:
                await self.process_next_job()
            except Exception as e:
                print("Worker error:", e)
            await asyncio.sleep(5)

    async def process_next_job(self):
        async with AsyncSessionLocal() as db:
            request = await request_repository.get_next_pending_request(db)
            if not request:
                return
            print(f"Processing request {request.id}")
            request = await request_repository.update_request_status(db, request.id, RequestStatus.PROCESSING)
            lecture_id = request.lecture_id

            try:
                # 1 этап — parser
                await self.run_parser(db, lecture_id)
                # 2 этап — speech
                await self.run_speech(db, lecture_id)
                # 3 этап — summary
                await self.run_summary(db, lecture_id)
                request = await request_repository.update_request_status(db, request.id, RequestStatus.FINISHED)
            except Exception as e:
                print("Pipeline failed:", e)
                request = await request_repository.update_request_status(db, request.id, RequestStatus.FAILED)

    async def run_parser(self, db, lecture_id):
        print("Parser stage")
        await self.parser_service.parse_lecture(db, lecture_id)

    async def run_speech(self, db, lecture_id):
        print("Speech stage")
        # await self.speech.transcribe_lecture(db, lecture_id)

    async def run_summary(self, db, lecture_id):
        print("Summary stage")
        # await self.summary.generate_summary(db, lecture_id)


def test_get_slides_url(parser, lecture_url):

    slides_url = parser.get_slides_url(lecture_url)

    assert slides_url.startswith("https://bbb.ssau.ru:8443/presentation/")
    assert slides_url.endswith("svgs/slide")


def test_download_slides(parser, lecture_url):

    slides_path = parser.download_slides(lecture_url)

    assert slides_path.exists()
    assert any(slides_path.iterdir())


def test_download_audio(parser, lecture_url):

    audio_path = parser.download_audio(lecture_url)

    length = parser.get_length(str(audio_path))

    print(f"Длина видео: {length} секунд")

    assert audio_path.exists()
    assert audio_path.name == "lecture.mp3"

    assert isinstance(length, float)
    assert length > 0