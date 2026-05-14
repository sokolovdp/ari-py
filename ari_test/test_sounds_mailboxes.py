import httpx
import pytest
import respx

from ari.models import Sound, Mailbox
from ari.repositories.sounds import SoundRepository
from ari.repositories.mailboxes import MailboxRepository

BASE = "http://ari.py/ari"


@pytest.fixture
async def sound_repo():
    async with httpx.AsyncClient(base_url=BASE) as http:
        yield SoundRepository(http, client=None)


@pytest.fixture
async def mailbox_repo():
    async with httpx.AsyncClient(base_url=BASE) as http:
        yield MailboxRepository(http, client=None)


async def test_sound_list(sound_repo):
    with respx.mock:
        respx.get(f"{BASE}/sounds").mock(
            return_value=httpx.Response(200, json=[{"id": "beep", "formats": []}])
        )
        result = await sound_repo.list()
    assert len(result) == 1
    assert isinstance(result[0], Sound)


async def test_sound_get(sound_repo):
    with respx.mock:
        respx.get(f"{BASE}/sounds/beep").mock(
            return_value=httpx.Response(
                200, json={"id": "beep", "text": "A beep sound"}
            )
        )
        s = await sound_repo.get("beep")
    assert s.id == "beep"


async def test_mailbox_list(mailbox_repo):
    with respx.mock:
        respx.get(f"{BASE}/mailboxes").mock(
            return_value=httpx.Response(
                200, json=[{"name": "1000", "old_messages": "0", "new_messages": "2"}]
            )
        )
        result = await mailbox_repo.list()
    assert len(result) == 1
    assert isinstance(result[0], Mailbox)


async def test_mailbox_update(mailbox_repo):
    with respx.mock:
        respx.put(f"{BASE}/mailboxes/1000").mock(
            return_value=httpx.Response(
                200, json={"name": "1000", "old_messages": "1", "new_messages": "3"}
            )
        )
        mb = await mailbox_repo.update("1000", old_messages=1, new_messages=3)
    assert mb.name == "1000"
    assert mb.old_messages == "1"


async def test_mailbox_delete(mailbox_repo):
    with respx.mock:
        respx.delete(f"{BASE}/mailboxes/1000").mock(return_value=httpx.Response(204))
        await mailbox_repo.delete("1000")
