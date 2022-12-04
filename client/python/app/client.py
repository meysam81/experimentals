import grpc
from app.config import config
from app.logger import get_logger
from proto_files import greetings_pb2, greetings_pb2_grpc

logger = get_logger(__name__)


def do_run(channel, name):
    logger.info(f"Will try to greet {name} ...")
    response = channel.SayHello(greetings_pb2.HelloRequest(name=name))
    logger.info("Greeter client received: " + response.message)


def run(infinite=None):

    server_addr = config.SERVER_ADDRESS

    channel = grpc.insecure_channel(server_addr)
    stub = greetings_pb2_grpc.GreeterStub(channel)
    if infinite:
        counter = 0
        while True:
            try:
                do_run(stub, f"{config.NAME}-{counter}")
                counter += 1
            except KeyboardInterrupt:
                logger.info("Stopping client ...")
                break
            except Exception as e:
                logger.error(f"Error: {e}")
                logger.info("reconnecting...")
                # try to reconnect, maybe a deadline has exceeded
                stub = greetings_pb2_grpc.GreeterStub(channel)
    else:
        do_run(stub, config.NAME)

    logger.info("Done.")
    channel.close()
