# Building an AI-Powered Personal Assistant for Weather-Based Clothing Recommendations

In this tutorial, we'll walk through building a sophisticated AI-powered personal assistant that helps users choose appropriate clothing based on weather conditions. We'll cover everything from setting up the project structure to implementing advanced features like location awareness and smart clothing recommendations.

## Table of Contents
1. [Project Overview](#project-overview)
2. [System Architecture](#system-architecture)
3. [Implementation Steps](#implementation-steps)
4. [Key Components](#key-components)
5. [Testing and Validation](#testing-and-validation)
6. [Future Enhancements](#future-enhancements)

## Project Overview

Our personal assistant is designed to:
- Process location data and fetch weather information
- Analyze weather conditions comprehensively
- Generate contextual clothing recommendations
- Maintain conversation history for better suggestions
- Handle edge cases and special weather conditions

### Tech Stack
- Python 3.9+
- OpenAI/Anthropic for LLM capabilities
- Open-Meteo API for weather data
- Location services via Open-Meteo Geocoding API
- Custom utilities for data processing

## System Architecture

The system is built with a modular architecture consisting of:

```
src/
├── agents/         # AI agent implementations
├── tools/          # Utility tools and APIs
├── utils/          # Helper functions
├── llm/           # LLM integration
├── tests/         # Test suite
└── main.py        # Application entry point
```

### Key Components:

1. **LocationUtils**: Handles location validation and processing
2. **WeatherUtils**: Processes weather data and conditions
3. **ClothingUtils**: Manages clothing recommendations
4. **PersonalAssistantAgent**: Orchestrates the entire interaction

## Implementation Steps

### Step 1: Location and Weather Integration

First, we implement location handling with caching and validation:

```python
# src/utils/location_utils.py
class LocationUtils:
    def __init__(self):
        self.cache = {}  # Simple in-memory cache
        self.geocoding_api = "https://geocoding-api.open-meteo.com/v1/search"
        
    def validate_and_normalize_location(self, location: str) -> bool:
        try:
            # Check cache first
            if location in self.cache:
                return True
                
            # Clean location string
            location = location.strip()
            if not location:
                raise LocationError("Location cannot be empty")
                
            # Query geocoding API
            params = {
                "name": location,
                "count": 1
            }
            
            response = requests.get(self.geocoding_api, params=params)
            response.raise_for_status()
            
            data = response.json()
            if not data.get("results"):
                raise LocationError(
                    message=f"Could not find location: {location}",
                    location=location,
                    details={"api_response": data}
                )
                
            # Cache the result
            self.cache[location] = data["results"][0]
            return True
            
        except Exception as e:
            raise LocationError(
                message=f"Error validating location: {str(e)}",
                location=location
            )
```

### Step 2: Weather Processing

The WeatherTool class handles weather data processing:

```python
# src/tools/weather_tool.py
class WeatherTool(Tool):
    def _get_weather_data(self, lat: float, lon: float) -> dict:
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
```

### Step 3: Clothing Recommendation Engine

The clothing recommendation system provides contextual suggestions:

```python
# src/tools/clothing_tool.py
class ClothingTool(Tool):
    def use(self, location: str) -> str:
        try:
            # Get coordinates
            coords = self._get_location_coordinates(location)
            if not coords:
                return f"Sorry, I couldn't find the location: {location}"
            
            # Get weather data
            weather = self._get_weather_data(*coords)
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
            response = [
                f"Based on the current temperature of {weather['temperature']}°C in {location}, "
                "here's what you should wear:"
            ]
            
            for category, items in recommendations.items():
                if items:
                    category_name = category.replace('_', ' ').title()
                    items_str = ', '.join(items)
                    response.append(f"{category_name}: {items_str}")

            return '\n'.join(response)

        except Exception as e:
            logger.error(f"Error in ClothingTool: {e}")
            return "Sorry, I encountered an error getting clothing recommendations."
```

### Step 4: Orchestration

The AgentOrchestrator manages the interaction flow:

```python
# src/orchestrator.py
class AgentOrchestrator:
    def __init__(self, agents: list[Agent]):
        self.agents = agents
        self.memory = []  # Stores recent interactions
        self.max_memory = 10
        self.location = None  # Current location
        self.location_utils = LocationUtils()
        
    def get_location(self, user_input: str) -> str:
        # First check if we already have a location
        if self.location:
            return self.location

        # If location is in the input, validate it
        if "in" in user_input:
            try:
                location = user_input.split("in")[1].strip().split()[0].strip(",.!?")
                if self.location_utils.validate_and_normalize_location(location):
                    self.location = location
                    return location
            except:
                pass

        # Ask user for location
        print("I'd love to help! Could you tell me which city you're in?")
        while True:
            location = input("> ").strip()
            if self.location_utils.validate_and_normalize_location(location):
                self.location = location
                return location
            print("I'm having trouble finding that location. Could you try again?")
```

## Testing and Validation

We implement comprehensive testing for each component:

```python
# src/tests/unit/test_weather.py
class TestWeatherTool(unittest.TestCase):
    def setUp(self):
        self.weather_tool = WeatherTool()
        self.test_locations = [
            "New York, US",      # Major city
            "London, UK",        # International city
            "Tokyo, Japan",      # International city with different timezone
            "Invalid Location"   # Invalid location
        ]

    def test_valid_locations(self):
        """Test weather information for valid locations."""
        for location in self.test_locations[:-1]:
            with self.subTest(location=location):
                result = self.weather_tool.use(location)
                self.assertIsNotNone(result)
                self.assertNotIn("Sorry", result)
                self.assertIn("Weather in", result)
                self.assertIn("Temperature:", result)
                self.assertIn("Conditions:", result)
```

## Future Enhancements

Potential improvements include:
1. User preference learning
2. Style recommendations
3. Special occasion handling
4. Integration with calendar events
5. Multi-day forecasting
6. Personalized clothing inventory management
7. Integration with e-commerce platforms
8. Social sharing features

## Conclusion

This implementation demonstrates how to build a sophisticated AI personal assistant that provides contextual clothing recommendations. The modular architecture allows for easy extensions and maintenance while providing robust functionality.

The key strengths of this implementation include:
- Robust error handling and validation
- Efficient caching mechanisms
- Comprehensive weather data processing
- Natural language responses
- Extensible agent architecture

For the complete implementation and more details, check out the full source code in the repository. 