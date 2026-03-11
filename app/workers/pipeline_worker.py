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
        self.parser = ParserService()
        self.speech = SpeechService()
        self.summary = SummaryService()

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
        await self.parser.process_lecture(lecture_id, db)

    async def run_speech(self, db, lecture_id):
        print("Speech stage")
        await self.speech.transcribe_lecture(lecture_id, db)

    async def run_summary(self, db, lecture_id):
        print("Summary stage")
        await self.summary.generate_summary(lecture_id, db)
