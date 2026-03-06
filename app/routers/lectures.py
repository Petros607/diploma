# app/routers/lectures.py
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

import hashlib
import os

from app.database import get_db
from app.models.lecture import Lecture

router = APIRouter(prefix="/lectures", tags=["Lectures"])


@router.get("/")
async def get_lecture_list(
    db: AsyncSession = Depends(get_db)
):
    """
    Получить список лекций
    """

    result = await db.execute(select(Lecture))
    lectures = result.scalars().all()

    return lectures


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
