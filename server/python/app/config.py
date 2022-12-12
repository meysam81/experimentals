import os
from dataclasses import dataclass


@dataclass
class Config:
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    PORT: str = os.getenv("PORT", "50051")
    THREAD_POOL: int = os.getenv("THREAD_POOL", 10)
    SERVER_HOST: str = os.getenv("SERVER_HOST", "localhost")
    PROMETHEUS_ENABLED: bool = os.getenv("PROMETHEUS_ENABLED", "true").lower() == "true"
    METRICS_PORT: int = int(os.getenv("METRICS_PORT", f"400{PORT[-2:]}"))

    CELERY_BROKER: str = os.getenv("CELERY_BROKER", "confluentkafka://localhost:9092")
    CELERY_BACKEND: str = os.getenv("CELERY_BACKEND")
    CELERY_TASK_SERIALIZER: str = os.getenv("CELERY_TASK_SERIALIZER", "json")
    CELERY_RESULT_SERIALIZER: str = os.getenv("CELERY_RESULT_SERIALIZER", "json")
    CELERY_TASK_RESULT_EXPIRES: int = int(os.getenv("CELERY_TASK_RESULT_EXPIRES", 3600))
    CELERY_CONFLUENT_SASL_USERNAME: str = os.getenv("CELERY_CONFLUENT_SASL_USERNAME")
    CELERY_CONFLUENT_SASL_PASSWORD: str = os.getenv("CELERY_CONFLUENT_SASL_PASSWORD")
    CELERY_CONFLUENT_SASL_MECHANISM: str = os.getenv("CELERY_CONFLUENT_SASL_MECHANISM")
    CELERY_CONFLUENT_SECURITY_PROTOCOL: str = os.getenv(
        "CELERY_CONFLUENT_SECURITY_PROTOCOL", "plaintext"
    )
    CELERY_TOPIC_METADATA_REFRESH_INTERVAL_MS: int = int(
        os.getenv("CELERY_TOPIC_METADATA_REFRESH_INTERVAL_MS", 30_000)
    )
    CELERY_SOCKET_TIMEOUT_MS: int = int(os.getenv("CELERY_SOCKET_TIMEOUT_MS", 3_000))
    CELERY_MESSAGE_TIMEOUT_MS: int = int(os.getenv("CELERY_MESSAGE_TIMEOUT_MS", 3_000))

    # ref: https://github.com/edenhill/librdkafka/blob/v1.9.2/CONFIGURATION.md
    @property
    def broker_transport_options(self):
        bootstrap_server = self.CELERY_BROKER.replace("confluentkafka://", "")
        security_protocol = self.CELERY_CONFLUENT_SECURITY_PROTOCOL
        sasl_mechanism = self.CELERY_CONFLUENT_SASL_MECHANISM
        refresh_interval = self.CELERY_TOPIC_METADATA_REFRESH_INTERVAL_MS

        common = {
            "topic.metadata.refresh.interval.ms": refresh_interval,
            "bootstrap.servers": bootstrap_server,
            "security.protocol": security_protocol,
            "retries": 3,
            "socket.timeout.ms": self.CELERY_SOCKET_TIMEOUT_MS,
        }

        if sasl_mechanism:
            common["sasl.mechanisms"] = sasl_mechanism
            if not (
                self.CELERY_CONFLUENT_SASL_USERNAME
                and self.CELERY_CONFLUENT_SASL_PASSWORD
            ):
                raise ValueError(
                    "SASL mechanism requires username and password to be set"
                )
            common["sasl.username"] = self.CELERY_CONFLUENT_SASL_USERNAME
            common["sasl.password"] = self.CELERY_CONFLUENT_SASL_PASSWORD

        return {
            "security_protocol": security_protocol,
            "kafka_common_config": common,
            "kafka_producer_config": {
                "message.timeout.ms": self.CELERY_MESSAGE_TIMEOUT_MS,
            },
            "kafka_consumer_config": {
                "allow.auto.create.topics": True,
                "auto.offset.reset": "earliest",
            },
        }


config = Config()
