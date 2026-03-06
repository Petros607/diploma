import pathlib
from app.services.parser_service import ParserService

TEST_URL = "https://bbb.ssau.ru:8443/playback/presentation/2.3/aa788c4e3599195fe1a7a12ad585903f44c6f9ed-1739185560849"

# @pytest.mark.asyncio
def test_parser_download():
    parser = ParserService()
    
    # Получаем URL слайда
    slides_url = parser.get_data(TEST_URL)
    assert slides_url.startswith("https://bbb.ssau.ru:8443/presentation/")
    
    # Скачиваем слайды
    slides_path = parser.download_image(slides_url)
    assert slides_path.exists() and any(slides_path.iterdir()), "Слайды не скачались"
    
    # Скачиваем аудио
    audio_path = parser.download_audio(slides_url)
    assert audio_path.exists(), "Аудио не скачалось"
    
    # Получаем длительность аудио
    length = parser.get_length(audio_path)
    assert length > 0, "Неверная длительность аудио"
    
    # Получаем метаданные
    # metadata = parser.get_metadata(TEST_URL)
    # assert isinstance(metadata, dict) and len(metadata) > 0, "Метаданные пустые"
