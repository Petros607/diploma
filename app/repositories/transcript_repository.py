# app/repositories/transcript_repository.py
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.transcript import Transcript


async def create_transcript(
    db: AsyncSession,
    lecture_id: int,
    audio_path: str
) -> Transcript:

    transcript = Transcript(
        lecture_id=lecture_id,
        audio_path=audio_path
    )

    db.add(transcript)
    await db.commit()
    await db.refresh(transcript)

    return transcript


async def set_transcript_path(
    db: AsyncSession,
    transcript: Transcript,
    transcript_path: str
):

    transcript.transcript_path = transcript_path

    await db.commit()
