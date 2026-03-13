# app/repositories/request_repository.py
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime

from app.models.request import Request
from app.core.status import RequestStatus


async def create_request(db: AsyncSession, lecture_id: int) -> Request:
    """Создание нового запроса на обработку"""
    request = Request(
        lecture_id=lecture_id,
        status=RequestStatus.PENDING,
        created_at=datetime.utcnow()
    )

    db.add(request)
    await db.commit()
    await db.refresh(request)

    return request


async def get_request(db: AsyncSession, request_id: int) -> Request | None:
    """Получение запроса по его ID"""
    result = await db.execute(
        select(Request).where(Request.id == request_id)
    )
    return result.scalar_one_or_none()


async def get_request_by_lecture_id(db: AsyncSession, lecture_id: int) -> Request | None:
    """Получение запроса для лекции по ID лекции"""
    result = await db.execute(
        select(Request)
        .where(Request.lecture_id == lecture_id)
        .order_by(Request.created_at.desc())
        .limit(1)
    )
    return result.scalar_one_or_none()


async def start_processing(db: AsyncSession, request_id: int):
    """Обновление статуса запроса на PROCESSING и установка времени начала обработки"""
    request = await get_request(db, request_id)
    if request:
        request.status = RequestStatus.PROCESSING
        request.started_at = datetime.utcnow()
        await db.commit()
        await db.refresh(request)
    return request


async def finish_request(db: AsyncSession, request_id: int):
    """Обновление статуса запроса на FINISHED и установка времени окончания обработки"""
    request = await get_request(db, request_id)
    if request:
        request.status = RequestStatus.FINISHED
        request.finished_at = datetime.utcnow()
        await db.commit()
        await db.refresh(request)
    return request


async def update_request_status(
    db: AsyncSession, 
    request_id: int, 
    status: RequestStatus
) -> Request | None:
    """Обновление статуса запроса"""
    request = await get_request(db, request_id)
    if request:
        request.status = status
        await db.commit()
        await db.refresh(request)
    return request


async def get_next_pending_request(db: AsyncSession) -> Request | None:
    """Получение следующего запроса в очереди на обработку со статусом PENDING."""
    request = await db.execute(
        select(Request)
        .where(Request.status == RequestStatus.PENDING)
        .order_by(Request.created_at.asc())
        .limit(1)
    )
    return request.scalar_one_or_none()
