import httpx

async def get_gender(name: str):
    async with httpx.AsyncClient(timeout=5) as client:
        r = await client.get("https://api.genderize.io", params={"name": name})
        return r.json()