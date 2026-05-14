import httpx
import pytest
import respx

from ari.models import Playback
from ari.repositories.playbacks import PlaybackRepository

BASE = "http://ari.py/ari"


@pytest.fixture
async def repo():
    async with httpx.AsyncClient(base_url=BASE) as http:
        yield PlaybackRepository(http, client=None)


async def test_get(repo):
    with respx.mock:
        respx.get(f"{BASE}/playbacks/pb-1").mock(
            return_value=httpx.Response(200, json={"id": "pb-1", "state": "playing"})
        )
        pb = await repo.get("pb-1")
    assert isinstance(pb, Playback)
    assert pb.id == "pb-1"


async def test_stop(repo):
    with respx.mock:
        respx.delete(f"{BASE}/playbacks/pb-1").mock(return_value=httpx.Response(204))
        await repo.stop("pb-1")


async def test_control(repo):
    with respx.mock:
        respx.post(f"{BASE}/playbacks/pb-1/control").mock(
            return_value=httpx.Response(204)
        )
        await repo.control("pb-1", "pause")
