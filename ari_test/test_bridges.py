import httpx
import pytest
import respx

from ari.models import Bridge, Playback
from ari.repositories.bridges import BridgeRepository

BASE = "http://ari.py/ari"


@pytest.fixture
async def repo():
    async with httpx.AsyncClient(base_url=BASE) as http:
        yield BridgeRepository(http, client=None)


async def test_list_empty(repo):
    with respx.mock:
        respx.get(f"{BASE}/bridges").mock(return_value=httpx.Response(200, json=[]))
        result = await repo.list()
    assert result == []


async def test_create(repo):
    with respx.mock:
        respx.post(f"{BASE}/bridges").mock(
            return_value=httpx.Response(
                200, json={"id": "br-1", "technology": "simple_bridge"}
            )
        )
        br = await repo.create(type="mixing")
    assert isinstance(br, Bridge)
    assert br.id == "br-1"


async def test_get(repo):
    with respx.mock:
        respx.get(f"{BASE}/bridges/br-1").mock(
            return_value=httpx.Response(200, json={"id": "br-1"})
        )
        br = await repo.get("br-1")
    assert br.id == "br-1"


async def test_destroy(repo):
    with respx.mock:
        respx.delete(f"{BASE}/bridges/br-1").mock(return_value=httpx.Response(204))
        await repo.destroy("br-1")


async def test_add_channel(repo):
    with respx.mock:
        respx.post(f"{BASE}/bridges/br-1/addChannel").mock(
            return_value=httpx.Response(204)
        )
        await repo.add_channel("br-1", "ch-1")


async def test_play(repo):
    with respx.mock:
        respx.post(f"{BASE}/bridges/br-1/play").mock(
            return_value=httpx.Response(200, json={"id": "pb-1", "state": "playing"})
        )
        pb = await repo.play("br-1", "sound:beep")
    assert isinstance(pb, Playback)
