from zoneinfo import ZoneInfo
from datetime import datetime
from utils.db import load

PATH = "data/timezones.json"


def get_time_by_key(key):
    data = load(PATH)

    zone = data.get(key.lower())
    if not zone:
        return None

    return datetime.now(ZoneInfo(zone)).strftime("%H:%M:%S")