from __future__ import annotations

from typing import TYPE_CHECKING

import httpx

from ari.exceptions import raise_for_status
from ari.models import DeviceState

if TYPE_CHECKING:
    from ari.client import ARIClient


class DeviceStateRepository:
    def __init__(self, http: httpx.AsyncClient, client: ARIClient | None) -> None:
        self._http = http
        self._client = client

    async def list(self) -> list[DeviceState]:
        r = await self._http.get("/deviceStates")
        raise_for_status(r, self._client)
        return [DeviceState._with_client(ds, self._client) for ds in r.json()]

    async def get(self, device_name: str) -> DeviceState:
        r = await self._http.get(f"/deviceStates/{device_name}")
        raise_for_status(r, self._client)
        return DeviceState._with_client(r.json(), self._client)

    async def update(self, device_name: str, device_state: str) -> DeviceState:
        r = await self._http.put(
            f"/deviceStates/{device_name}",
            params={"deviceState": device_state},
        )
        raise_for_status(r, self._client)
        return DeviceState._with_client(r.json(), self._client)

    async def delete(self, device_name: str) -> None:
        r = await self._http.delete(f"/deviceStates/{device_name}")
        raise_for_status(r, self._client)
