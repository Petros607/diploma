# app/services/lecture_service.py
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import asyncio

from app.services.parser_service import ParserService
from app.services.speech_service import SpeechService
from app.services.summary_service import SummaryService
from app.models.lecture import Lecture
from app.models.request import Request
from app.core.status import RequestStatus
from app.database import AsyncSessionLocal
from app.repositories import lecture_repository, request_repository


class LectureService:

    def __init__(self):
        self.parser_service = ParserService()
        self.speech_service = SpeechService()
        self.summary_service = SummaryService()

    async def get_room_lectures(self, url_room: str, db: AsyncSession):
        """Получение списка лекций для комнаты"""
        metadata = self.parser_service.get_room_metadata(url_room)
        result = {}
        for key, lecture_data in metadata.items():
            lecture_url = lecture_data["url"]
            lecture = await lecture_repository.get_lecture_by_url(db, lecture_url)
            status = RequestStatus.PENDING

            if lecture:
                request = await request_repository.get_request_by_lecture_id(db, lecture.id)
                status = request.status if request else RequestStatus.PENDING

            result[key] = {
                "name_teacher": lecture_data["name_teacher"],
                "name_subject": lecture_data["name_subject"],
                "datetime": lecture_data["datetime"],
                "url": lecture_url,
                "length": lecture_data["length"],
                "users_count": lecture_data["users_count"],
                "status": status
            }

        return result
    
    async def generate_lecture(self, url_lecture: str, subject: str, teacher: str, datetime: str, db: AsyncSession):
        """Обработка запроса на генерацию лекции"""
        lecture = await lecture_repository.get_lecture_by_url(db, url_lecture)

        if not lecture:
            lecture = await lecture_repository.create_lecture(db, url_lecture, subject, teacher, datetime)

        request = await request_repository.create_request(db, lecture_id=lecture.id)

        return {
            "status": RequestStatus.PENDING,
            "lecture_id": lecture.id,
            "request_id": request.id
        }

