"""Error handling module for the AI Agents framework.

This module provides custom exceptions and error handling utilities
for agent operations, tool execution, and orchestration.
"""

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
    """Decorator for handling agent-related errors.
    
    Args:
        func: The function to wrap
        
    Returns:
        wrapper: The wrapped function with error handling
    """
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
    """Decorator for handling tool-related errors.
    
    Args:
        func: The function to wrap
        
    Returns:
        wrapper: The wrapped function with error handling
    """
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
    """Format error into a user-friendly response.
    
    Args:
        error: The exception to format
        
    Returns:
        dict: Formatted error response
    """
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
    """Log error with additional context.
    
    Args:
        error: The exception to log
        context: Additional context information
    """
    error_type = type(error).__name__
    error_msg = str(error)
    
    if context:
        logger.error(f"{error_type}: {error_msg} | Context: {context}")
    else:
        logger.error(f"{error_type}: {error_msg}")
        
    if hasattr(error, 'details') and error.details:
        logger.debug(f"Error details: {error.details}") 