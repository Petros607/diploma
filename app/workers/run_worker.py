# app/workers/run_worker.py
import asyncio
from app.workers.pipeline_worker import PipelineWorker


async def main():
    worker = PipelineWorker()
    await worker.run()


if __name__ == "__main__":
    asyncio.run(main())
