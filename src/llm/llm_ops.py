import requests
import os
import json
import logging
import re
from openai import OpenAI
import httpx

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

def _init_codegenie_client():
    """Initialize Code Genie OpenAI client with custom configuration."""
    base_url = os.getenv("CODEGENIE_BASE_URL")
    api_key = os.getenv("CODE_GENIE_API_KEY")
    
    if not base_url or not api_key:
        raise ValueError("CODEGENIE_BASE_URL and CODE_GENIE_API_KEY environment variables must be set")
    
    return OpenAI(
        api_key=api_key,
        base_url=base_url,
        http_client=httpx.Client(
            base_url=base_url,
            timeout=60.0,
            follow_redirects=True
        )
    )

def query_llm(prompt: str, model=None):
    try:
        use_codegenie = os.getenv("USE_CODEGENIE", "false").lower() == "true"
        model = model or os.getenv("LLM_MODEL", "gpt-4o-mini")
        logger.debug(f"Configuration - USE_CODEGENIE: {use_codegenie}, Initial Model: {model}")
        
        if use_codegenie:
            # Use Code Genie API
            client = _init_codegenie_client()
            logger.debug("Using Code Genie API")
            
            # Format model name for Code Genie
            model_name = f"openai/{model}" if not model.startswith("openai/") else model
            logger.debug(f"Formatted model name for Code Genie: {model_name}")
            
            try:
                logger.debug("Sending request to Code Genie API...")
                completion = client.chat.completions.create(
                    model=model_name,
                    messages=[
                        {"role": "system", "content": "You are a helpful assistant."},
                        {"role": "user", "content": prompt}
                    ],
                    max_tokens=150,
                    temperature=0.2
                )
                logger.debug(f"Code Genie API response structure: {completion}")
                final_response = completion.choices[0].message.content.strip()
                logger.debug(f"Successfully extracted response from Code Genie API")
            except Exception as e:
                logger.error(f"Code Genie API call failed with error type {type(e).__name__}: {str(e)}")
                logger.error(f"Model used: {model_name}")
                logger.error(f"Base URL: {os.getenv('CODEGENIE_BASE_URL')}")
                raise
        else:
            # Use OpenAI API
            api_key = os.getenv("OPENAI_API_KEY")
            if not api_key:
                raise ValueError("OPENAI_API_KEY environment variable not set")

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
            
            logger.debug("Using OpenAI API")
            response = requests.post(
                "https://api.openai.com/v1/chat/completions",
                headers=headers,
                data=json.dumps(data),
                verify=True
            )
            response.raise_for_status()
            final_response = response.json()['choices'][0]['message']['content'].strip()
        
        logger.debug(f"Raw response from LLM: {final_response}")
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