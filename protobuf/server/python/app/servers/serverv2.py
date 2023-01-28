from app.logger import get_logger
from proto_files.v2 import healthcheck_pb2, healthcheck_pb2_grpc

logger = get_logger(__name__)


class HealthCheck(healthcheck_pb2_grpc.HealthServicer):
    def Check(self, request, context):
        logger.info("HealthCheck server received: " + request.service)
        return healthcheck_pb2.HealthCheckResponse(
            status=healthcheck_pb2.HealthCheckResponse.SERVING
        )


services = [
    {
        "service": HealthCheck,
        "handler": healthcheck_pb2_grpc.add_HealthServicer_to_server,
    },
]
