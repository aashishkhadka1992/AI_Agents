"""Location utilities for handling and validating location data."""

import requests
import logging
from typing import Optional, Dict, Any
from utils.error_handler import LocationError

logger = logging.getLogger(__name__)

class LocationUtils:
    """Utility class for location operations."""
    
    def __init__(self):
        """Initialize location utilities."""
        self.cache = {}  # Simple in-memory cache
        self.geocoding_api = "https://geocoding-api.open-meteo.com/v1/search"
        self.country_codes = {
            'US': 'United States',
            'UK': 'United Kingdom',
            'UAE': 'United Arab Emirates',
            # Add more common codes as needed
        }
        
    def _normalize_country_code(self, location: str) -> str:
        """Convert common country codes to full names."""
        if ',' not in location:
            return location
            
        city, country = [part.strip() for part in location.split(',', 1)]
        country = self.country_codes.get(country, country)
        return f"{city}, {country}"
        
    def validate_and_normalize_location(self, location: str) -> bool:
        """Validate location and normalize its format.
        
        Args:
            location (str): Location string to validate
            
        Returns:
            bool: True if location is valid
            
        Raises:
            LocationError: If location is invalid or API call fails
        """
        try:
            # Check cache first
            if location in self.cache:
                return True
                
            # Clean location string
            location = location.strip()
            if not location:
                raise LocationError("Location cannot be empty")
                
            # Normalize country codes
            normalized_location = self._normalize_country_code(location)
                
            # Query geocoding API
            params = {
                "name": normalized_location,
                "count": 1
            }
            
            response = requests.get(self.geocoding_api, params=params)
            response.raise_for_status()
            
            data = response.json()
            if not data.get("results"):
                # Try with just the city name
                if ',' in location:
                    city = location.split(',')[0].strip()
                    params["name"] = city
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
            
        except requests.exceptions.RequestException as e:
            raise LocationError(
                message="Failed to validate location",
                location=location,
                details={"error": str(e)}
            )
        except Exception as e:
            raise LocationError(
                message=f"Error validating location: {str(e)}",
                location=location
            )
            
    def get_location_info(self, location: str) -> Dict[str, Any]:
        """Get detailed information about a location.
        
        Args:
            location (str): Location string
            
        Returns:
            dict: Location information including coordinates
            
        Raises:
            LocationError: If location is invalid or not found
        """
        try:
            # Validate and get from cache if available
            self.validate_and_normalize_location(location)
            if location in self.cache:
                return self.cache[location]
                
            raise LocationError(
                message="Location not found in cache",
                location=location
            )
            
        except Exception as e:
            raise LocationError(
                message=f"Error getting location info: {str(e)}",
                location=location
            )
            
    def clear_cache(self) -> None:
        """Clear the location cache."""
        self.cache = {} 