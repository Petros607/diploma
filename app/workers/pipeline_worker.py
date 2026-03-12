# app/workers/pipeline_worker.py
import asyncio
import pathlib
from sqlalchemy import select

from app.database import AsyncSessionLocal
from app.models.request import Request
from app.models.lecture import Lecture
from app.core.status import RequestStatus
from app.repositories import *
from app.services.parser_service import ParserService
from app.services.speech_service import SpeechService
from app.services.summary_service import SummaryService


class PipelineWorker:
    PATH_FILES = pathlib.Path("./data/")

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
            request = await request_repository.start_processing(db, request.id)
            lecture = await lecture_repository.get_lecture(db, request.lecture_id)

            try:
                # Создание в папке PATH_FILES папки с названием lecture_id
                lecture_path = self.PATH_FILES / str(lecture.id)
                lecture_path.mkdir(parents=True, exist_ok=True)
                # 1 этап — parser
                transcript = await self.run_parser(db, lecture)
                # 2 этап — speech
                path_to_transcript = await self.run_speech(db, lecture, transcript)
                # # 3 этап — summary
                # await self.run_summary(db, lecture.id, path_to_transcript)
                # request = await request_repository.finish_request(db, request.id)
            except Exception as e:
                print("Pipeline failed:", e)
                request = await request_repository.update_request_status(db, request.id, RequestStatus.FAILED)

    async def run_parser(self, db, lecture):
        print("Parser stage")
        presentation_dir = await self.parser_service.download_slides(lecture.url, lecture.id)
        slides_timings = {i*i: i for i in range(1, len(list(presentation_dir.glob("slide*.svg"))) + 1)}
        audio_path = await self.parser_service.download_audio(lecture.url, lecture.id)
        await presentation_repository.create_presentation(db=db, lecture_id=lecture.id, slides_timings=slides_timings, presentation_path=str(presentation_dir))
        transcript = await transcript_repository.create_transcript(db=db, lecture_id=lecture.id, audio_path=str(audio_path))
        return transcript

    async def run_speech(self, db, lecture, transcript): #f8d85mv08tn9loc01cnt
        print("Speech stage")

        uri = await self.speech_service.upload_file(transcript.audio_path)
        operation_id = await self.speech_service.start_recognition(uri)
        transcript = await transcript_repository.set_transcript_path(db=db, transcript=transcript, transcript_path=operation_id)
        await self.speech_service.wait_operation(operation_id)
        text = await self.speech_service.get_result(operation_id)
        formatted = await self.speech_service.parse_result(text)
        transcript_file = self.PATH_FILES / str(lecture.id) / "transcript.txt"
        saved_path = await self.speech_service.save_to_file(formatted, transcript_file)
        transcript = await transcript_repository.set_transcript_path(db=db, transcript=transcript, transcript_path=saved_path)
        return saved_path

    async def run_summary(self, db, lecture_id, path_to_transcript):
        print("Summary stage")
        annotation = "Аннотация к лекции" #TODO: доделать пайплайн, чтобы получать аннотацию к лекции и конспект
        # saved_path = await self.summary_service.summarize_from_file(path_to_transcript)
        # await summary_repository.create_summary(db=db, lecture_id=lecture_id, annotation=annotation, summary_path=str(path_to_transcript))
