from concurrent import futures

import grpc
from app.config import config
from app.logger import get_logger
from proto_files import (
    data_store_pb2,
    data_store_pb2_grpc,
    greetings_pb2,
    greetings_pb2_grpc,
)

logger = get_logger(__name__)


class Greeter(greetings_pb2_grpc.GreeterServicer):
    def SayHello(self, request, context):
        logger.info("Greeter server received: " + request.name)
        try:
            from app.tasks import app as celery_app

            celery_app.send_task("greet", args=[request.name])
        except Exception as e:
            logger.error(e)
        return greetings_pb2.HelloReply(message="Hello %s" % request.name)


class DataStore(data_store_pb2_grpc.DataStoreServicer):
    data_store = {}

    def Save(self, request, context):
        logger.info("DataStore server received: " + request.key)
        self.data_store[request.key] = request.value
        return data_store_pb2.SaveReply(key=request.key, value=request.value)

    def Load(self, request, context):
        logger.info("DataStore server received: " + request.key)
        value = self.data_store.get(request.key, "Not found")
        return data_store_pb2.LoadReply(value=value)


def serve(interceptors=None):
    port = config.PORT
    server = grpc.server(
        futures.ThreadPoolExecutor(max_workers=config.THREAD_POOL),
        interceptors=interceptors,
        options=(("grpc.enable_http_proxy", 0),),
    )
    greetings_pb2_grpc.add_GreeterServicer_to_server(Greeter(), server)
    data_store_pb2_grpc.add_DataStoreServicer_to_server(DataStore(), server)

    server.add_insecure_port("[::]:" + port)
    logger.info("Starting server ...")
    server.start()

    logger.info("Server started, listening on " + port)
    server.wait_for_termination()
