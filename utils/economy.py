from utils.db import load
from pathlib import Path
import json

PATH = "data/economy.json"


def _save(data):
    Path(PATH).write_text(
        json.dumps(data, indent=2),
        encoding="utf-8"
    )


def get(uid):
    data = load(PATH)
    return data.get(str(uid), 0)


def add(uid, amount):
    data = load(PATH)

    uid = str(uid)

    if uid not in data:
        data[uid] = 0

    data[uid] += amount

    if data[uid] < 0:
        data[uid] = 0

    _save(data)
    return data[uid]