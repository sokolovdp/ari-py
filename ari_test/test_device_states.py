import httpx
import pytest
import respx

from ari.models import DeviceState
from ari.repositories.device_states import DeviceStateRepository

BASE = "http://ari.py/ari"


@pytest.fixture
async def repo():
    async with httpx.AsyncClient(base_url=BASE) as http:
        yield DeviceStateRepository(http, client=None)


async def test_list(repo):
    with respx.mock:
        respx.get(f"{BASE}/deviceStates").mock(
            return_value=httpx.Response(
                200, json=[{"name": "dev1", "state": "NOT_INUSE"}]
            )
        )
        result = await repo.list()
    assert len(result) == 1
    assert isinstance(result[0], DeviceState)


async def test_get(repo):
    with respx.mock:
        respx.get(f"{BASE}/deviceStates/dev1").mock(
            return_value=httpx.Response(200, json={"name": "dev1", "state": "BUSY"})
        )
        ds = await repo.get("dev1")
    assert ds.state == "BUSY"


async def test_update(repo):
    with respx.mock:
        respx.put(f"{BASE}/deviceStates/foobar").mock(
            return_value=httpx.Response(200, json={"name": "foobar", "state": "BUSY"})
        )
        ds = await repo.update("foobar", "BUSY")
    assert ds.name == "foobar"
    assert ds.state == "BUSY"


async def test_delete(repo):
    with respx.mock:
        respx.delete(f"{BASE}/deviceStates/dev1").mock(return_value=httpx.Response(204))
        await repo.delete("dev1")
