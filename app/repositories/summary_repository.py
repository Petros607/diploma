# app/repositories/summary_repository.py
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.summary import Summary


async def create_summary(
    db: AsyncSession,
    lecture_id: int,
    annotation: str,
    summary_path: str
) -> Summary:

    summary = Summary(
        lecture_id=lecture_id,
        annotation=annotation,
        summary_path=summary_path
    )

    db.add(summary)
    await db.commit()
    await db.refresh(summary)

    return summary

async def get_summary_by_lecture_id(db: AsyncSession, lecture_id: int) -> Summary | None:
    """Получение конспекта лекции по ID лекции"""
    result = await db.execute(
        select(Summary)
        .where(Summary.lecture_id == lecture_id)
    )
    return result.scalar_one_or_none()

async def set_summary_path(
    db: AsyncSession,
    summary: Summary,
    summary_path: str
) -> Summary:
    if summary:
        summary.summary_path = summary_path
        await db.commit()
        await db.refresh(summary)
    return summary
