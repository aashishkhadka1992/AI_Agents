import ast
import json
import logging
from llm.llm_ops import query_llm
from agents.base_agent import Agent
from utils.location_utils import LocationUtils

logger = logging.getLogger(__name__)

class AgentOrchestrator:
    """Coordinates multiple agents to handle user requests.
    
    The orchestrator manages:
    - Agent selection based on request type
    - Location context management
    - Response formatting and delivery
    - Multi-agent coordination for summary requests
    """
    
    def __init__(self, agents: list[Agent]):
        """Initialize orchestrator with list of available agents.
        
        Args:
            agents (list[Agent]): List of agent instances to coordinate
        """
        self.agents = agents
        self.memory = []  # Stores recent interactions
        self.max_memory = 10
        self.location = None  # Current location
        self.location_utils = LocationUtils()
        self.follow_up_prompts = [
            "What else would you like to know?",
            "Is there anything else I can help you with?",
            "What other information would be helpful?",
            "Feel free to ask me anything else!",
            "Would you like to know anything else about the weather or what to wear?",
            "I'm here to help - what's on your mind?",
            "Need any other assistance?",
            "Anything else you'd like to check?"
        ]
        self.exit_phrases = [
            "exit", "bye", "quit", "no", "nope", "that's all", "that is all", 
            "nothing else", "i'm good", "im good", "i am good", "thanks",
            "thank you", "that's it", "that will be all"
        ]
        self.goodbye_messages = [
            "Take care! Have a great day! 👋",
            "Goodbye! Stay warm and stylish! 👋",
            "See you next time! Have a wonderful day! 👋",
            "Thanks for chatting! Stay amazing! ✨",
            "Bye for now! Remember to dress for the weather! 🌤️"
        ]
        self.prompt_index = 0
        self.goodbye_index = 0
        logger.info(f"Initialized orchestrator with {len(agents)} agents")

    def get_next_prompt(self) -> str:
        """Get the next follow-up prompt in a rotating manner."""
        prompt = self.follow_up_prompts[self.prompt_index]
        self.prompt_index = (self.prompt_index + 1) % len(self.follow_up_prompts)
        return prompt

    def get_goodbye_message(self) -> str:
        """Get the next goodbye message in a rotating manner."""
        message = self.goodbye_messages[self.goodbye_index]
        self.goodbye_index = (self.goodbye_index + 1) % len(self.goodbye_messages)
        return message

    def get_location(self, user_input: str) -> str:
        """Extract or request location information.
        
        Attempts to:
        1. Use cached location if available
        2. Extract location from user input
        3. Prompt user for location if needed
        
        Args:
            user_input (str): User's request text
            
        Returns:
            str: Validated location string
        """
        # First check if we already have a location
        if self.location:
            return self.location

        # If location is in the input, validate it
        if "in" in user_input:
            try:
                location = user_input.split("in")[1].strip().split()[0].strip(",.!?")
                if self.location_utils.validate_and_normalize_location(location):
                    self.location = location
                    return location
            except:
                pass

        # Ask user for location in a friendly way
        print("I'd love to help! Could you tell me which city you're in? (You can include state/country for more accuracy)")
        while True:
            location = input("> ").strip()
            if self.location_utils.validate_and_normalize_location(location):
                self.location = location
                return location
            print("I'm having trouble finding that location. Could you try again with a different city name?")

    def format_response(self, responses: list) -> str:
        """Format multiple agent responses into natural language.
        
        Args:
            responses (list): List of agent responses
            
        Returns:
            str: Formatted response string
        """
        if not responses:
            return "I apologize, but I couldn't process your request."
        
        # Join unique responses naturally
        unique = []
        for response in responses:
            if response not in unique:
                unique.append(response)
        
        return " ".join(unique)

    def orchestrate_task(self, user_input: str):
        """Process user request and coordinate appropriate agents.
        
        This method:
        1. Determines request type (summary or specific)
        2. Manages location context
        3. Selects and coordinates appropriate agents
        4. Formats and returns response
        
        Args:
            user_input (str): User's request text
            
        Returns:
            dict: Response containing action and formatted result
        """
        try:
            # Handle negative responses gracefully
            if user_input.lower() in ["no", "nope", "nothing"]:
                return {"action": "respond_to_user", "input": "Alright! Let me know if you need anything else! 😊"}

            # Keep memory of recent interactions
            self.memory = self.memory[-self.max_memory:]
            self.memory.append(f"User: {user_input}")
            
            # Determine if this is a summary request
            is_summary = any(word in user_input.lower() for word in 
                           ['summarize', 'summary', 'rundown', 'brief', 'tell me about'])

            # Get location if needed
            if is_summary or any(word in user_input.lower() for word in ['weather', 'time', 'wear']):
                location = self.get_location(user_input)
                if not location:
                    return {"action": "respond_to_user", 
                           "input": "I need a valid location to provide recommendations."}

            # For summary requests, get all information
            if is_summary:
                responses = []
                # Get weather first
                for agent in self.agents:
                    if agent.name == "Weather Agent":
                        response = agent.process_input(f"Get weather for {location}")
                        responses.append(response)
                    elif agent.name == "Time Agent":
                        response = agent.process_input(f"Get time for {location}")
                        responses.append(response)
                    elif agent.name == "Clothing Agent":
                        response = agent.process_input(f"What should I wear in {location}")
                        responses.append(response)
                return {"action": "respond_to_user", "input": self.format_response(responses)}

            # For specific requests, determine which agent to use
            prompt = f"""
            Based on the user's request, which agent should handle it?
            User request: {user_input}
            Available agents: Weather Agent (weather info), Time Agent (current time), Clothing Agent (clothing recommendations)
            Only return the agent name, nothing else.
            """
            agent_name = query_llm(prompt).strip()
            
            # Find and use the appropriate agent
            for agent in self.agents:
                if agent.name == agent_name:
                    # Add location to input if needed
                    if self.location and self.location not in user_input:
                        user_input += f" in {self.location}"
                    response = agent.process_input(user_input)
                    return {"action": "respond_to_user", "input": response}

            return {"action": "respond_to_user", 
                   "input": "I'm not sure how to help with that request."}

        except Exception as e:
            logger.error(f"Error in orchestration: {str(e)}")
            return {"action": "respond_to_user", 
                   "input": "I encountered an error processing your request."}

    def run(self):
        """Run interactive assistant loop.
        
        Handles:
        - User input/output
        - Command processing
        - Error handling
        - Graceful exit
        """
        try:
            print("Hi there! 👋 I'm your personal assistant for weather updates, time information, and clothing recommendations.")
            print("I can help you plan your day and choose the perfect outfit based on the weather!")
            print("\nHere are some things you can ask me:")
            print("🌤️  What's the weather like in New York?")
            print("👔  What should I wear today?")
            print("📋  Give me a summary of my day")
            print("🕒  What time is it in London?")
            print("\nType 'exit' when you're done!")
            
            while True:
                user_input = input(f"\n{self.get_next_prompt()} ").strip()
                
                if user_input.lower() in self.exit_phrases:
                    print(f"\n{self.get_goodbye_message()}")
                    break

                response = self.orchestrate_task(user_input)
                print("\n" + response["input"])

        except KeyboardInterrupt:
            print(f"\n{self.get_goodbye_message()}")
        except Exception as e:
            logger.error(f"Error in main loop: {str(e)}")
            print("Oops! Something unexpected happened. Let's try that again!")
