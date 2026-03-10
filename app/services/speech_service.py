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
    
    def get_filelist(self) -> list[dict]:
        """Получение списка файлой в Object Storage"""
        response = self.s3.list_objects_v2(
            Bucket=self.bucket
        )
        files = []
        for obj in response['Contents']:
            files.append({
                'name': obj['Key'],
                'size': obj['Size'],
                'last_modified': obj['LastModified']
            })
        return files
    
    def delete_file(self, filename: str) -> bool:
        """Удаление файла из Object Storage"""
        try:
            self.s3.delete_object(
                Bucket=self.bucket,
                Key=filename
            )
            return True
        except Exception as e:
            print(f"Ошибка при удалении файла {filename}: {e}") #TODO: logger
            return False
    
    def start_recognition(self, file_uri: str):
        """Запуск асинхронного распознавания"""
        payload = {
            "uri": file_uri,
            "recognition_model": {
                "model": "general",
                "audioFormat": {
                    "containerAudio": {
                        "containerAudioType": "MP3"
                    }
                },
                "languageRestriction": {
                    "restrictionType": "WHITELIST",
                    "languageCode": ["ru-RU"]
                },
                "textNormalization": {
                    "textNormalization": "TEXT_NORMALIZATION_DISABLED"
                }
            },
            "speakerLabeling": {
                "speakerLabeling": "SPEAKER_LABELING_DISABLED"
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
            time.sleep(10)

    def get_result(self, operation_id: str):
        """Получение результата распознавания"""
        response = requests.get(
            f"{self.RESULT_URL}?operation_id={operation_id}",
            headers=self.headers
        )
        response.raise_for_status()
        return response.text
    
    def ms_to_time(self, ms: int) -> str:
        seconds = ms // 1000
        minutes = seconds // 60
        seconds = seconds % 60
        return f"{minutes:02d}:{seconds:02d}"
    
    def parse_result(self, raw_result: str) -> str:
        """Преобразование ответа SpeechKit в читаемый текст"""
        lines = raw_result.strip().split("\n")
        segments = []
        seen = set()
        for line in lines:
            data = json.loads(line)
            result = data.get("result", {})
            if "final" not in result:
                continue

            alt = result["final"]["alternatives"][0]
            start = int(alt["startTimeMs"])
            end = int(alt["endTimeMs"])
            text = alt["text"]

            key = (start, end)
            if key in seen:
                continue
            seen.add(key)

            segments.append((start, end, text))
        formatted = []

        for start, end, text in segments:
            formatted.append(
                f"{self.ms_to_time(start)} - {self.ms_to_time(end)}\n{text}"
            )
        return "\n".join(formatted)
    
    def transcribe(self, local_audio_path: str):
        """Полный пайплайн транскрипции"""
        uri = self.upload_file(local_audio_path)
        operation_id = self.start_recognition(uri)
        self.wait_operation(operation_id)
        text = self.get_result(operation_id)
        formatted = self.parse_result(text)
        return formatted
