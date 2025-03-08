import requests
import os
import json
import logging
import re

logger = logging.getLogger(__name__)

def clean_json_response(response: str) -> str:
    """Clean JSON response from markdown formatting."""
    # Remove markdown code block if present
    cleaned = re.sub(r'```(?:json)?\n(.*?)\n```', r'\1', response, flags=re.DOTALL)
    # Remove any remaining backticks
    cleaned = cleaned.replace('`', '')
    # Strip whitespace
    cleaned = cleaned.strip()
    return cleaned

def query_llm(prompt: str, model=None):
    try:
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY environment variable not set")

        model = model or os.getenv("LLM_MODEL", "gpt-4o")
        logger.debug(f"Using model: {model}")

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}"
        }
        data = {
            "model": model,
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": 150,
            "temperature": 0.2
        }
        
        logger.debug(f"Sending request to OpenAI API")
        response = requests.post(
            "https://api.openai.com/v1/chat/completions",
            headers=headers,
            data=json.dumps(data),
            verify=True  # Always verify SSL certificates in production
        )
        
        response.raise_for_status()  # Raise an exception for bad status codes
        
        final_response = response.json()['choices'][0]['message']['content'].strip()
        logger.debug(f"Raw response from LLM: {final_response}")
        
        # Clean the response
        cleaned_response = clean_json_response(final_response)
        logger.debug(f"Cleaned response: {cleaned_response}")
        
        return cleaned_response
        
    except requests.exceptions.RequestException as e:
        logger.error(f"API request failed: {str(e)}")
        raise
    except (KeyError, IndexError) as e:
        logger.error(f"Error parsing API response: {str(e)}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        raise