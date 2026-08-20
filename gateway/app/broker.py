from faststream.kafka.fastapi import KafkaRouter

from .config import settings

kafka_router = KafkaRouter(settings.kafka_host)
