import requests
import logging
from typing import Dict
from tools.base_tool import BaseTool
from utils.error_handler import LocationError

logger = logging.getLogger(__name__)

class ClothingTool(BaseTool):
    def __init__(self):
        super().__init__()
        # Basic clothing recommendations by temperature range (°C)
        self.recommendations = {
            'very_cold': {  # Below 0°C
                'base': ['Thermal underwear', 'Warm long-sleeve shirt'],
                'mid': ['Wool sweater', 'Fleece jacket'],
                'outer': ['Heavy winter coat'],
                'bottom': ['Insulated pants', 'Thermal leggings'],
                'accessories': ['Warm hat', 'Scarf', 'Gloves', 'Warm socks', 'Winter boots']
            },
            'cold': {  # 0-10°C
                'base': ['Long-sleeve thermal shirt'],
                'mid': ['Sweater'],
                'outer': ['Winter jacket'],
                'bottom': ['Warm pants'],
                'accessories': ['Light hat', 'Scarf', 'Gloves']
            },
            'mild': {  # 10-20°C
                'base': ['Long-sleeve shirt'],
                'mid': ['Light jacket'],
                'bottom': ['Regular pants', 'Jeans'],
                'accessories': ['Light scarf']
            },
            'warm': {  # 20-25°C
                'base': ['T-shirt', 'Short-sleeve shirt'],
                'bottom': ['Light pants', 'Shorts'],
                'accessories': ['Sunglasses']
            },
            'hot': {  # Above 25°C
                'base': ['Light t-shirt', 'Tank top'],
                'bottom': ['Shorts', 'Light skirt'],
                'accessories': ['Sunglasses', 'Sun hat']
            }
        }

    def name(self):
        return "Clothing Agent"

    def description(self):
        return "Recommends clothing based on weather conditions."

    def _get_weather_data(self, lat: float, lon: float) -> dict:
        """Get current weather data from Open-Meteo API."""
        try:
            url = "https://api.open-meteo.com/v1/forecast"
            params = {
                "latitude": lat,
                "longitude": lon,
                "current": ["temperature_2m", "weather_code", "wind_speed_10m"],
                "timezone": "auto"
            }
            
            response = requests.get(url, params=params)
            data = response.json()
            
            if "current" not in data:
                return None
                
            current = data["current"]
            return {
                "temperature": current["temperature_2m"],
                "weather_code": current["weather_code"],
                "wind_speed": current["wind_speed_10m"]
            }
        except Exception as e:
            logger.error(f"Error getting weather data: {e}")
            return None

    def _get_temperature_range(self, temp: float) -> str:
        """Determine temperature range category."""
        if temp < 0:
            return 'very_cold'
        elif temp < 10:
            return 'cold'
        elif temp < 20:
            return 'mild'
        elif temp < 25:
            return 'warm'
        else:
            return 'hot'

    def _adjust_for_conditions(self, recommendations: Dict, weather_code: int, wind_speed: float):
        """Adjust clothing recommendations based on weather conditions."""
        # Rain conditions (codes 51-65, 80-82)
        if 51 <= weather_code <= 65 or 80 <= weather_code <= 82:
            recommendations['outer'] = recommendations.get('outer', []) + ['Rain jacket']
            recommendations['accessories'].append('Umbrella')

        # Snow conditions (codes 71-77, 85-86)
        elif 71 <= weather_code <= 77 or 85 <= weather_code <= 86:
            recommendations['outer'] = recommendations.get('outer', []) + ['Snow-proof jacket']
            recommendations['accessories'].extend(['Snow boots', 'Waterproof gloves'])

        # Strong wind (> 20 km/h)
        if wind_speed > 20:
            recommendations['outer'] = recommendations.get('outer', []) + ['Windbreaker']

    def use(self, location) -> str:
        """Get clothing recommendations for a location."""
        try:
            # Handle dictionary input
            if isinstance(location, dict):
                location = location.get('location', '')
            
            # Get location info
            try:
                location_info = self.location_utils.get_location_info(location)
                lat = location_info["latitude"]
                lon = location_info["longitude"]
                name = location_info["name"]
                country = location_info.get("country", "")
            except LocationError as e:
                return f"Sorry, I couldn't find the location: {location}"
            
            # Get weather data
            weather = self._get_weather_data(lat, lon)
            if not weather:
                return f"Sorry, I couldn't get weather data for {location}"

            # Get base recommendations for temperature
            temp_range = self._get_temperature_range(weather['temperature'])
            recommendations = self.recommendations[temp_range].copy()

            # Adjust for weather conditions
            self._adjust_for_conditions(
                recommendations,
                weather['weather_code'],
                weather['wind_speed']
            )

            # Format response
            loc_name = f"{name}, {country}" if country else name
            response = [f"Based on the current temperature of {weather['temperature']}°C in {loc_name}, here's what you should wear:"]
            
            for category, items in recommendations.items():
                if items:
                    category_name = category.replace('_', ' ').title()
                    items_str = ', '.join(items)
                    response.append(f"{category_name}: {items_str}")

            return '\n'.join(response)

        except Exception as e:
            logger.error(f"Error in ClothingTool: {e}")
            return "Sorry, I encountered an error getting clothing recommendations." 