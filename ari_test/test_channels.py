import httpx
import pytest
import respx

from ari.models import Channel, Playback, LiveRecording
from ari.repositories.channels import ChannelRepository
from ari.exceptions import ARINotFound

BASE = "http://ari.py/ari"


@pytest.fixture
async def repo():
    async with httpx.AsyncClient(base_url=BASE) as http:
        yield ChannelRepository(http, client=None)


async def test_list_empty(repo):
    with respx.mock:
        respx.get(f"{BASE}/channels").mock(return_value=httpx.Response(200, json=[]))
        result = await repo.list()
    assert result == []


async def test_list_one(repo):
    with respx.mock:
        respx.get(f"{BASE}/channels").mock(
            return_value=httpx.Response(200, json=[{"id": "ch-1"}])
        )
        result = await repo.list()
    assert len(result) == 1
    assert isinstance(result[0], Channel)
    assert result[0].id == "ch-1"


async def test_get(repo):
    with respx.mock:
        respx.get(f"{BASE}/channels/ch-1").mock(
            return_value=httpx.Response(200, json={"id": "ch-1", "state": "Up"})
        )
        ch = await repo.get("ch-1")
    assert ch.id == "ch-1"
    assert ch.state == "Up"


async def test_get_not_found(repo):
    with respx.mock:
        respx.get(f"{BASE}/channels/missing").mock(
            return_value=httpx.Response(404, json={"message": "not found"})
        )
        with pytest.raises(ARINotFound):
            await repo.get("missing")


async def test_hangup(repo):
    with respx.mock:
        respx.delete(f"{BASE}/channels/ch-1").mock(return_value=httpx.Response(204))
        await repo.hangup("ch-1")


async def test_answer(repo):
    with respx.mock:
        respx.post(f"{BASE}/channels/ch-1/answer").mock(
            return_value=httpx.Response(204)
        )
        await repo.answer("ch-1")


async def test_play(repo):
    with respx.mock:
        respx.post(f"{BASE}/channels/ch-1/play").mock(
            return_value=httpx.Response(
                200, json={"id": "pb-1", "media_uri": "sound:beep", "state": "playing"}
            )
        )
        pb = await repo.play("ch-1", "sound:beep")
    assert isinstance(pb, Playback)
    assert pb.id == "pb-1"


async def test_record(repo):
    with respx.mock:
        respx.post(f"{BASE}/channels/ch-1/record").mock(
            return_value=httpx.Response(
                200, json={"name": "my-rec", "format": "wav", "state": "recording"}
            )
        )
        rec = await repo.record("ch-1", "my-rec", "wav")
    assert isinstance(rec, LiveRecording)
    assert rec.name == "my-rec"


async def test_get_channel_var(repo):
    with respx.mock:
        respx.get(f"{BASE}/channels/ch-1/variable").mock(
            return_value=httpx.Response(200, json={"value": "myval"})
        )
        val = await repo.get_channel_var("ch-1", "MY_VAR")
    assert val == "myval"
