# app/services/summary_service.py

from botocore import response
from gigachat import GigaChat
from pathlib import Path

from app.config import settings


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

    def summarize_from_file(self, file_path: str) -> str:
        """
        Читает текст из файла и создает его краткий конспект
        
        Args:
            file_path: путь к файлу с текстом
            
        Returns:
            str: конспект текста
        """
        # Читаем текст из файла
        text = self._read_file(file_path)
        
        # Создаем конспект
        return self._summarize_text(text)
    
    def _read_file(self, file_path: str) -> str:
        """
        Читает содержимое файла
        
        Args:
            file_path: путь к файлу
            
        Returns:
            str: содержимое файла
        """
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"Файл не найден: {file_path}")
        
        with open(path, 'r', encoding='utf-8') as file:
            return file.read()
    
    def _summarize_text(self, text: str) -> str:
        """
        Создает конспект переданного текста
        
        Args:
            text: текст для конспектирования
            
        Returns:
            str: конспект текста
        """
        prompt = f"""
Сделай краткий конспект текста.

Текст:
{text}
"""
        # response = self.client.chat(
        #     messages=[
        #         {
        #             "role": "user",
        #             "content": prompt
        #         }
        #     ]
        # )

        response = self.client.chat(prompt)

        return response.choices[0].message.content.strip()
