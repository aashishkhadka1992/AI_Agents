from abc import ABC, abstractmethod
import ast
import os
import requests
from llm.llm_ops import query_llm
from tools.base_tool import BaseTool
import json
import logging
from typing import Union, Dict

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
        """Parse string input into JSON/dict format.
        
        Args:
            input_string: String to parse into JSON
            
        Returns:
            dict: Parsed JSON dictionary
            
        Raises:
            ValueError: If input cannot be parsed as JSON
        """
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
        
        Args:
            user_input (str): User's request/query
            
        Returns:
            dict: Response containing action and result
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
        """Execute a specific tool with given arguments.
        
        Args:
            tool_name (str): Name of the tool to use
            args (Union[str, Dict]): Arguments for the tool
            
        Returns:
            str: Result of tool execution
        """
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
