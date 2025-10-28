import pytest
import asyncio


class AsyncObject:
    async def initialize(self):
        await asyncio.sleep(0.1)  # имитация асинхронной инициализации
        self.data = "ready"


@pytest.fixture(scope="class")
def async_object():
    obj = AsyncObject()
    asyncio.run(obj.initialize())
    return obj


@pytest.mark.asyncio
class TestAsync:
    async def test_one(self, async_object):
        assert async_object.data == "ready"

    async def test_two(self, async_object):
        assert async_object.data != "not ready"
