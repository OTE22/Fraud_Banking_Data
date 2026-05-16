import json
from app.core.logging import LOGGER


class KafkaProducer:
    def __init__(self, bootstrap_servers: str = "localhost:9092"):
        self.servers = bootstrap_servers
        self.connected = False

    async def connect(self) -> None:
        LOGGER.info("kafka_producer_connected", servers=self.servers)
        self.connected = True

    async def send(self, topic: str, key: str, value: dict) -> None:
        LOGGER.info("kafka_message_sent", topic=topic, key=key)


class KafkaConsumer:
    def __init__(self, bootstrap_servers: str = "localhost:9092", group_id: str = "fraud-group"):
        self.servers = bootstrap_servers
        self.group_id = group_id
        self.connected = False

    async def connect(self) -> None:
        LOGGER.info("kafka_consumer_connected", servers=self.servers, group=self.group_id)
        self.connected = True

    async def consume(self, topic: str, callback) -> None:
        LOGGER.info("kafka_consuming", topic=topic)
