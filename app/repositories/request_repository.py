# app/repositories/request_repository.py
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime

from app.models.request import Request


async def create_request(db: AsyncSession, lecture_id: int) -> Request:

    request = Request(
        lecture_id=lecture_id,
        status="pending",
        created_at=datetime.utcnow()
    )

    db.add(request)
    await db.commit()
    await db.refresh(request)

    return request


async def get_request(db: AsyncSession, request_id: int) -> Request | None:
    result = await db.execute(
        select(Request).where(Request.id == request_id)
    )
    return result.scalar_one_or_none()


async def start_processing(db: AsyncSession, request: Request):

    request.status = "processing"
    request.started_at = datetime.utcnow()

    await db.commit()


async def finish_request(db: AsyncSession, request: Request):

    request.status = "finished"
    request.finished_at = datetime.utcnow()

    await db.commit()
