import unittest
from unittest.mock import patch, MagicMock
import requests
from utils.location_utils import LocationUtils
from utils.error_handler import LocationError

class TestLocationUtils(unittest.TestCase):
    """Test cases for LocationUtils class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.location_utils = LocationUtils()
        self.test_location = "New York"
        self.test_response = {
            "results": [{
                "name": "New York City",
                "latitude": 40.7128,
                "longitude": -74.0060,
                "country": "United States"
            }]
        }

    @patch('requests.get')
    def test_validate_valid_location(self, mock_get):
        """Test location validation with valid location."""
        # Mock API response
        mock_response = MagicMock()
        mock_response.json.return_value = self.test_response
        mock_get.return_value = mock_response
        
        # Test validation
        result = self.location_utils.validate_and_normalize_location(self.test_location)
        self.assertTrue(result)
        self.assertIn(self.test_location, self.location_utils.cache)

    @patch('requests.get')
    def test_validate_invalid_location(self, mock_get):
        """Test location validation with invalid location."""
        # Mock API response for invalid location
        mock_response = MagicMock()
        mock_response.json.return_value = {"results": []}
        mock_get.return_value = mock_response
        
        # Test validation
        with self.assertRaises(LocationError):
            self.location_utils.validate_and_normalize_location("InvalidCity123")

    def test_validate_empty_location(self):
        """Test location validation with empty string."""
        with self.assertRaises(LocationError):
            self.location_utils.validate_and_normalize_location("")

    @patch('requests.get')
    def test_api_error_handling(self, mock_get):
        """Test handling of API errors."""
        # Mock API error
        mock_get.side_effect = requests.exceptions.RequestException("API Error")
        
        # Test error handling
        with self.assertRaises(LocationError) as context:
            self.location_utils.validate_and_normalize_location(self.test_location)
        self.assertIn("Failed to validate location", str(context.exception))

    def test_cache_functionality(self):
        """Test location caching."""
        # Add location to cache
        self.location_utils.cache[self.test_location] = self.test_response["results"][0]
        
        # Test validation uses cache
        result = self.location_utils.validate_and_normalize_location(self.test_location)
        self.assertTrue(result)

    def test_get_location_info(self):
        """Test getting location information."""
        # Add location to cache
        cached_info = self.test_response["results"][0]
        self.location_utils.cache[self.test_location] = cached_info
        
        # Test getting info
        result = self.location_utils.get_location_info(self.test_location)
        self.assertEqual(result, cached_info)

    def test_get_location_info_not_found(self):
        """Test getting information for non-existent location."""
        with self.assertRaises(LocationError):
            self.location_utils.get_location_info("NonExistentCity")

    def test_clear_cache(self):
        """Test cache clearing."""
        # Add location to cache
        self.location_utils.cache[self.test_location] = self.test_response["results"][0]
        
        # Clear cache
        self.location_utils.clear_cache()
        self.assertEqual(len(self.location_utils.cache), 0)

    @patch('requests.get')
    def test_location_normalization(self, mock_get):
        """Test location string normalization."""
        # Mock API response
        mock_response = MagicMock()
        mock_response.json.return_value = self.test_response
        mock_get.return_value = mock_response
        
        # Test with extra whitespace
        result = self.location_utils.validate_and_normalize_location("  New York  ")
        self.assertTrue(result)
        self.assertIn("New York", self.location_utils.cache)

if __name__ == '__main__':
    unittest.main() 