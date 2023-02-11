import os

from base_utils import get_logger
from fastapi import FastAPI

logger = get_logger(__name__)

app = FastAPI()


@app.get("/count_words")
async def count_words(text: str):
    from app.broker import broker
    from app.tasks import count_words

    # count_words.broker = broker
    # count_words.queue_name = os.getenv("QUEUE_NAME", "default")
    logger.debug(count_words.queue_name)
    result = count_words.send(text).get_result(block=True, timeout=1_000)
    broker.join(count_words.queue_name)
    logger.debug(dir(result))
    return {"count": result}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=os.getenv("PORT", 8000))
