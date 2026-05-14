import httpx
import pytest
import respx

from ari.models import LiveRecording, StoredRecording
from ari.repositories.recordings import RecordingRepository

BASE = "http://ari.py/ari"


@pytest.fixture
async def repo():
    async with httpx.AsyncClient(base_url=BASE) as http:
        yield RecordingRepository(http, client=None)


async def test_get_live(repo):
    with respx.mock:
        respx.get(f"{BASE}/recordings/live/test-rec").mock(
            return_value=httpx.Response(
                200, json={"name": "test-rec", "state": "recording"}
            )
        )
        rec = await repo.get_live("test-rec")
    assert isinstance(rec, LiveRecording)
    assert rec.name == "test-rec"


async def test_cancel(repo):
    with respx.mock:
        respx.delete(f"{BASE}/recordings/live/test-rec").mock(
            return_value=httpx.Response(204)
        )
        await repo.cancel("test-rec")


async def test_stop(repo):
    with respx.mock:
        respx.post(f"{BASE}/recordings/live/test-rec/stop").mock(
            return_value=httpx.Response(204)
        )
        await repo.stop("test-rec")


async def test_pause(repo):
    with respx.mock:
        respx.post(f"{BASE}/recordings/live/test-rec/pause").mock(
            return_value=httpx.Response(204)
        )
        await repo.pause("test-rec")


async def test_unpause(repo):
    with respx.mock:
        respx.delete(f"{BASE}/recordings/live/test-rec/pause").mock(
            return_value=httpx.Response(204)
        )
        await repo.unpause("test-rec")


async def test_mute(repo):
    with respx.mock:
        respx.post(f"{BASE}/recordings/live/test-rec/mute").mock(
            return_value=httpx.Response(204)
        )
        await repo.mute("test-rec")


async def test_unmute(repo):
    with respx.mock:
        respx.delete(f"{BASE}/recordings/live/test-rec/mute").mock(
            return_value=httpx.Response(204)
        )
        await repo.unmute("test-rec")


async def test_list_stored(repo):
    with respx.mock:
        respx.get(f"{BASE}/recordings/stored").mock(
            return_value=httpx.Response(200, json=[{"name": "r1", "format": "wav"}])
        )
        result = await repo.list_stored()
    assert len(result) == 1
    assert isinstance(result[0], StoredRecording)


async def test_get_stored(repo):
    with respx.mock:
        respx.get(f"{BASE}/recordings/stored/test-rec").mock(
            return_value=httpx.Response(200, json={"name": "test-rec", "format": "wav"})
        )
        rec = await repo.get_stored("test-rec")
    assert isinstance(rec, StoredRecording)
    assert rec.name == "test-rec"


async def test_delete_stored(repo):
    with respx.mock:
        respx.delete(f"{BASE}/recordings/stored/test-rec").mock(
            return_value=httpx.Response(204)
        )
        await repo.delete_stored("test-rec")
