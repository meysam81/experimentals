from concurrent import futures

import grpc
from app.config import config
from app.logger import get_logger
from proto_files import greetings_pb2, greetings_pb2_grpc

logger = get_logger(__name__)


class Greeter(greetings_pb2_grpc.GreeterServicer):
    def SayHello(self, request, context):
        logger.info("Greeter server received: " + request.name)
        return greetings_pb2.HelloReply(message="Hello %s" % request.name)


def serve(interceptors=None):
    port = config.PORT
    server = grpc.server(
        futures.ThreadPoolExecutor(max_workers=config.THREAD_POOL),
        interceptors=interceptors,
    )
    greetings_pb2_grpc.add_GreeterServicer_to_server(Greeter(), server)

    server.add_insecure_port("[::]:" + port)
    logger.info("Starting server ...")
    server.start()

    logger.info("Server started, listening on " + port)
    server.wait_for_termination()
