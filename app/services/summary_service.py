# app/services/summary_service.py

from gigachat import GigaChat
from pathlib import Path

from app.config import settings


class SummaryService:

    def __init__(self):
        self.client = GigaChat(
            credentials=settings.gigachat_api_key,
            scope="GIGACHAT_API_PERS",
            # model="GigaChat",
            verify_ssl_certs=False
        )

    async def generate_annotation(self, summary_path: str) -> str:
        """Генерирует короткую аннотацию лекции по готовому конспекту"""
        text = self._read_file(summary_path)
        text = text[:8000]
        prompt = f"""
    Ты помощник студента.

    На основе конспекта лекции сделай очень короткую аннотацию.

    Требования:
    - 2–4 предложения
    - максимум 60 слов
    - описать тему лекции

    Конспект лекции:
    {text}
    """
        response = self.client.chat(prompt)
        return response.choices[0].message.content.strip()

    async def summarize_from_file(
        self,
        transcript_path: str,
        slide_timings: dict,
        output_path: str
    ) -> str:
        """
        Создание конспекта лекции по транскрипту и таймингам слайдов
        """
        text = self._read_file(transcript_path)
        segments = self._parse_transcript(text)
        grouped = self._group_by_slides(segments, slide_timings)
        result_sections = []
        for slide_number, texts in grouped.items():
            joined_text = " ".join(texts)
            summary = self._summarize_slide(slide_number, joined_text)
            slide_time = self._get_slide_time(slide_timings, slide_number)
            section = f"""
---Слайд {slide_number}
Тайминг: {slide_time} сек

{summary}
"""
            result_sections.append(section)
        final_summary = "\n".join(result_sections)
        self._save_file(output_path, final_summary)
        return output_path
    
    def _read_file(self, file_path: str) -> str:
        """Читает содержимое файла"""
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"Файл не найден: {file_path}")
        
        with open(path, 'r', encoding='utf-8') as file:
            return file.read()
        
    def _time_to_seconds(self, time_str: str) -> int:

        minutes, seconds = map(int, time_str.split(":"))
        return minutes * 60 + seconds
    
    def _parse_transcript(self, text: str):
        segments = []
        lines = text.split("\n")
        i = 0
        while i < len(lines) - 1:
            if " - " in lines[i]:
                start, end = lines[i].split(" - ")
                segment = {
                    "start": self._time_to_seconds(start),
                    "end": self._time_to_seconds(end),
                    "text": lines[i + 1]
                }
                segments.append(segment)
                i += 2
            else:
                i += 1
        return segments

    def _group_by_slides(self, segments, slide_timings):

        slide_starts = sorted(
            [(int(k), v) for k, v in slide_timings.items()],
            key=lambda x: x[0]
        )
        slide_text = {}
        for segment in segments:
            slide_number = None
            for start, slide in slide_starts:
                if segment["start"] >= start:
                    slide_number = slide
                else:
                    break
            if slide_number not in slide_text:
                slide_text[slide_number] = []
            slide_text[slide_number].append(segment["text"])
        return slide_text

    def _summarize_slide(self, slide_number, text):

        prompt = f"""
Ты помощник студента.

Сделай краткий конспект объяснения преподавателя для одного слайда лекции.

Слайд №{slide_number}

Текст лекции:
{text}

Сделай конспект:
- кратко
- по делу
"""
        response = self.client.chat(prompt)
        return response.choices[0].message.content.strip()

    def _get_slide_time(self, slide_timings, slide_number):
        for time, slide in slide_timings.items():
            if slide == slide_number:
                return time
        return "?"

    def _save_file(self, output_path, text):
        path = Path(output_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            f.write(text)
