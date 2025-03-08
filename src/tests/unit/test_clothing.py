import unittest
import logging
from tools.clothing_tool import ClothingTool

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

class TestClothingTool(unittest.TestCase):
    def setUp(self):
        self.clothing_tool = ClothingTool()
        self.test_locations = [
            "Miami, US",        # Hot climate
            "Denver, US",       # Variable climate
            "Seattle, US",      # Mild climate
            "Invalid Location"  # Invalid location
        ]

    def test_valid_locations(self):
        """Test clothing recommendations for valid locations."""
        for location in self.test_locations[:-1]:  # Exclude invalid location
            with self.subTest(location=location):
                result = self.clothing_tool.use(location)
                self.assertIsNotNone(result)
                self.assertNotIn("Sorry", result)
                self.assertIn("Based on the current temperature", result)
                self.assertIn("here's what you should wear", result)

    def test_invalid_location(self):
        """Test clothing recommendations for invalid location."""
        result = self.clothing_tool.use(self.test_locations[-1])
        self.assertIn("Sorry", result)
        self.assertIn("couldn't find the location", result)

    def test_recommendation_format(self):
        """Test clothing recommendations contain all required categories."""
        result = self.clothing_tool.use("New York")
        required_categories = [
            "Base:",
            "Bottom:",
            "Accessories:"
        ]
        for category in required_categories:
            with self.subTest(category=category):
                self.assertIn(category, result)

    def test_temperature_ranges(self):
        """Test temperature range categorization."""
        tool = ClothingTool()
        test_temps = [
            (-5, 'very_cold'),
            (5, 'cold'),
            (15, 'mild'),
            (22, 'warm'),
            (30, 'hot')
        ]
        for temp, expected_range in test_temps:
            with self.subTest(temp=temp):
                result = tool._get_temperature_range(temp)
                self.assertEqual(result, expected_range)

    def test_weather_adjustments(self):
        """Test weather condition adjustments to clothing."""
        tool = ClothingTool()
        recommendations = {
            'base': ['T-shirt'],
            'accessories': ['Sunglasses'],
            'outer': []
        }
        
        # Test rain adjustment
        tool._adjust_for_conditions(recommendations, 61, 10)  # Light rain
        self.assertIn('Rain jacket', recommendations['outer'])
        self.assertIn('Umbrella', recommendations['accessories'])
        
        # Test wind adjustment
        recommendations['outer'] = []  # Reset
        tool._adjust_for_conditions(recommendations, 0, 25)  # Strong wind
        self.assertIn('Windbreaker', recommendations['outer'])

if __name__ == '__main__':
    unittest.main() 