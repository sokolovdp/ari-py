import httpx
import respx

from ari.client import ARIClient
from ari.models import Channel

BASE_URL = "http://ari.py"


async def test_connect_creates_client():
    from ari import connect

    client = connect(BASE_URL, "user", "pass")
    assert isinstance(client, ARIClient)
    assert client._base_url == BASE_URL
    await client.close()


async def test_async_context_manager():
    from ari import connect

    async with connect(BASE_URL, "user", "pass") as client:
        assert isinstance(client, ARIClient)


async def test_channels_repo_is_available(ari_client):
    with respx.mock:
        respx.get(f"{BASE_URL}/ari/channels").mock(
            return_value=httpx.Response(200, json=[])
        )
        result = await ari_client.channels.list()
    assert result == []


async def test_channel_fluent_hangup(ari_client):
    with respx.mock:
        respx.get(f"{BASE_URL}/ari/channels/ch-1").mock(
            return_value=httpx.Response(200, json={"id": "ch-1"})
        )
        respx.delete(f"{BASE_URL}/ari/channels/ch-1").mock(
            return_value=httpx.Response(204)
        )
        ch = await ari_client.channels.get("ch-1")
        assert isinstance(ch, Channel)
        await ch.hangup()


async def test_channel_fluent_play(ari_client):
    from ari.models import Playback

    with respx.mock:
        respx.get(f"{BASE_URL}/ari/channels/ch-1").mock(
            return_value=httpx.Response(200, json={"id": "ch-1"})
        )
        respx.post(f"{BASE_URL}/ari/channels/ch-1/play").mock(
            return_value=httpx.Response(200, json={"id": "pb-1", "state": "playing"})
        )
        ch = await ari_client.channels.get("ch-1")
        pb = await ch.play("sound:beep")
    assert isinstance(pb, Playback)
    assert pb.id == "pb-1"
