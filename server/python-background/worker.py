from random import random

from celery import Celery
from config import config

worker = Celery("tasks", broker=config.BROKER)


@worker.task(name="dummy")
def long_running_task():
    # time.sleep(10)
    if random() < 0.5:
        raise Exception("Something went wrong")
    print("Done!")
