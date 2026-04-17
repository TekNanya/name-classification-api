import httpx

async def get_age(name: str):
    async with httpx.AsyncClient(timeout=5) as client:
        r = await client.get("https://api.agify.io", params={"name": name})
        return r.json()