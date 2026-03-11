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
                await self.run_parser(db, lecture)
                # 2 этап — speech
                await self.run_speech(db, lecture)
                # # 3 этап — summary
                # await self.run_summary(db, lecture_id)
                request = await request_repository.finish_request(db, request.id)
            except Exception as e:
                print("Pipeline failed:", e)
                request = await request_repository.update_request_status(db, request.id, RequestStatus.FAILED)

    async def run_parser(self, db, lecture):
        print("Parser stage")
        presentation_dir = await self.parser_service.download_slides(lecture.url, lecture.id)
        slides_timings = {i*i: i for i in range(1, len(list(presentation_dir.glob("slide*.svg"))) + 1)}
        audio_path = await self.parser_service.download_audio(lecture.url, lecture.id)
        await presentation_repository.create_presentation(db=db, lecture_id=lecture.id, slides_timings=slides_timings, presentation_path=str(presentation_dir))
        await transcript_repository.create_transcript(db=db, lecture_id=lecture.id, audio_path=str(audio_path))

    async def run_speech(self, db, lecture):
        print("Speech stage")
        # await self.speech.transcribe_lecture(db, lecture_id)

    async def run_summary(self, db, lecture_id):
        print("Summary stage")
        # await self.summary.generate_summary(db, lecture_id)
