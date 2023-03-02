import pymongo
from app.otel import PymongoInstrumentor
from app.settings import settings

PymongoInstrumentor().instrument()
db = pymongo.MongoClient(settings.MONGO_CONNECTION_URI)[settings.MONGO_DATABASE_NAME]
