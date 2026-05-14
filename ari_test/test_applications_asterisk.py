import httpx
import pytest
import respx

from ari.repositories.applications import ApplicationRepository
from ari.repositories.asterisk import AsteriskRepository

BASE = "http://ari.py/ari"


@pytest.fixture
async def app_repo():
    async with httpx.AsyncClient(base_url=BASE) as http:
        yield ApplicationRepository(http, client=None)


@pytest.fixture
async def asterisk_repo():
    async with httpx.AsyncClient(base_url=BASE) as http:
        yield AsteriskRepository(http, client=None)


async def test_app_list(app_repo):
    with respx.mock:
        respx.get(f"{BASE}/applications").mock(
            return_value=httpx.Response(200, json=[{"name": "my-app"}])
        )
        result = await app_repo.list()
    assert result == [{"name": "my-app"}]


async def test_app_get(app_repo):
    with respx.mock:
        respx.get(f"{BASE}/applications/my-app").mock(
            return_value=httpx.Response(200, json={"name": "my-app"})
        )
        result = await app_repo.get("my-app")
    assert result["name"] == "my-app"


async def test_app_subscribe(app_repo):
    with respx.mock:
        respx.post(f"{BASE}/applications/my-app/subscription").mock(
            return_value=httpx.Response(200, json={"name": "my-app"})
        )
        result = await app_repo.subscribe("my-app", "channel:ch-1")
    assert result["name"] == "my-app"


async def test_app_unsubscribe(app_repo):
    with respx.mock:
        respx.delete(f"{BASE}/applications/my-app/subscription").mock(
            return_value=httpx.Response(200, json={"name": "my-app"})
        )
        result = await app_repo.unsubscribe("my-app", "channel:ch-1")
    assert result["name"] == "my-app"


async def test_asterisk_get_info(asterisk_repo):
    with respx.mock:
        respx.get(f"{BASE}/asterisk/info").mock(
            return_value=httpx.Response(200, json={"build": {}, "system": {}})
        )
        result = await asterisk_repo.get_info()
    assert "build" in result


async def test_asterisk_get_global_var(asterisk_repo):
    with respx.mock:
        respx.get(f"{BASE}/asterisk/variable").mock(
            return_value=httpx.Response(200, json={"value": "hello"})
        )
        val = await asterisk_repo.get_global_var("MY_VAR")
    assert val == "hello"


async def test_asterisk_set_global_var(asterisk_repo):
    with respx.mock:
        respx.post(f"{BASE}/asterisk/variable").mock(return_value=httpx.Response(204))
        await asterisk_repo.set_global_var("MY_VAR", "hello")
