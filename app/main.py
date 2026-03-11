# app/main.py
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi import Request
from app.routers import lecture_router

app = FastAPI(title="Капибара - Конспекты лекций")

# Подключаем статические файлы
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# Подключаем шаблоны
templates = Jinja2Templates(directory="app/templates")

# Подключаем роутеры
app.include_router(lecture_router.router)

@app.get("/")
async def root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})
