from meysam_utils import BaseSettings, LogLevel, root_validator


class Config(BaseSettings):
    LOG_LEVEL: LogLevel = LogLevel.INFO
    PORT: str = "50051"
    THREAD_POOL: int = 10
    SERVER_HOST: str = "localhost"
    PROMETHEUS_ENABLED: bool = True
    METRICS_PORT: int | None

    CELERY_BROKER: str = "confluentkafka://localhost:9092"
    CELERY_BACKEND: str
    CELERY_TASK_SERIALIZER: str = "json"
    CELERY_RESULT_SERIALIZER: str = "json"
    CELERY_TASK_RESULT_EXPIRES: int = 3600
    CELERY_CONFLUENT_SASL_USERNAME: str | None
    CELERY_CONFLUENT_SASL_PASSWORD: str | None
    CELERY_CONFLUENT_SASL_MECHANISM: str | None
    CELERY_CONFLUENT_SECURITY_PROTOCOL: str = "plaintext"
    CELERY_TOPIC_METADATA_REFRESH_INTERVAL_MS: int = 30_000
    CELERY_SOCKET_TIMEOUT_MS: int = 3_000
    CELERY_MESSAGE_TIMEOUT_MS: int = 3_000

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

    @root_validator
    def validate_settings(cls, values):
        super().validate_settings(values)

        if not values["METRICS_PORT"]:
            # get the last two digits of port and append it to 400
            values["METRICS_PORT"] = int("400" + values["PORT"][-2:])

        return values


config = Config()
