import unittest
from unittest.mock import Mock, patch
import json
import os
import sys
from pathlib import Path

# Add src directory to Python path
src_dir = Path(__file__).parent.parent.parent
sys.path.append(str(src_dir))

from orchestrator import AgentOrchestrator
from agents.base_agent import Agent
from tools.weather_tool import WeatherTool
from tools.time_tool import TimeTool
from tools.clothing_tool import ClothingTool

class TestOrchestrator(unittest.TestCase):
    """Integration tests for AgentOrchestrator."""
    
    def setUp(self):
        """Set up test agents and orchestrator."""
        # Create test agents with real tools
        self.weather_agent = Agent(
            Name="Weather Agent",
            Description="Provides weather information",
            Tools=[WeatherTool()],
            Model="gpt-4"
        )
        
        self.time_agent = Agent(
            Name="Time Agent",
            Description="Provides time information",
            Tools=[TimeTool()],
            Model="gpt-4"
        )
        
        self.clothing_agent = Agent(
            Name="Clothing Agent",
            Description="Provides clothing recommendations",
            Tools=[ClothingTool()],
            Model="gpt-4"
        )
        
        # Create orchestrator with test agents
        self.orchestrator = AgentOrchestrator([
            self.weather_agent,
            self.time_agent,
            self.clothing_agent
        ])
        
        # Set a default test location
        self.test_location = "New York"
        self.orchestrator.location = self.test_location

    def test_agent_coordination_summary_request(self):
        """Test that orchestrator properly coordinates multiple agents for summary requests."""
        # Test summary request
        result = self.orchestrator.orchestrate_task("Give me a summary for New York")
        
        # Verify response format
        self.assertIsInstance(result, dict)
        self.assertIn("action", result)
        self.assertIn("input", result)
        self.assertEqual(result["action"], "respond_to_user")
        
        # Verify response content includes information from all agents
        response = result["input"].lower()
        self.assertIn("weather", response)  # Should have weather info
        self.assertIn("time", response)     # Should have time info
        self.assertIn("wear", response)     # Should have clothing info

    def test_agent_selection(self):
        """Test that orchestrator selects the appropriate agent for specific requests."""
        # Test weather request
        weather_result = self.orchestrator.orchestrate_task("What's the weather like in New York?")
        self.assertIn("temperature", weather_result["input"].lower())
        
        # Test time request
        time_result = self.orchestrator.orchestrate_task("What time is it in New York?")
        self.assertIn("time", time_result["input"].lower())
        
        # Test clothing request
        clothing_result = self.orchestrator.orchestrate_task("What should I wear in New York?")
        self.assertIn("wear", clothing_result["input"].lower())

    def test_context_management(self):
        """Test that orchestrator maintains location context between requests."""
        # Set initial location
        self.orchestrator.location = None
        
        # First request sets location
        self.orchestrator.orchestrate_task("What's the weather like in London?")
        self.assertEqual(self.orchestrator.location, "London")
        
        # Second request should use cached location
        result = self.orchestrator.orchestrate_task("What should I wear?")
        self.assertIn("London", str(result))

    def test_invalid_requests(self):
        """Test orchestrator handles invalid requests gracefully."""
        # Test with empty request
        empty_result = self.orchestrator.orchestrate_task("")
        self.assertIn("help", empty_result["input"].lower())
        
        # Test with unsupported request
        invalid_result = self.orchestrator.orchestrate_task("What's the stock price of AAPL?")
        self.assertIn("not sure", invalid_result["input"].lower())

    def test_location_validation(self):
        """Test location validation and error handling."""
        # Enable test mode to prevent interactive prompts
        self.orchestrator._test_mode = True
        
        # Test with invalid location
        result = self.orchestrator.orchestrate_task("What's the weather like in InvalidCity123?")
        self.assertIsInstance(result, dict)
        self.assertIn("action", result)
        self.assertIn("input", result)
        self.assertIn("location", result["input"].lower())
        
        # Test with valid location
        valid_result = self.orchestrator.orchestrate_task("What's the weather like in Tokyo?")
        self.assertIsInstance(valid_result, dict)
        self.assertIn("action", valid_result)
        self.assertIn("input", valid_result)
        self.assertNotIn("couldn't find", valid_result["input"].lower())

    def test_memory_management(self):
        """Test conversation memory management."""
        # Generate multiple requests
        for i in range(12):  # More than max_memory
            self.orchestrator.orchestrate_task(f"Test request {i}")
            
        # Verify memory limit is maintained
        self.assertLessEqual(len(self.orchestrator.memory), self.orchestrator.max_memory)

if __name__ == '__main__':
    unittest.main() 