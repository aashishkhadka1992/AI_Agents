import unittest
import logging
from tools.time_tool import TimeTool

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

class TestTimeTool(unittest.TestCase):
    def setUp(self):
        self.time_tool = TimeTool()
        self.test_locations = [
            "New York, US",      # EST timezone
            "London, UK",        # GMT timezone
            "Tokyo, Japan",      # JST timezone
            "Invalid Location"   # Invalid location
        ]

    def test_valid_locations(self):
        """Test time information for valid locations."""
        for location in self.test_locations[:-1]:  # Exclude invalid location
            with self.subTest(location=location):
                result = self.time_tool.use(location)
                self.assertIsNotNone(result)
                self.assertNotIn("Sorry", result)
                self.assertIn("current time in", result)
                self.assertIn(":", result)  # Time separator
                self.assertIn("M", result)  # AM/PM indicator

    def test_invalid_location(self):
        """Test time information for invalid location."""
        result = self.time_tool.use(self.test_locations[-1])
        self.assertIn("Sorry", result)
        self.assertIn("couldn't find the location", result)

    def test_timezone_info(self):
        """Test timezone information is included."""
        result = self.time_tool.use("New York")
        self.assertIn("America/New_York", result)

    def test_response_format(self):
        """Test time response format."""
        result = self.time_tool.use("London")
        self.assertRegex(result, r"The current time in .+ is \d{1,2}:\d{2} [AP]M \(.+\)")

if __name__ == '__main__':
    unittest.main() 