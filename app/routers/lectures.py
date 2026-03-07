# app/routers/lectures.py
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

import hashlib
import os

from app.database import get_db
from app.models.lecture import Lecture
from app.services.parser_service import ParserService
from app.models.request import Request


router = APIRouter(prefix="/lectures", tags=["Lectures"])


@router.get("/list")
async def get_list(
    url_room: str,
    db: AsyncSession = Depends(get_db)
):
    """
    Получить список записей лекций по комнате BBB
    """
    parser = ParserService()

    try:
        metadata = parser.get_metadata(url_room)
    except Exception:
        raise HTTPException(
            status_code=400,
            detail="Не удалось получить данные комнаты"
        )

    # {'lecture_0': {'name_teacher': 'Жданова Александра Николаевна', 'url': 'https://bbb.ssau.ru:8443/playback/presentation/2.3/bc140f637937d69f1ce2f7b836745e4c24131f16-1747630362721', 'name_subject': 'ИТ-практикум', 'datetime': 'May 19, 2025 08:52am', 'datetime_utc': '2025-05-19T04:52:42Z', 'length': '6 h 7 min', 'users_count': 117},
    #  'lecture_1': {'name_teacher': 'Жданова Александра Николаевна', 'url': 'https://bbb.ssau.ru:8443/playback/presentation/2.3/bc140f637937d69f1ce2f7b836745e4c24131f16-1739530683456', 'name_subject': 'ИТ-практикум', 'datetime': 'Feb 14, 2025 02:58pm', 'datetime_utc': '2025-02-14T10:58:03Z', 'length': '1 h 4 min', 'users_count': 28}}
    result = {}

    for key, lecture_data in metadata.items():
        lecture_url = lecture_data["url"]

        query = await db.execute(
            select(Lecture).where(Lecture.url == lecture_url)
        )
        print(query)

        lecture = query.scalar_one_or_none()
        status = "generate"
        path = None

        if lecture:
            req_query = await db.execute(
                select(Request).where(Request.lecture_id == lecture.id)
            )

            request = req_query.scalar_one_or_none()

            if request:

                if request.status == "finished":
                    status = "download"
                    path = f"/lectures/{lecture.id}"

                elif request.status in ["created", "started"]:
                    status = "processing"

        result[key] = {
            "name_teacher": lecture_data["name_teacher"],
            "name_subject": lecture_data["name_subject"],
            "datetime": lecture_data["datetime"],
            "url": lecture_url,
            "path": path,
            "status": status
        }
    return result

@router.get("/{lecture_id}")
async def get_lecture_summary(
    lecture_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    Сгенерировать конспект лекции
    """

    result = await db.execute(
        select(Lecture).where(Lecture.id == lecture_id)
    )

    lecture = result.scalar_one_or_none()

    if lecture is None:
        raise HTTPException(
            status_code=404,
            detail="Lecture not found"
        )

    try:

        # TODO: здесь будет вызов LLM
        content = "КОНСПЕКТ ЛЕКЦИИ"

        file_hash = hashlib.md5(lecture.url.encode()).hexdigest()
        file_path = f"/tmp/{file_hash}.txt"

        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)

        return FileResponse(
            path=file_path,
            filename="conspect.txt",
            media_type="text/plain"
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Ошибка генерации конспекта: {str(e)}"
        )
