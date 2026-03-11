# app/repositories/presentation_repository.py
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.presentation import Presentation


async def create_presentation(
    db: AsyncSession,
    lecture_id: int,
    slides_timings: dict,
    presentation_path: str
) -> Presentation:

    presentation = Presentation(
        lecture_id=lecture_id,
        slides_timings=slides_timings,
        presentation_path=presentation_path
    )

    db.add(presentation)
    await db.commit()
    await db.refresh(presentation)

    return presentation
