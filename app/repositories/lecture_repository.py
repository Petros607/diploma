# app/repositories/lecture_repository.py
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.lecture import Lecture


async def create_lecture(db: AsyncSession, url: str, subject: str = "", teacher: str = "", datetime: str = "") -> Lecture:
    lecture = Lecture(url=url, subject=subject, teacher=teacher, datetime=datetime)

    db.add(lecture)
    await db.commit()
    await db.refresh(lecture)

    return lecture


async def get_lecture(db: AsyncSession, lecture_id: int) -> Lecture | None:
    result = await db.execute(
        select(Lecture).where(Lecture.id == lecture_id)
    )
    return result.scalar_one_or_none()


async def get_lecture_by_url(db: AsyncSession, url: str) -> Lecture | None:
    result = await db.execute(
        select(Lecture).where(Lecture.url == url)
    )
    return result.scalar_one_or_none()


async def update_lecture_info(
    db: AsyncSession,
    lecture: Lecture,
    subject: str,
    teacher: str,
    datetime: str
) -> Lecture:

    lecture.subject = subject
    lecture.teacher = teacher
    lecture.datetime = datetime

    await db.commit()
    await db.refresh(lecture)

    return lecture
