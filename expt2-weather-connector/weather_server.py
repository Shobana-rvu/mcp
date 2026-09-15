# expt2-weather-connector/server.py
import requests
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("weather-connector")


@mcp.tool()
def get_current_weather(location: str) -> str:
    """Get the current weather for a given location (city name)."""
    try:
        response = requests.get(f"https://wttr.in/{location}?format=j1", timeout=10)
        response.raise_for_status()
        data = response.json()
        current = data["current_condition"][0]
        return (
            f"Weather in {location}: {current['weatherDesc'][0]['value']}, "
            f"{current['temp_C']}°C (feels like {current['FeelsLikeC']}°C), "
            f"humidity {current['humidity']}%, "
            f"wind {current['windspeedKmph']} km/h"
        )
    except Exception as e:
        return f"Couldn't fetch weather for {location}: {e}"


if __name__ == "__main__":
    mcp.run(transport="stdio")
