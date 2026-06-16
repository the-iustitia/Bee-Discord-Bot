import pycountry
import pytz
from datetime import datetime


def find_country(query: str):
    query = query.lower().strip()

    country = pycountry.countries.get(alpha_2=query.upper())
    if country:
        return country

    for c in pycountry.countries:
        if query == c.name.lower():
            return c

    for c in pycountry.countries:
        if query in c.name.lower():
            return c

    return None


def get_time_by_country(query: str):
    country = find_country(query)

    if not country:
        return None, None, None

    timezones = pytz.country_timezones.get(country.alpha_2)

    if not timezones:
        return country.name, None, None

    tz = timezones[0]
    now = datetime.now(pytz.timezone(tz))

    return country.name, tz, now.strftime("%Y-%m-%d %H:%M:%S")