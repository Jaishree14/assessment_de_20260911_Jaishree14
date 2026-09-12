import requests
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

BASE_URL = "https://archive-api.open-meteo.com/v1/archive"


@retry(
    reraise=True,
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=2, max=10),
    retry=retry_if_exception_type((requests.ConnectionError, requests.Timeout)),
)
def fetch_weather(latitude: float, longitude: float, date: str) -> dict:
    """Fetch one city's daily weather for a single date from Open-Meteo's archive API."""
    response = requests.get(
        BASE_URL,
        params={
            "latitude": latitude,
            "longitude": longitude,
            "start_date": date,
            "end_date": date,
            "daily": "temperature_2m_max,temperature_2m_min,precipitation_sum",
            "timezone": "UTC",
        },
        timeout=15,
    )
    response.raise_for_status()
    return response.json()


def extract_all(logical_date: str, cities: list[dict]) -> dict[str, dict]:
    """Extract weather for every configured city on one logical date.

    Returns {city_name: raw_api_response_dict}.
    """
    results = {}
    for city in cities:
        results[city["name"]] = fetch_weather(
            city["latitude"], city["longitude"], logical_date
        )
    return results