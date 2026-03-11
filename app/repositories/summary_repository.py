# app/repositories/summary_repository.py
from sqlalchemy.ext.asyncio import AsyncSession
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
