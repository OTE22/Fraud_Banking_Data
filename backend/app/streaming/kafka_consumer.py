class FakeConsumer:
    def __init__(self, topics: list[str]):
        self.topics = topics

    async def poll(self) -> list[dict]:
        return []
