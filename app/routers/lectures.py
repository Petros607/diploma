from fastapi import APIRouter, Request, Query, HTTPException
from fastapi.responses import JSONResponse, FileResponse
import hashlib

router = APIRouter(tags=["Lectures"])

# Временные данные для демонстрации
SAMPLE_LECTURES = {
    "lection_0": {
        "id": None,
        "name_file": None,
        "name_teacher": "Грешняков Павел Иванович",
        "url": "https://bbb.ssau.ru:8443/playback/presentation/2.3/cf5215d4ed77ac8f39337081f34c2a49a413621d-1649044933105",
        "name_subject": "Робототехнические комплексы",
        "datetime": "Apr 04, 2022 4:02am",
        "lenght": None,
        "path": "что-то",
        "size": None
    },
    "lection_1": {
        "id": None,
        "name_file": None,
        "name_teacher": "Грешняков Павел Иванович",
        "url": "https://bbb.ssau.ru:8443/playback/presentation/2.3/cf5215d4ed77ac8f39337081f34c2a49a413621d-1645415216551",
        "name_subject": "Робототехнические комплексы",
        "datetime": "Feb 21, 2022 3:46am",
        "lenght": None,
        "path": None,
        "size": None
    },
    "lection_2": {
        "id": None,
        "name_file": None,
        "name_teacher": "Грешняков Павел Иванович",
        "url": "https://bbb.ssau.ru:8443/playback/presentation/2.3/cf5215d4ed77ac8f39337081f34c2a49a413621d-1636948468965",
        "name_subject": "Робототехнические комплексы",
        "datetime": "Nov 15, 2021 3:54am",
        "lenght": None,
        "path": None,
        "size": None
    }
}

@router.get("/get_list")
async def get_lecture_list(url_room: str = Query(..., description="URL комнаты")):
    """
    Получает список лекций по URL комнаты
    """
    # TODO: Здесь будет реальная логика парсинга BBB
    # Пока возвращаем тестовые данные
    return JSONResponse(content=SAMPLE_LECTURES)

@router.get("/get_lecture")
async def get_lecture(url_lecture: str = Query(..., description="URL лекции")):
    """
    Генерирует и возвращает конспект лекции
    """
    try:
        # TODO: Здесь будет реальная логика генерации конспекта
        # Пока создаем тестовый файл
        content = f"""КОНСПЕКТ ЛЕКЦИИ"""
        file_path = hashlib.md5(url_lecture.encode()).hexdigest()
        with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
        
        # return FileResponse(
        #     path=file_path,
        #     filename=f"conspect_{file_hash}.pdf",
        #     media_type="application/pdf"
        # )
        return FileResponse(
            path=file_path,
            filename=f"conspect.txt",
            media_type="text/plain; charset=utf-8"
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка генерации конспекта: {str(e)}")
