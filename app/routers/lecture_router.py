# app/routers/lecture_router.py
from fastapi import APIRouter, Depends, Request, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.services.lecture_service import LectureService
from app.schemas.lecture import (
    LectureCreate,
    LectureGenerateResponse,
    LectureStatusResponse,
    RoomLecturesResponse,
)


router = APIRouter(prefix="/lectures", tags=["Lectures"])

lecture_service = LectureService()


@router.get("/list", response_model=RoomLecturesResponse)
async def get_list(
    url_room: str,
    db: AsyncSession = Depends(get_db)
):
    """Получить список записей лекций по комнате BBB"""
    try:
        lectures = await lecture_service.get_room_lectures(url_room, db)
        # FastAPI will coerce the dict to RoomLecturesResponse automatically
        return lectures
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Не удалось получить данные комнаты: {e}"
        )

@router.post("/generate", response_model=LectureGenerateResponse)
async def generate(
    lecture: LectureCreate,
    db: AsyncSession = Depends(get_db)
):
    """Пользователь начал пайплайн генерации конспекта"""
    try:
        return await lecture_service.generate_lecture(
            lecture.url,
            lecture.subject or "",
            lecture.teacher or "",
            lecture.datetime or "",
            db
        )
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Ошибка генерации: {e}"
        )

@router.get("/status", response_model=LectureStatusResponse)
async def get_status(
    url_lecture: str,
    db: AsyncSession = Depends(get_db)
):
    """Проверить статус генерации"""
    try:
        return await lecture_service.get_status(url_lecture, db)
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Не удалось получить статус: {e}"
        )
    
@router.get("/download")
async def download(
    url_lecture: str,
    db: AsyncSession = Depends(get_db)
):
    """Скачать конспект"""
    try:
        return await lecture_service.download_summary(url_lecture, db)
    except Exception:
        raise HTTPException(
            status_code=400,
            detail="Файл не найден"
        )
