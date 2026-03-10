# app/services/speech_service.py
"""Сервис транскрипции аудио через Yandex SpeechKit v3"""

import time
import requests
import boto3
from botocore.client import Config
from pathlib import Path
import json

from app.config import settings


class SpeechService:
    RECOGNIZE_URL = "https://stt.api.cloud.yandex.net/stt/v3/recognizeFileAsync"
    OPERATION_URL = "https://operation.api.cloud.yandex.net/operations"
    RESULT_URL = "https://stt.api.cloud.yandex.net/stt/v3/getRecognition"

    def __init__(self):
        self.bucket = settings.yandex_bucket
        self.s3 = boto3.client(
            "s3",
            endpoint_url="https://storage.yandexcloud.net",
            aws_access_key_id=settings.yandex_static_api_key,
            aws_secret_access_key=settings.yandex_static_secret_key,
            config=Config(signature_version="s3v4")
        )
        self.headers = {
            "Authorization": f"Api-Key {settings.yandex_api_key}",
            "x-folder-id": settings.yandex_folder_id
        }

    def upload_file(self, local_path: str, object_name: str | None = None):
        """Загрузка файла в Object Storage"""
        local_path = Path(local_path)
        if not object_name:
            object_name = Path(local_path).name
        self.s3.upload_file(str(local_path), self.bucket, object_name)
        uri = f"https://storage.yandexcloud.net/{self.bucket}/{object_name}"
        return uri
    
    def start_recognition(self, file_uri: str):
        """Запуск асинхронного распознавания"""
        payload = {
            "uri": file_uri,
            "recognition_model": {
                "model": "general",
                "audio_format": {
                    "container_audio": {
                        "container_audio_type": "WAV"
                    }
                }
            }
        }
        response = requests.post(
            self.RECOGNIZE_URL,
            headers=self.headers,
            json=payload
        )
        response.raise_for_status()
        operation_id = response.json()["id"]
        print("Operation ID:", operation_id)
        return operation_id
    
    def wait_operation(self, operation_id: str):
        """Ожидание завершения операции"""
        while True:
            response = requests.get(
                f"{self.OPERATION_URL}/{operation_id}",
                headers=self.headers
            )
            response.raise_for_status()
            data = response.json()
            if data.get("done"):
                print("Операция завершена")
                return
            print("Ожидание распознавания...")
            time.sleep(3)

    def parse_yandex_stt_response(self, response_text):
        """Парсинг ответа Yandex SpeechKit в формате NDJSON"""
        chunks = []
        
        for line_num, line in enumerate(response_text.strip().split('\n'), 1):
            if not line.strip():
                continue
                
            try:
                chunk = json.loads(line)
                chunks.append(chunk)
                
                # Выводим информацию о чанке
                print(f"\n--- Чанк {line_num} ---")
                print(json.dumps(chunk, indent=2, ensure_ascii=False))
                
                # Извлекаем текст, если есть
                if "result" in chunk:
                    result = chunk["result"]
                    if "final" in result:
                        alternatives = result["final"].get("alternatives", [])
                        if alternatives:
                            print(f"Текст: {alternatives[0].get('text', '')}")
                    elif "finalRefinement" in result:
                        refinement = result["finalRefinement"]
                        if "normalizedText" in refinement:
                            alt = refinement["normalizedText"].get("alternatives", [])
                            if alt:
                                print(f"Нормализованный текст: {alt[0].get('text', '')}")
                                
            except json.JSONDecodeError as e:
                print(f"Ошибка в чанке {line_num}: {e}")
                print(f"Проблемная строка: {line[:200]}...")
        
        return chunks

    def get_result(self, operation_id: str):
        """Получение результата распознавания"""
        response = requests.get(
            f"{self.RESULT_URL}?operation_id={operation_id}",
            headers=self.headers
        )
        response.raise_for_status()
        chunks = self.parse_yandex_stt_response(response.text)
    
        # Собираем все тексты
        full_text = ""
        for chunk in chunks:
            try:
                if "result" in chunk:
                    result = chunk["result"]
                    if "finalRefinement" in result:
                        alt = result["finalRefinement"]["normalizedText"]["alternatives"][0]
                        full_text += " " + alt["text"]
                    elif "final" in result:
                        alt = result["final"]["alternatives"][0]
                        full_text += " " + alt["text"]
            except (KeyError, IndexError):
                continue
        
        return full_text.strip()
    
    def transcribe(self, local_audio_path: str):
        """Полный пайплайн транскрипции"""
        uri = self.upload_file(local_audio_path)
        # uri = f"https://storage.yandexcloud.net/{self.bucket}/speech1.wav"
        operation_id = self.start_recognition(uri)
        self.wait_operation(operation_id)
        # operation_id = "f8dkofp338du4hst4ekc"
        text = self.get_result(operation_id)
        return text
