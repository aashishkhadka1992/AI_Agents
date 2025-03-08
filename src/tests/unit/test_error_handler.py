import unittest
from unittest.mock import patch, MagicMock
import logging
from utils.error_handler import (
    AgentError,
    ToolError,
    LocationError,
    OrchestratorError,
    LLMError,
    handle_agent_error,
    handle_tool_error,
    format_error_response,
    log_error
)

class TestErrorHandler(unittest.TestCase):
    """Test cases for error handling module."""

    def setUp(self):
        """Set up test fixtures."""
        self.test_message = "Test error message"
        self.test_details = {"key": "value"}

    def test_agent_error(self):
        """Test AgentError creation and logging."""
        with self.assertLogs(level='ERROR') as log:
            error = AgentError(
                message=self.test_message,
                agent_name="TestAgent",
                details=self.test_details
            )
            
            self.assertEqual(str(error), self.test_message)
            self.assertEqual(error.agent_name, "TestAgent")
            self.assertEqual(error.details, self.test_details)
            self.assertIn("Agent Error [TestAgent]", log.output[0])

    def test_tool_error(self):
        """Test ToolError creation and logging."""
        with self.assertLogs(level='ERROR') as log:
            error = ToolError(
                message=self.test_message,
                tool_name="TestTool",
                details=self.test_details
            )
            
            self.assertEqual(str(error), self.test_message)
            self.assertEqual(error.tool_name, "TestTool")
            self.assertEqual(error.details, self.test_details)
            self.assertIn("Tool Error [TestTool]", log.output[0])

    def test_location_error(self):
        """Test LocationError creation and logging."""
        with self.assertLogs(level='ERROR') as log:
            error = LocationError(
                message=self.test_message,
                location="TestCity",
                details=self.test_details
            )
            
            self.assertEqual(str(error), self.test_message)
            self.assertEqual(error.location, "TestCity")
            self.assertEqual(error.details, self.test_details)
            self.assertIn("Location Error [TestCity]", log.output[0])

    def test_orchestrator_error(self):
        """Test OrchestratorError creation and logging."""
        with self.assertLogs(level='ERROR') as log:
            error = OrchestratorError(
                message=self.test_message,
                details=self.test_details
            )
            
            self.assertEqual(str(error), self.test_message)
            self.assertEqual(error.details, self.test_details)
            self.assertIn("Orchestrator Error", log.output[0])

    def test_llm_error(self):
        """Test LLMError creation and logging."""
        with self.assertLogs(level='ERROR') as log:
            error = LLMError(
                message=self.test_message,
                model="TestModel",
                details=self.test_details
            )
            
            self.assertEqual(str(error), self.test_message)
            self.assertEqual(error.model, "TestModel")
            self.assertEqual(error.details, self.test_details)
            self.assertIn("LLM Error [TestModel]", log.output[0])

    def test_handle_agent_error_decorator(self):
        """Test agent error handling decorator."""
        @handle_agent_error
        def test_func():
            raise AgentError("Test agent error")

        result = test_func()
        self.assertEqual(result["action"], "respond_to_user")
        self.assertIn("error", result["input"].lower())

    def test_handle_tool_error_decorator(self):
        """Test tool error handling decorator."""
        @handle_tool_error
        def test_func():
            raise ToolError("Test tool error")

        result = test_func()
        self.assertIn("Tool error", result)

    def test_format_error_response(self):
        """Test error response formatting."""
        # Test LocationError formatting
        location_error = LocationError("Invalid location")
        response = format_error_response(location_error)
        self.assertIn("location", response["input"].lower())
        
        # Test ToolError formatting
        tool_error = ToolError("Tool failed")
        response = format_error_response(tool_error)
        self.assertIn("trouble", response["input"].lower())
        
        # Test LLMError formatting
        llm_error = LLMError("Model error")
        response = format_error_response(llm_error)
        self.assertIn("processing", response["input"].lower())
        
        # Test generic error formatting
        generic_error = Exception("Generic error")
        response = format_error_response(generic_error)
        self.assertIn("unexpected", response["input"].lower())

    def test_log_error(self):
        """Test error logging with context."""
        test_error = AgentError("Test error")
        test_context = {"operation": "test"}
        
        with self.assertLogs(level='ERROR') as log:
            log_error(test_error, test_context)
            self.assertIn("Context", log.output[0])
            
        with self.assertLogs(level='ERROR') as log:
            log_error(test_error)
            self.assertNotIn("Context", log.output[0])

if __name__ == '__main__':
    unittest.main() 