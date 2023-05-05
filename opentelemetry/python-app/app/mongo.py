import pymongo
from app.settings import settings

db = pymongo.MongoClient(settings.MONGO_CONNECTION_URI)[settings.MONGO_DATABASE_NAME]
