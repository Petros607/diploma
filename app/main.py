# app/main.py
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi import Request
import asyncio

from app.routers import lecture_router
from app.workers.pipeline_worker import PipelineWorker

app = FastAPI(title="Капибара - Конспекты лекций")

# Подключаем статические файлы
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# Подключаем шаблоны
templates = Jinja2Templates(directory="app/templates")

# Подключаем роутеры
app.include_router(lecture_router.router)

@app.on_event("startup")
async def start_background_worker():
    """Запускаем цикл обработки запросов в фоне одновременно с сервером."""
    # worker.run() содержит бесконечный цикл, запускаем как таск
    app.state.worker_task = asyncio.create_task(PipelineWorker().run())


@app.on_event("shutdown")
async def stop_background_worker():
    task = getattr(app.state, "worker_task", None)
    if task:
        task.cancel()
        try:
            await task
        except asyncio.CancelledError:
            pass


@app.get("/")
async def root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})
