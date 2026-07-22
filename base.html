from datetime import datetime
from typing import Any

import httpx


class WeatherClient:
    USER_AGENT = "EdgeBoardMLB/2.1 (personal model dashboard)"

    async def forecast_for(self, latitude: float | None, longitude: float | None, game_time: datetime) -> dict[str, Any]:
        if latitude is None or longitude is None:
            return self.neutral()
        headers = {"User-Agent": self.USER_AGENT, "Accept": "application/geo+json"}
        try:
            async with httpx.AsyncClient(timeout=20, headers=headers) as client:
                point = await client.get(f"https://api.weather.gov/points/{latitude},{longitude}")
                point.raise_for_status()
                hourly_url = point.json()["properties"]["forecastHourly"]
                forecast = await client.get(hourly_url)
                forecast.raise_for_status()
                periods = forecast.json()["properties"]["periods"]

            closest = min(
                periods,
                key=lambda p: abs(datetime.fromisoformat(p["startTime"]).timestamp() - game_time.timestamp())
            )
            wind_speed = self._parse_wind(closest.get("windSpeed", "0 mph"))
            temp = float(closest.get("temperature", 72))
            precip = float(closest.get("probabilityOfPrecipitation", {}).get("value") or 0)
            wind_dir = closest.get("windDirection", "")
            factor = 1.0 + (temp - 72) * 0.002
            if wind_speed >= 8:
                # Cardinal direction alone cannot establish out/in for every park, so use a conservative variance bump.
                factor += min(wind_speed, 20) * 0.001
            factor -= min(precip, 100) * 0.0004
            return {
                "temperature": temp,
                "wind_speed": wind_speed,
                "wind_direction": wind_dir,
                "precip_probability": precip,
                "description": closest.get("shortForecast", ""),
                "run_factor": max(0.90, min(1.12, factor)),
                "quality": 78,
            }
        except Exception:
            return self.neutral()

    @staticmethod
    def _parse_wind(value: str) -> float:
        import re
        nums = [float(x) for x in re.findall(r"\d+(?:\.\d+)?", value)]
        return sum(nums) / len(nums) if nums else 0.0

    @staticmethod
    def neutral() -> dict[str, Any]:
        return {
            "temperature": 72.0,
            "wind_speed": 0.0,
            "wind_direction": "",
            "precip_probability": 0.0,
            "description": "Weather unavailable",
            "run_factor": 1.0,
            "quality": 45,
        }
