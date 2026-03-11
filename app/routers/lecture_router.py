# app/routers/lecture_router.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.services.lecture_service import LectureService


router = APIRouter(prefix="/lectures", tags=["Lectures"])

lecture_service = LectureService()


@router.get("/list")
async def get_list(
    url_room: str,
    db: AsyncSession = Depends(get_db)
):
    """
    Получить список записей лекций по комнате BBB
    """

    try:
        return await lecture_service.get_room_lectures(url_room, db)

    except Exception:
        raise HTTPException(
            status_code=400,
            detail="Не удалось получить данные комнаты"
        )
