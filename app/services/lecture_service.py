# app/services/lecture_service.py
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.services.parser_service import ParserService
from app.models.lecture import Lecture
from app.models.request import Request


class LectureService:

    def __init__(self):
        self.parser = ParserService()

    async def get_room_lectures(self, url_room: str, db: AsyncSession):

        metadata = self.parser.get_metadata(url_room)

        result = {}

        for key, lecture_data in metadata.items():

            lecture_url = lecture_data["url"]

            query = await db.execute(
                select(Lecture).where(Lecture.url == lecture_url)
            )

            lecture = query.scalar_one_or_none()

            status = "generate"

            if lecture:

                req_query = await db.execute(
                    select(Request).where(Request.lecture_id == lecture.id)
                )

                request = req_query.scalar_one_or_none()

                if request:

                    if request.status == "finished":
                        status = "download"

                    elif request.status in ["created", "started"]:
                        status = "processing"

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
