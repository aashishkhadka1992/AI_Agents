# Building an AI-Powered Personal Assistant

In this hands-on tutorial, we'll build a sophisticated AI personal assistant using an agent-based architecture. The system uses multiple specialized agents coordinated by an orchestrator to provide various services, starting with weather-based clothing recommendations.

## Architecture Overview

Our personal assistant uses a layered architecture:
```
┌─────────────────────────────────────┐
│            Orchestrator             │
│  (Manages agents and conversation)  │
├─────────────┬─────────────┬────────┤
│  Weather    │    Time     │Clothing│
│   Agent     │    Agent    │ Agent  │
├─────────────┼─────────────┼────────┤
│  Weather    │    Time     │Clothing│
│   Tool      │    Tool     │  Tool  │
└─────────────┴─────────────┴────────┘
```

### Key Components:
1. **Agents**: Specialized modules that handle specific tasks
2. **Tools**: Underlying implementations that agents use
3. **Orchestrator**: Coordinates agents and manages conversation flow
4. **Utilities**: Shared functionality like location handling and error management

## Getting Started

1. Create a new project directory and set up a virtual environment:
```bash
mkdir personal-assistant
cd personal-assistant
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install requests pytz
```

2. Create the project structure:
```
personal-assistant/
├── src/
│   ├── agents/
│   │   ├── __init__.py
│   │   └── base_agent.py
│   ├── tools/
│   │   ├── __init__.py
│   │   ├── base_tool.py
│   │   ├── weather_tool.py
│   │   ├── time_tool.py
│   │   └── clothing_tool.py
│   ├── utils/
│   │   ├── __init__.py
│   │   ├── location_utils.py
│   │   └── error_handler.py
│   ├── orchestrator.py
│   └── main.py
└── requirements.txt
```

## Phase 1: Foundation

Let's start by implementing the base classes and error handling.

### 1. Error Handler

First, create the error handling utilities:

```python
# src/utils/error_handler.py
import logging
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)

class AgentError(Exception):
    """Base exception for agent-related errors."""
    def __init__(self, message: str, agent_name: Optional[str] = None, details: Optional[Dict[str, Any]] = None):
        self.message = message
        self.agent_name = agent_name
        self.details = details or {}
        super().__init__(self.message)
        
        # Log the error
        logger.error(f"Agent Error [{agent_name or 'Unknown'}]: {message}")
        if details:
            logger.debug(f"Error details: {details}")

class ToolError(Exception):
    """Base exception for tool-related errors."""
    def __init__(self, message: str, tool_name: Optional[str] = None, details: Optional[Dict[str, Any]] = None):
        self.message = message
        self.tool_name = tool_name
        self.details = details or {}
        super().__init__(self.message)
        
        # Log the error
        logger.error(f"Tool Error [{tool_name or 'Unknown'}]: {message}")
        if details:
            logger.debug(f"Error details: {details}")

class LocationError(Exception):
    """Exception for location-related errors."""
    def __init__(self, message: str, location: Optional[str] = None, details: Optional[Dict[str, Any]] = None):
        self.message = message
        self.location = location
        self.details = details or {}
        super().__init__(self.message)
        
        # Log the error
        logger.error(f"Location Error [{location or 'Unknown'}]: {message}")
        if details:
            logger.debug(f"Error details: {details}")

class OrchestratorError(Exception):
    """Exception for orchestrator-related errors."""
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        self.message = message
        self.details = details or {}
        super().__init__(self.message)
        
        # Log the error
        logger.error(f"Orchestrator Error: {message}")
        if details:
            logger.debug(f"Error details: {details}")

class LLMError(Exception):
    """Exception for LLM-related errors."""
    def __init__(self, message: str, model: Optional[str] = None, details: Optional[Dict[str, Any]] = None):
        self.message = message
        self.model = model
        self.details = details or {}
        super().__init__(self.message)
        
        # Log the error
        logger.error(f"LLM Error [{model or 'Unknown'}]: {message}")
        if details:
            logger.debug(f"Error details: {details}")

def handle_agent_error(func):
    """Decorator for handling agent-related errors."""
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except AgentError as e:
            logger.error(f"Agent operation failed: {str(e)}")
            return {"action": "respond_to_user", "input": f"I encountered an error: {str(e)}"}
        except Exception as e:
            logger.error(f"Unexpected error in agent operation: {str(e)}")
            return {"action": "respond_to_user", "input": "I encountered an unexpected error."}
    return wrapper

def handle_tool_error(func):
    """Decorator for handling tool-related errors."""
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except ToolError as e:
            logger.error(f"Tool operation failed: {str(e)}")
            return f"Tool error: {str(e)}"
        except Exception as e:
            logger.error(f"Unexpected error in tool operation: {str(e)}")
            return "Tool encountered an unexpected error."
    return wrapper

def format_error_response(error: Exception) -> Dict[str, str]:
    """Format error into a user-friendly response."""
    if isinstance(error, LocationError):
        return {
            "action": "respond_to_user",
            "input": f"I couldn't find that location. Please try another city or check the spelling."
        }
    elif isinstance(error, ToolError):
        return {
            "action": "respond_to_user",
            "input": f"I had trouble getting that information. {str(error)}"
        }
    elif isinstance(error, LLMError):
        return {
            "action": "respond_to_user",
            "input": "I'm having trouble processing your request. Please try again in a moment."
        }
    else:
        return {
            "action": "respond_to_user",
            "input": "I encountered an unexpected error. Please try again."
        }

def log_error(error: Exception, context: Optional[Dict[str, Any]] = None) -> None:
    """Log error with additional context."""
    error_type = type(error).__name__
    error_msg = str(error)
    
    if context:
        logger.error(f"{error_type}: {error_msg} | Context: {context}")
    else:
        logger.error(f"{error_type}: {error_msg}")
        
    if hasattr(error, 'details') and error.details:
        logger.debug(f"Error details: {error.details}")
```

This error handling system provides:
- Specialized error classes for different types of errors (Agent, Tool, Location, Orchestrator, LLM)
- Detailed error logging with context and debug information
- Error handling decorators for agents and tools
- User-friendly error response formatting
- Centralized error logging utility

Each error class includes:
- Custom message
- Optional component-specific information (e.g., agent_name, tool_name, location)
- Optional details dictionary for additional context
- Automatic error logging with appropriate severity levels

The utility functions help with:
- Consistent error handling across the application
- Converting errors to user-friendly responses
- Proper error logging with context
- Decorators for standardized error handling in agents and tools

### 2. Base Tool

Next, create the base tool class that all tools will inherit from:

```python
# src/tools/base_tool.py
from abc import ABC, abstractmethod
import logging
from utils.location_utils import LocationUtils

logger = logging.getLogger(__name__)

class BaseTool(ABC):
    """Base class for all tools."""
    
    def __init__(self):
        """Initialize the tool with LocationUtils if needed."""
        self.location_utils = LocationUtils()

    @abstractmethod
    def name(self) -> str:
        """Return the name of the tool."""
        pass

    @abstractmethod
    def description(self) -> str:
        """Return a description of what the tool does."""
        pass

    @abstractmethod
    def use(self, *args, **kwargs) -> str:
        """Execute the tool's main functionality."""
        pass
```

### 3. Base Agent

Create the base agent class:

```python
# src/agents/base_agent.py
from abc import ABC, abstractmethod
import ast
import json
import logging
from typing import Union, Dict
from llm.llm_ops import query_llm
from tools.base_tool import BaseTool

logger = logging.getLogger(__name__)

class Agent:
    """Base agent class that handles tool selection and execution.
    
    This class provides the foundation for specialized agents by managing:
    - Tool selection and execution
    - Conversation memory
    - Input processing
    - Response formatting
    """

    def __init__(self, Name: str, Description: str, Tools: list, Model: str):
        """Initialize the agent with required components.
        
        Args:
            Name (str): Name of the agent
            Description (str): Description of agent's capabilities
            Tools (list): List of available tools
            Model (str): LLM model to use for processing
        """
        self.memory = []
        self.name = Name
        self.description = Description
        self.tools = Tools
        self.model = Model
        self.max_memory = 10
        logger.debug(f"Initialized {self.name} agent with model {self.model}")

    def json_parser(self, input_string):
        """Parse string input into JSON/dict format."""
        try:
            logger.debug(f"Parsing input string: {input_string}")
            if isinstance(input_string, (dict, list)):
                return input_string

            python_dict = ast.literal_eval(input_string)
            json_string = json.dumps(python_dict)
            json_dict = json.loads(json_string)

            if isinstance(json_dict, (dict, list)):
                return json_dict

            raise ValueError("Invalid JSON response")
        except Exception as e:
            logger.error(f"Error parsing JSON: {str(e)}")
            raise

    def process_input(self, user_input):
        """Process user input and determine appropriate action.
        
        This method:
        1. Updates conversation memory
        2. Determines if a tool should be used
        3. Executes the appropriate tool or returns direct response
        """
        try:
            self.memory.append(f"User: {user_input}")
            if len(self.memory) > self.max_memory:
                self.memory.pop(0)

            context = "\n".join(self.memory)
            tool_descriptions = "\n".join([f"- {tool.name()}: {tool.description()}" for tool in self.tools])
            response_format = {"action":"", "args":""}

            prompt = f"""Context:
            {context}

            Available tools:
            {tool_descriptions}

            Based on the user's input and context, decide if you should use a tool or respond directly.        
            If you identify a action, respond with the tool name and the arguments for the tool.        
            If you decide to respond directly to the user then make the action "respond_to_user" with args as your response in the following format.

            Response Format:
            {response_format}
            """

            logger.debug(f"Sending prompt to LLM: {prompt}")
            response = query_llm(prompt)
            logger.debug(f"Received response from LLM: {response}")
            
            self.memory.append(f"Agent: {response}")

            response_dict = self.json_parser(response)

            # Check if any tool can handle the input
            for tool in self.tools:
                if tool.name().lower() == response_dict["action"].lower():
                    logger.debug(f"Using tool: {tool.name()} with args: {response_dict['args']}")
                    return tool.use(response_dict["args"])

            return response_dict
        except Exception as e:
            logger.error(f"Error processing input: {str(e)}")
            raise

    def use_tool(self, tool_name: str, args: Union[str, Dict]) -> str:
        """Execute a specific tool with given arguments."""
        try:
            tool = self.tools.get(tool_name)
            if not tool:
                return f"Tool {tool_name} not found"

            # If args is a dictionary, extract the location value
            if isinstance(args, dict) and 'location' in args:
                args = args['location']
            elif isinstance(args, dict):
                # If no location in dict, convert the first value to string
                args = str(next(iter(args.values())))

            return tool.use(args)

        except Exception as e:
            logging.error(f"Error using tool {tool_name}: {str(e)}")
            return f"Error using tool {tool_name}"
```

This base agent class provides:
- Conversation memory management with a maximum history size
- JSON parsing for structured communication
- LLM-based tool selection
- Flexible tool execution with both string and dictionary arguments
- Comprehensive error handling and logging
- Context-aware processing through memory of past interactions

The agent can:
- Maintain a conversation history
- Parse and validate JSON responses
- Select appropriate tools based on user input
- Execute tools with proper argument handling
- Handle errors gracefully with detailed logging
- Provide consistent response formatting

This completes Phase 1 of our implementation. In the next phase, we'll implement the core tools (Weather, Time, and Clothing) that our agents will use.

## Phase 2: Core Tools

Now that we have our foundation in place, let's implement the core tools our agents will use.

### 1. Location Utilities

First, let's create the location handling utility that all tools will share:

```python
# src/utils/location_utils.py
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
```

This location utility provides:
- Location validation and normalization
- Country code standardization
- Geocoding using the Open-Meteo API
- In-memory caching for performance
- Comprehensive error handling
- Detailed location information retrieval

Key features:
1. **Caching**: Stores validated locations to reduce API calls
2. **Country Code Normalization**: Converts common codes (US, UK) to full names
3. **Flexible Validation**: Tries both full location and city-only searches
4. **Error Handling**: Provides detailed error information with context
5. **Clean API**: Simple interface for validation and information retrieval

The utility is used by all tools that need location information, ensuring consistent handling of:
- Location validation
- Geocoding
- Error handling
- Cache management

### 2. Weather Tool

Next, let's implement the weather tool that fetches and processes weather data:

```python
# src/tools/weather_tool.py
import requests
import logging
from datetime import datetime
import pytz
from tools.base_tool import BaseTool
from utils.error_handler import LocationError

logger = logging.getLogger(__name__)

class WeatherTool(BaseTool):
    def __init__(self):
        super().__init__()
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
```

### 3. Time Tool

Now let's implement the time tool for handling timezone-aware time information:

```python
# src/tools/time_tool.py
import requests
import logging
from datetime import datetime
import pytz
from tools.base_tool import BaseTool

logger = logging.getLogger(__name__)

class TimeTool(BaseTool):
    def __init__(self):
        super().__init__()

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

    def use(self, location) -> str:
        """Get current time for a location."""
        try:
            # Handle dictionary input
            if isinstance(location, dict):
                location = location.get('location', '')
            
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
```

This time tool provides:
- Direct timezone lookup using the Open-Meteo Geocoding API
- Proper error handling and logging
- Support for both string and dictionary inputs
- Clean response formatting with location name and timezone
- Integration with the `pytz` library for accurate timezone conversions

Key features:
1. **Direct API Integration**: Uses Open-Meteo Geocoding API for timezone lookup
2. **Error Management**: Comprehensive error handling with proper logging
3. **Flexible Input**: Supports both string and dictionary inputs
4. **Clean Output**: Provides formatted responses with location name and timezone
5. **Timezone Accuracy**: Uses `pytz` for reliable timezone conversions

The tool follows the same pattern as other tools in the system:
- Inherits from `BaseTool` for consistent behavior
- Provides detailed logging for debugging
- Returns user-friendly error messages
- Handles location lookup and timezone conversion

### 4. Clothing Tool

Finally, let's implement the clothing recommendation tool:

```python
# src/tools/clothing_tool.py
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
```

This clothing tool provides:
- Temperature-based clothing recommendations with five distinct ranges
- Weather condition adjustments for rain, snow, and wind
- Integration with the Open-Meteo API for weather data
- Proper error handling and logging
- Support for both string and dictionary inputs
- Clean response formatting with categorized recommendations

Key features:
1. **Comprehensive Recommendations**: Pre-defined clothing suggestions for different temperature ranges
2. **Weather Adaptability**: Adjusts recommendations based on precipitation and wind conditions
3. **Location Integration**: Uses LocationUtils for consistent location handling
4. **Error Management**: Comprehensive error handling with proper logging
5. **Clean Output**: Provides formatted responses with categorized clothing recommendations

The tool follows the same pattern as other tools in the system:
- Inherits from `BaseTool` for consistent behavior
- Uses shared utilities for location handling
- Provides detailed logging for debugging
- Returns user-friendly error messages
- Handles both weather data fetching and recommendation logic

This completes Phase 2 of our implementation. We now have all the core tools ready:
- LocationUtils for handling location validation and geocoding
- WeatherTool for fetching current weather conditions
- TimeTool for providing timezone-aware time information
- ClothingTool for generating weather-appropriate clothing recommendations

Each tool follows our base class interface and includes proper error handling and logging. In the next phase, we'll implement the agent system that will use these tools.

## Phase 3: Agents & Orchestration

Now that we have our core tools in place, let's implement the agent system that will use these tools and the orchestrator that will coordinate them.

### 1. Specialized Agents

First, let's create our specialized agents that will use the tools we built:

```python
# src/agents/weather_agent.py
from typing import Dict, Any
from agents.base_agent import Agent
from tools.weather_tool import WeatherTool

class WeatherAgent(Agent):
    def __init__(self):
        super().__init__(
            Name="Weather Agent",
            Description="Provides weather information for locations",
            Tools=[WeatherTool()],
            Model="gpt-4o"  # Using OpenAI's GPT-4 for processing
        )

    def process_input(self, user_input: str, context: Dict[str, Any] = None) -> str:
        """Process weather-related queries."""
        try:
            # Extract location from input or context
            location = context.get('location') if context else None
            if not location:
                # Simple location extraction - in production, use NLP
                location = user_input.strip()
            
            # Use weather tool
            return self.use_tool("Weather Agent", location)
        except Exception as e:
            return f"I couldn't get the weather information: {str(e)}"
```

```python
# src/agents/time_agent.py
from typing import Dict, Any
from agents.base_agent import Agent
from tools.time_tool import TimeTool

class TimeAgent(Agent):
    def __init__(self):
        super().__init__(
            Name="Time Agent",
            Description="Provides time information for locations",
            Tools=[TimeTool()],
            Model="gpt-4o"
        )

    def process_input(self, user_input: str, context: Dict[str, Any] = None) -> str:
        """Process time-related queries."""
        try:
            location = context.get('location') if context else None
            if not location:
                location = user_input.strip()
            
            return self.use_tool("Time Agent", location)
        except Exception as e:
            return f"I couldn't get the time information: {str(e)}"
```

```python
# src/agents/clothing_agent.py
from typing import Dict, Any
from agents.base_agent import Agent
from tools.clothing_tool import ClothingTool

class ClothingAgent(Agent):
    def __init__(self):
        super().__init__(
            Name="Clothing Agent",
            Description="Provides clothing recommendations based on weather",
            Tools=[ClothingTool()],
            Model="gpt-4o"
        )

    def process_input(self, user_input: str, context: Dict[str, Any] = None) -> str:
        """Process clothing recommendation queries."""
        try:
            location = context.get('location') if context else None
            if not location:
                location = user_input.strip()
            
            return self.use_tool("Clothing Agent", location)
        except Exception as e:
            return f"I couldn't get clothing recommendations: {str(e)}"
```

### 2. Conversation Context

Let's create a context manager to maintain conversation state:

```python
# src/utils/context_manager.py
from typing import Dict, Any, Optional
import logging
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class ConversationContext:
    def __init__(self):
        self.context: Dict[str, Any] = {}
        self.last_update = datetime.now()
        self.expiry_time = timedelta(minutes=30)

    def update(self, key: str, value: Any) -> None:
        """Update context with new information."""
        self.context[key] = value
        self.last_update = datetime.now()
        logger.debug(f"Updated context: {key}={value}")

    def get(self, key: str) -> Optional[Any]:
        """Get value from context if not expired."""
        if self.is_expired():
            self.clear()
            return None
        return self.context.get(key)

    def is_expired(self) -> bool:
        """Check if context has expired."""
        return datetime.now() - self.last_update > self.expiry_time

    def clear(self) -> None:
        """Clear expired context."""
        self.context.clear()
        self.last_update = datetime.now()
        logger.debug("Cleared conversation context")
```

### 3. Agent Orchestrator

Now, let's implement the orchestrator that will coordinate our agents:

```python
# src/orchestrator.py
import logging
from typing import Dict, List, Any
from agents.base_agent import Agent
from agents.weather_agent import WeatherAgent
from agents.time_agent import TimeAgent
from agents.clothing_agent import ClothingAgent
from utils.context_manager import ConversationContext
from utils.error_handler import BaseError

logger = logging.getLogger(__name__)

class Orchestrator:
    """Coordinates agents and manages conversation flow."""
    
    def __init__(self):
        """Initialize orchestrator with available agents."""
        self.agents: Dict[str, Agent] = {
            'weather': WeatherAgent(),
            'time': TimeAgent(),
            'clothing': ClothingAgent()
        }
        self.context = ConversationContext()
        logger.info(f"Initialized orchestrator with {len(self.agents)} agents")

    def _determine_intent(self, user_input: str) -> List[str]:
        """Determine which agents should handle the input.
        
        In a production system, this would use a more sophisticated
        NLP model to determine intent. For this tutorial, we use
        simple keyword matching.
        """
        intents = []
        input_lower = user_input.lower()
        
        # Simple keyword matching
        if any(word in input_lower for word in ['weather', 'temperature', 'rain', 'sunny']):
            intents.append('weather')
        
        if any(word in input_lower for word in ['time', 'hour', 'clock']):
            intents.append('time')
        
        if any(word in input_lower for word in ['wear', 'clothes', 'dress', 'outfit']):
            intents.append('clothing')
            
        # If no specific intent is found, assume weather+clothing
        if not intents:
            intents = ['weather', 'clothing']
            
        return intents

    def _extract_location(self, user_input: str) -> str:
        """Extract location from user input.
        
        In a production system, this would use NLP for entity extraction.
        For this tutorial, we use a simple approach.
        """
        # First check context
        location = self.context.get('location')
        if location:
            return location
            
        # Simple location extraction - last word or phrase
        words = user_input.split()
        if 'in' in words:
            idx = words.index('in')
            if idx + 1 < len(words):
                return ' '.join(words[idx + 1:])
        
        # Default to last word if no location found
        return words[-1]

    def process_input(self, user_input: str) -> str:
        """Process user input and coordinate agent responses."""
        try:
            # Determine intent
            intents = self._determine_intent(user_input)
            if not intents:
                return "I'm not sure how to help with that. Try asking about weather, time, or clothing recommendations."
            
            # Extract location
            location = self._extract_location(user_input)
            self.context.update('location', location)
            
            # Get responses from relevant agents
            responses = []
            for intent in intents:
                agent = self.agents.get(intent)
                if agent:
                    response = agent.process_input(
                        user_input,
                        context={'location': location}
                    )
                    responses.append(response)
            
            # Combine responses
            return '\n\n'.join(responses)
            
        except BaseError as e:
            logger.error(f"Error processing input: {e}")
            return f"Sorry, I encountered an error: {e.message}"
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            return "I apologize, but I encountered an unexpected error. Please try again."
```

### 4. Main Application

Finally, let's create the main application that ties everything together:

```python
# src/main.py
import logging
from orchestrator import Orchestrator

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

def main():
    """Run the personal assistant."""
    print("AI Personal Assistant")
    print("Ask me about weather, time, or clothing recommendations!")
    print("Type 'quit' to exit.")
    
    orchestrator = Orchestrator()
    
    while True:
        try:
            # Get user input
            user_input = input("\nYou: ").strip()
            if user_input.lower() in ['quit', 'exit']:
                break
            
            # Process input and get response
            response = orchestrator.process_input(user_input)
            print("\nAssistant:", response)
            
        except KeyboardInterrupt:
            break
        except Exception as e:
            print(f"\nError: {str(e)}")
            print("Please try again.")
    
    print("\nGoodbye!")

if __name__ == "__main__":
    main()
```

This completes Phase 3 of our implementation. We now have:
1. Specialized agents for weather, time, and clothing recommendations
2. A context manager for maintaining conversation state
3. An orchestrator that coordinates agents and manages conversation flow
4. A main application that brings everything together

The system can now:
- Process natural language inputs
- Maintain conversation context
- Route requests to appropriate agents
- Combine responses from multiple agents
- Handle errors gracefully
- Provide logging for debugging

In the final phase, we'll add example interactions, testing, and deployment instructions.

## Phase 4: Examples, Testing, and Deployment

Let's complete our personal assistant implementation with examples, tests, and deployment instructions.

### 1. Example Interactions

Here are some example interactions with our personal assistant:

```text
You: What's the weather like in London?
Assistant: Weather in London, United Kingdom at 02:30 PM:
Temperature: 18°C (feels like 17°C)
Conditions: partly cloudy
Humidity: 65%
Wind Speed: 12 km/h

You: What should I wear?
Assistant: Based on the current temperature of 18°C in London, United Kingdom, here's what you should wear:
Base: Long-sleeve shirt
Mid: Light jacket
Bottom: Regular pants, Jeans
Accessories: Light scarf

You: What time is it in Tokyo?
Assistant: The current time in Tokyo, Japan is 10:30 PM (Asia/Tokyo)

You: How about the weather and clothing in New York?
Assistant: Weather in New York, United States at 03:30 PM:
Temperature: 22°C (feels like 23°C)
Conditions: mainly clear
Humidity: 55%
Wind Speed: 8 km/h

Based on the current temperature of 22°C in New York, United States, here's what you should wear:
Base: T-shirt, Short-sleeve shirt
Bottom: Light pants, Shorts
Accessories: Sunglasses
```

### 2. Testing

Let's add unit tests for our components:

```python
# tests/test_location_utils.py
import unittest
from unittest.mock import patch, MagicMock
from src.utils.location_utils import LocationUtils
from src.utils.error_handler import LocationError

class TestLocationUtils(unittest.TestCase):
    def setUp(self):
        self.location_utils = LocationUtils()

    def test_normalize_country_code(self):
        self.assertEqual(
            self.location_utils._normalize_country_code("London, UK"),
            "London, United Kingdom"
        )
        self.assertEqual(
            self.location_utils._normalize_country_code("New York, US"),
            "New York, United States"
        )

    @patch('requests.get')
    def test_validate_location_success(self, mock_get):
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "results": [{
                "name": "London",
                "country": "United Kingdom",
                "latitude": 51.5074,
                "longitude": -0.1278
            }]
        }
        mock_get.return_value = mock_response

        self.assertTrue(
            self.location_utils.validate_and_normalize_location("London, UK")
        )

    @patch('requests.get')
    def test_validate_location_failure(self, mock_get):
        mock_response = MagicMock()
        mock_response.json.return_value = {"results": []}
        mock_get.return_value = mock_response

        with self.assertRaises(LocationError):
            self.location_utils.validate_and_normalize_location("NonexistentCity")
```

```python
# tests/test_weather_tool.py
import unittest
from unittest.mock import patch, MagicMock
from src.tools.weather_tool import WeatherTool

class TestWeatherTool(unittest.TestCase):
    def setUp(self):
        self.weather_tool = WeatherTool()

    def test_get_temperature_range(self):
        self.assertEqual(
            self.weather_tool._get_temperature_range(-5),
            'very_cold'
        )
        self.assertEqual(
            self.weather_tool._get_temperature_range(15),
            'mild'
        )
        self.assertEqual(
            self.weather_tool._get_temperature_range(28),
            'hot'
        )

    @patch('src.tools.weather_tool.requests.get')
    def test_get_weather_data(self, mock_get):
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "current": {
                "temperature_2m": 20,
                "relative_humidity_2m": 65,
                "apparent_temperature": 21,
                "precipitation": 0,
                "weather_code": 1,
                "wind_speed_10m": 10
            },
            "timezone": "Europe/London"
        }
        mock_get.return_value = mock_response

        weather_data = self.weather_tool._get_weather_data(51.5074, -0.1278)
        self.assertEqual(weather_data["temperature"], 20)
        self.assertEqual(weather_data["description"], "mainly clear")
```

To run the tests:

```bash
python -m unittest discover tests
```

### 3. Deployment

To deploy the personal assistant, follow these steps:

1. Set up a production environment:

```bash
# Create a production directory
mkdir personal-assistant-prod
cd personal-assistant-prod

# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install production dependencies
pip install -r requirements.txt
```

2. Create a production configuration file:

```python
# config/production.py
import os

# API Configuration
GEOCODING_API = "https://geocoding-api.open-meteo.com/v1/search"
WEATHER_API = "https://api.open-meteo.com/v1/forecast"

# Logging Configuration
LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
LOG_FILE = 'logs/personal_assistant.log'

# Context Configuration
CONTEXT_EXPIRY_MINUTES = 30

# Model Configuration
DEFAULT_MODEL = "gpt-4o"
```

3. Set up logging:

```python
# src/utils/logger.py
import logging
import os
from logging.handlers import RotatingFileHandler
from config.production import LOG_LEVEL, LOG_FORMAT, LOG_FILE

def setup_logging():
    """Configure logging for production."""
    # Create logs directory if it doesn't exist
    os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)

    # Configure root logger
    logging.basicConfig(
        level=getattr(logging, LOG_LEVEL),
        format=LOG_FORMAT,
        handlers=[
            # Console handler
            logging.StreamHandler(),
            # File handler with rotation
            RotatingFileHandler(
                LOG_FILE,
                maxBytes=10485760,  # 10MB
                backupCount=5
            )
        ]
    )
```

4. Create a startup script:

```bash
#!/bin/bash
# start.sh

# Activate virtual environment
source venv/bin/activate

# Set environment variables
export LOG_LEVEL=INFO

# Start the application
python src/main.py
```

5. Make the startup script executable:

```bash
chmod +x start.sh
```

### 4. Extension Points

The personal assistant is designed to be easily extensible. Here are some ways to extend its functionality:

1. Add New Tools:
```python
# src/tools/news_tool.py
from tools.base_tool import BaseTool

class NewsTool(BaseTool):
    def __init__(self):
        super().__init__()
        # Initialize news API client

    def name(self):
        return "News Tool"

    def description(self):
        return "Provides latest news for a location."

    def use(self, location: str) -> str:
        # Implement news fetching logic
        pass
```

2. Add New Agents:
```python
# src/agents/news_agent.py
from agents.base_agent import Agent
from tools.news_tool import NewsTool

class NewsAgent(Agent):
    def __init__(self):
        super().__init__(
            Name="News Agent",
            Description="Provides local news updates",
            Tools=[NewsTool()],
            Model="gpt-4o"
        )

    def process_input(self, user_input: str, context: dict = None) -> str:
        # Implement news processing logic
        pass
```

3. Enhance Intent Recognition:
```python
# src/utils/intent_recognizer.py
from typing import List
import spacy

class IntentRecognizer:
    def __init__(self):
        self.nlp = spacy.load("en_core_web_sm")
        self.intent_patterns = {
            'weather': ['weather', 'temperature', 'rain', 'forecast'],
            'time': ['time', 'hour', 'clock'],
            'clothing': ['wear', 'clothes', 'dress', 'outfit'],
            'news': ['news', 'headlines', 'updates']
        }

    def recognize(self, text: str) -> List[str]:
        doc = self.nlp(text.lower())
        intents = []
        
        # Use NLP to identify intents
        for intent, patterns in self.intent_patterns.items():
            if any(token.text in patterns for token in doc):
                intents.append(intent)
                
        return intents
```

4. Add Conversation Memory:
```python
# src/utils/memory_manager.py
from typing import Dict, List
import json
from datetime import datetime

class MemoryManager:
    def __init__(self, file_path: str = "data/conversation_history.json"):
        self.file_path = file_path
        self.history: Dict[str, List[Dict]] = self._load_history()

    def _load_history(self) -> Dict:
        try:
            with open(self.file_path, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return {}

    def add_interaction(self, user_id: str, interaction: Dict):
        if user_id not in self.history:
            self.history[user_id] = []
            
        self.history[user_id].append({
            'timestamp': datetime.now().isoformat(),
            **interaction
        })
        self._save_history()

    def _save_history(self):
        with open(self.file_path, 'w') as f:
            json.dump(self.history, f, indent=2)
```

These extension points allow you to:
- Add new capabilities through tools and agents
- Improve natural language understanding
- Add persistent conversation history
- Enhance context management
- Add user authentication and personalization

The modular architecture makes it easy to add new features while maintaining clean separation of concerns.

This completes our tutorial! You now have a fully functional AI personal assistant that can:
- Provide weather information
- Give clothing recommendations
- Tell the time in different locations
- Maintain conversation context
- Handle errors gracefully
- Scale and extend with new capabilities

The system is ready for production use and can be extended with additional features as needed. 