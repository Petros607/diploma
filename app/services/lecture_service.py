# app/services/lecture_service.py
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import asyncio
from pathlib import Path

from fastapi.responses import FileResponse

from app.services.parser_service import ParserService
from app.core.status import RequestStatus
from app.database import AsyncSessionLocal
from app.repositories import lecture_repository, request_repository, summary_repository


class LectureService:

    def __init__(self):
        self.parser_service = ParserService()

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

    async def get_status(self, url_lecture: str, db: AsyncSession):
        """Возвращает текущий статус обработки лекции."""
        lecture = await lecture_repository.get_lecture_by_url(db, url_lecture)
        if not lecture:
            # если лекция не зарегистрирована, считаем, что ничего не обрабатывается
            return {"status": RequestStatus.PENDING}
        request = await request_repository.get_request_by_lecture_id(db, lecture.id)
        if not request:
            return {"status": RequestStatus.PENDING}
        return {"status": request.status}

    async def download_summary(self, url_lecture: str, db: AsyncSession):
        """Возвращает файл конспекта (PDF) для скачивания."""
        lecture = await lecture_repository.get_lecture_by_url(db, url_lecture)
        if not lecture:
            raise FileNotFoundError("Lecture not found")
        summary = await summary_repository.get_summary_by_lecture_id(db, lecture.id)
        if not summary or not summary.summary_path:
            raise FileNotFoundError("Summary not available")
        path = Path(summary.summary_path)
        if not path.exists():
            raise FileNotFoundError("File not found on disk")
        return FileResponse(path, media_type="application/pdf", filename="lecture.pdf")

