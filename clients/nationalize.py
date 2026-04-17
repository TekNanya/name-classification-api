import httpx

async def get_country(name: str):
    async with httpx.AsyncClient(timeout=5) as client:
        r = await client.get("https://api.nationalize.io", params={"name": name})
        return r.json()