from concurrent import futures

import grpc
from app.config import config
from base_utils import get_logger

logger = get_logger(__name__)


def serve(services: dict = None, interceptors=None):
    if not services:
        logger.critical("No servers to serve")
        return

    port = config.PORT
    server = grpc.server(
        futures.ThreadPoolExecutor(max_workers=config.THREAD_POOL),
        interceptors=interceptors,
        options=(("grpc.enable_http_proxy", 0),),
    )
    for service_meta in services:
        handler = service_meta["handler"]
        service = service_meta["service"]
        handler(service(), server)

    server.add_insecure_port("[::]:" + port)
    logger.info("Starting server ...")
    server.start()

    logger.info("Server started, listening on " + port)
    server.wait_for_termination()
