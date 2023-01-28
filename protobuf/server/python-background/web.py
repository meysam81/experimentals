from celery import Celery
from config import config
from fastapi import BackgroundTasks, FastAPI

app = FastAPI()
worker = Celery("tasks", broker=config.BROKER)


@app.get("/")
async def root(background_tasks: BackgroundTasks):
    # background_tasks.add_task(long_running_task)
    worker.send_task("dummy")

    return {"message": "Hello World"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=10000)
