import httpx
import pytest
import respx

from ari.models import Endpoint
from ari.repositories.endpoints import EndpointRepository

BASE = "http://ari.py/ari"


@pytest.fixture
async def repo():
    async with httpx.AsyncClient(base_url=BASE) as http:
        yield EndpointRepository(http, client=None)


async def test_list(repo):
    with respx.mock:
        respx.get(f"{BASE}/endpoints").mock(
            return_value=httpx.Response(
                200, json=[{"technology": "PJSIP", "resource": "100"}]
            )
        )
        result = await repo.list()
    assert len(result) == 1
    assert isinstance(result[0], Endpoint)
    assert result[0].technology == "PJSIP"


async def test_list_by_tech(repo):
    with respx.mock:
        respx.get(f"{BASE}/endpoints/PJSIP").mock(
            return_value=httpx.Response(
                200, json=[{"technology": "PJSIP", "resource": "100"}]
            )
        )
        result = await repo.list_by_tech("PJSIP")
    assert len(result) == 1


async def test_get(repo):
    with respx.mock:
        respx.get(f"{BASE}/endpoints/PJSIP/100").mock(
            return_value=httpx.Response(
                200, json={"technology": "PJSIP", "resource": "100", "state": "online"}
            )
        )
        ep = await repo.get("PJSIP", "100")
    assert ep.state == "online"
