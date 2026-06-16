import aiohttp
import random

JOKE_URL = "https://v2.jokeapi.dev/joke/Any"

async def get_joke():
    params = {
        "blacklistFlags": "nsfw,religious,racist,sexist,explicit",
        "type": "single,twopart"
    }

    async with aiohttp.ClientSession() as session:
        async with session.get(JOKE_URL, params=params) as r:
            data = await r.json()

    if data.get("error"):
        return "No joke available right now."

    if data["type"] == "single":
        return data["joke"]

    return f"{data['setup']} ... {data['delivery']}"