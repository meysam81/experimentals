import grpc
from app.config import config
from app.logger import get_logger
from proto_files import greetings_pb2, greetings_pb2_grpc

logger = get_logger(__name__)


def run():
    # NOTE(gRPC Python Team): .close() is possible on a channel and should be
    # used in circumstances in which the with statement does not fit the needs
    # of the code.
    logger.info("Will try to greet world ...")

    server_addr = config.SERVER_ADDRESS

    with grpc.insecure_channel(server_addr) as channel:
        stub = greetings_pb2_grpc.GreeterStub(channel)
        response = stub.SayHello(greetings_pb2.HelloRequest(name=config.NAME))
    logger.info("Greeter client received: " + response.message)
