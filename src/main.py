from agents.base_agent import Agent
from tools.weather_tool import WeatherTool
from tools.time_tool import TimeTool
from tools.clothing_tool import ClothingTool
from orchestrator import AgentOrchestrator

from dotenv import load_dotenv
import os
import logging
import sys

# Load environment variables first
load_dotenv()

# Set root logger level based on DEBUG environment variable
root_level = logging.DEBUG if os.getenv("DEBUG", "False").lower() == "true" else logging.INFO

# Configure root logger
logging.basicConfig(
    level=root_level,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

# Disable propagation of debug logs from child loggers
logging.getLogger('agents').setLevel(root_level)
logging.getLogger('llm').setLevel(root_level)
logging.getLogger('tools').setLevel(root_level)
logging.getLogger('utils').setLevel(root_level)
logging.getLogger('urllib3').setLevel(logging.WARNING)
logging.getLogger('httpx').setLevel(logging.WARNING)
logging.getLogger('httpcore').setLevel(logging.WARNING)
logging.getLogger('openai').setLevel(logging.WARNING)

logger = logging.getLogger(__name__)

def initialize_orchestrator():
    """Initialize and return the agent orchestrator."""
    try:
        logger.info("Environment variables loaded")
        
        # Create Weather Agent
        weather_agent = Agent(
            Name="Weather Agent",
            Description="Provides weather information for a given location",
            Tools=[WeatherTool()],
            Model=os.getenv("LLM_MODEL", "gpt-4o")
        )
        logger.info("Weather Agent initialized")

        # Create Time Agent
        time_agent = Agent(
            Name="Time Agent",
            Description="Provides the current time for a given city",
            Tools=[TimeTool()],
            Model=os.getenv("LLM_MODEL", "gpt-4o")
        )
        logger.info("Time Agent initialized")

        # Create Clothing Agent
        clothing_agent = Agent(
            Name="Clothing Agent",
            Description="Provides personalized clothing recommendations based on weather conditions, time, and user preferences",
            Tools=[ClothingTool()],
            Model=os.getenv("LLM_MODEL", "gpt-4o")
        )
        logger.info("Clothing Agent initialized")

        # Create and return AgentOrchestrator
        agent_orchestrator = AgentOrchestrator([weather_agent, time_agent, clothing_agent])
        logger.info("Agent Orchestrator initialized")
        
        return agent_orchestrator

    except Exception as e:
        logger.error(f"Error initializing orchestrator: {str(e)}")
        raise

def main():
    try:
        # Initialize orchestrator
        agent_orchestrator = initialize_orchestrator()

        # Run the orchestrator
        logger.info("Starting Agent Orchestrator...")
        agent_orchestrator.run()

    except Exception as e:
        logger.error(f"Error in main: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()

