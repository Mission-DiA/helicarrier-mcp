from typing import Any, Optional

import httpx


class HelicarrierClient:
    def __init__(self, base_url: str, api_key: str) -> None:
        self._base_url = base_url.rstrip("/")
        self._api_key = api_key
        self._client: Optional[httpx.AsyncClient] = None

    async def _get_client(self) -> httpx.AsyncClient:
        if self._client is None:
            self._client = httpx.AsyncClient(
                base_url=self._base_url,
                headers={"Authorization": f"Bearer {self._api_key}"},
                timeout=30.0,
            )
        return self._client

    async def get(self, path: str, params: Optional[dict[str, Any]] = None) -> dict:
        client = await self._get_client()
        # Strip None values from params
        if params:
            params = {k: v for k, v in params.items() if v is not None}
        response = await client.get(path, params=params or None)
        response.raise_for_status()
        return response.json()

    async def post(self, path: str, data: Optional[dict[str, Any]] = None) -> dict:
        client = await self._get_client()
        response = await client.post(path, json=data or {})
        response.raise_for_status()
        return response.json()
