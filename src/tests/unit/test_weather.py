import unittest
import logging
from tools.weather_tool import WeatherTool

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

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
        for location in self.test_locations[:-1]:  # Exclude invalid location
            with self.subTest(location=location):
                result = self.weather_tool.use(location)
                self.assertIsNotNone(result)
                self.assertNotIn("Sorry", result)
                self.assertIn("Weather in", result)
                self.assertIn("Temperature:", result)
                self.assertIn("Conditions:", result)
                self.assertIn("Humidity:", result)
                self.assertIn("Wind Speed:", result)

    def test_invalid_location(self):
        """Test weather information for invalid location."""
        result = self.weather_tool.use(self.test_locations[-1])
        self.assertIn("Sorry", result)
        self.assertIn("couldn't find the location", result)

    def test_response_format(self):
        """Test weather response contains all required fields."""
        result = self.weather_tool.use("New York")
        required_fields = [
            "Temperature:",
            "Conditions:",
            "Humidity:",
            "Wind Speed:"
        ]
        for field in required_fields:
            with self.subTest(field=field):
                self.assertIn(field, result)

    def test_weather_codes(self):
        """Test weather code descriptions are properly defined."""
        tool = WeatherTool()
        self.assertIsNotNone(tool.weather_codes)
        self.assertGreater(len(tool.weather_codes), 0)
        self.assertIn(0, tool.weather_codes)  # Clear sky
        self.assertIn(95, tool.weather_codes)  # Thunderstorm

if __name__ == '__main__':
    unittest.main() 