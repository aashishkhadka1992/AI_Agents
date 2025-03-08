import requests
import logging
from datetime import datetime
import pytz
from tools.base_tool import Tool

logger = logging.getLogger(__name__)

class WeatherTool(Tool):
    def __init__(self):
        self.weather_codes = {
            0: "clear sky", 1: "mainly clear", 2: "partly cloudy", 3: "overcast",
            45: "foggy", 48: "depositing rime fog",
            51: "light drizzle", 53: "moderate drizzle", 55: "dense drizzle",
            61: "slight rain", 63: "moderate rain", 65: "heavy rain",
            71: "slight snow", 73: "moderate snow", 75: "heavy snow",
            77: "snow grains", 95: "thunderstorm",
            96: "thunderstorm with slight hail", 99: "thunderstorm with heavy hail"
        }

    def name(self):
        return "Weather Agent"

    def description(self):
        return "Provides current weather information for a given location."

    def _get_location_coordinates(self, location: str) -> tuple:
        """Get coordinates for a location using Open-Meteo Geocoding API."""
        try:
            # Clean up location string
            location = location.replace(", ", ",").strip()
            
            url = "https://geocoding-api.open-meteo.com/v1/search"
            response = requests.get(url, params={"name": location, "count": 1})
            data = response.json()
            
            if "results" in data and data["results"]:
                result = data["results"][0]
                return (
                    result["latitude"], 
                    result["longitude"],
                    result["name"],
                    result.get("country", "")
                )
            
            # If no results, try without country code
            if "," in location:
                city = location.split(",")[0].strip()
                response = requests.get(url, params={"name": city, "count": 1})
                data = response.json()
                
                if "results" in data and data["results"]:
                    result = data["results"][0]
                    return (
                        result["latitude"], 
                        result["longitude"],
                        result["name"],
                        result.get("country", "")
                    )
            
            return None
        except Exception as e:
            logger.error(f"Error getting coordinates for {location}: {e}")
            return None

    def _get_weather_data(self, lat: float, lon: float) -> dict:
        """Get current weather data from Open-Meteo API."""
        try:
            url = "https://api.open-meteo.com/v1/forecast"
            params = {
                "latitude": lat,
                "longitude": lon,
                "current": [
                    "temperature_2m",
                    "relative_humidity_2m",
                    "apparent_temperature",
                    "precipitation",
                    "weather_code",
                    "wind_speed_10m"
                ],
                "timezone": "auto"
            }
            
            response = requests.get(url, params=params)
            data = response.json()
            
            if "current" not in data:
                return None
                
            current = data["current"]
            return {
                "temperature": current["temperature_2m"],
                "feels_like": current["apparent_temperature"],
                "humidity": current["relative_humidity_2m"],
                "precipitation": current["precipitation"],
                "wind_speed": current["wind_speed_10m"],
                "description": self.weather_codes.get(current["weather_code"], "unknown"),
                "timezone": data.get("timezone", "UTC")
            }
        except Exception as e:
            logger.error(f"Error getting weather data: {e}")
            return None

    def use(self, location: str) -> str:
        """Get current weather for a location."""
        try:
            # Get coordinates
            loc_data = self._get_location_coordinates(location)
            if not loc_data:
                return f"Sorry, I couldn't find the location: {location}"
            
            lat, lon, name, country = loc_data
            
            # Get weather data
            weather = self._get_weather_data(lat, lon)
            if not weather:
                return f"Sorry, I couldn't get weather data for {location}"

            # Format location name
            loc_name = f"{name}, {country}" if country else name
            
            # Get local time
            local_tz = pytz.timezone(weather["timezone"])
            local_time = datetime.now(local_tz).strftime("%I:%M %p")
            
            # Format response
            response = (
                f"Weather in {loc_name} at {local_time}:\n"
                f"Temperature: {weather['temperature']}°C "
                f"(feels like {weather['feels_like']}°C)\n"
                f"Conditions: {weather['description']}\n"
                f"Humidity: {weather['humidity']}%\n"
                f"Wind Speed: {weather['wind_speed']} km/h"
            )
            
            if weather['precipitation'] > 0:
                response += f"\nPrecipitation: {weather['precipitation']} mm"
            
            return response

        except Exception as e:
            logger.error(f"Error in WeatherTool: {e}")
            return "Sorry, I encountered an error getting the weather information."