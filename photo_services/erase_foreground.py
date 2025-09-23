from typing import Dict, Any, Optional
import requests
import base64

def erase_foreground(
    api_key: str,
    image_data: bytes = None,
    image_url: str = None,
    content_moderation: bool = False
    ) -> Dict[str, Any]:
    ''' Removes the primary object and fills the background at erased area. '''
    
    data = {
        'content_moderation': content_moderation
    }
    # Add image data
    if image_url:
        data['image_url'] = image_url
    elif image_data:
        data['file'] = base64.b64encode(image_data).decode('utf-8')
    else:
        raise ValueError("Either image_data or image_url must be provided")

    url = "https://engine.prod.bria-api.com/v1/erase_foreground"
    headers = {
        'api_token': api_key,
        'Accept': 'application/json',
        'Content-Type': 'application/json'
    }

    try:
        print(f"Making request to: {url}")
        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status() 
        print(f"Response status: {response.status_code}")
        return response.json()

    except Exception as e:
        raise Exception(f"Erase foreground failed: {str(e)}")

'''__all__ = ['erase_foreground'] '''