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

@router.post("/generate")
async def generate(
    url_lecture: str,
    db: AsyncSession = Depends(get_db)
):
    """
    Пользователь начал пайплайн генерации конспекта
    """

    try:
        return await lecture_service.generate_lecture(url_lecture, db)

    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Ошибка генерации: {str(e)}"
        )

@router.get("/status")
async def get_status(
    url_lecture: str,
    db: AsyncSession = Depends(get_db)
):
    """
    Проверить статус генерации
    """

    try:
        return await lecture_service.get_status(url_lecture, db)

    except Exception:
        raise HTTPException(
            status_code=400,
            detail="Не удалось получить статус"
        )
    
@router.get("/download")
async def download(
    url_lecture: str,
    db: AsyncSession = Depends(get_db)
):
    """
    Скачать конспект
    """

    try:
        return await lecture_service.download_summary(url_lecture, db)

    except Exception:
        raise HTTPException(
            status_code=400,
            detail="Файл не найден"
        )
