from typing import Dict, Any, Optional
import requests
import json

def enhance_prompt(api_key: str,
    prompt: str,
    **kwargs
    ) -> str:
    """ Enhance a prompt using Bria AI's prompt enhancement. """
    data = {
        'prompt': prompt,
        **kwargs
    }
    url = "https://engine.prod.bria-api.com/v1/prompt_enhancer"
    headers = {
        'api_token': api_key,
        'Accept': 'application/json',
        'Content-Type': 'application/json'
    }

    try:
        print(f"Making request to: {url}")
        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()
        result = response.json()
        return result.get("prompt variations", prompt)
    
    except Exception as e:
        print(f"Error enhancing prompt: {str(e)}")
        return prompt  
        # Return original prompt on error