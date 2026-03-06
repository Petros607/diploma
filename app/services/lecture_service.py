# app/schemas/lecture_service.py
from app.services.parser_service import ParserService

parser = ParserService()

def process_lecture(url: str):
    # Скачиваем все данные
    slides_url = parser.get_data(url)
    parser.download_image(slides_url)
    audio_path = parser.download_audio(slides_url)
    length = parser.get_length(audio_path)

    metadata = parser.get_metadata(url)
    return metadata
