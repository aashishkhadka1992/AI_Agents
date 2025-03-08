import requests
import logging
from datetime import datetime
import pytz
from tools.base_tool import Tool

logger = logging.getLogger(__name__)

class TimeTool(Tool):
    def __init__(self):
        pass

    def name(self):
        return "Time Agent"

    def description(self):
        return "Provides current time for a given location."

    def _get_location_timezone(self, location: str) -> str:
        """Get timezone for a location using Open-Meteo Geocoding API."""
        try:
            # Clean up location string
            location = location.replace(", ", ",").strip()
            
            url = "https://geocoding-api.open-meteo.com/v1/search"
            response = requests.get(url, params={"name": location, "count": 1})
            data = response.json()
            
            if "results" in data and data["results"]:
                result = data["results"][0]
                return (
                    result.get("timezone", "UTC"),
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
                        result.get("timezone", "UTC"),
                        result["name"],
                        result.get("country", "")
                    )
            
            return None
        except Exception as e:
            logger.error(f"Error getting timezone for {location}: {e}")
            return None

    def use(self, location: str) -> str:
        """Get current time for a location."""
        try:
            # Get timezone
            tz_data = self._get_location_timezone(location)
            if not tz_data:
                return f"Sorry, I couldn't find the location: {location}"
            
            timezone, name, country = tz_data
            
            # Format location name
            loc_name = f"{name}, {country}" if country else name
            
            # Get current time in location's timezone
            tz = pytz.timezone(timezone)
            current_time = datetime.now(tz)
            
            # Format response
            return (
                f"The current time in {loc_name} is "
                f"{current_time.strftime('%I:%M %p')} "
                f"({timezone})"
            )

        except Exception as e:
            logger.error(f"Error in TimeTool: {e}")
            return "Sorry, I encountered an error getting the time information."