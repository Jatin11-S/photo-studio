from typing import Dict, Any
import requests
import base64

def create_packshot(
    api_key: str,
    image_data: bytes,
    background_color: str = "#FFFFFF",
    sku: str = 'None',
    force_rmbg: bool = False,
    content_moderation: bool = False
    ) -> Dict[str, Any]:
    ''' Creates a professional packshot from a product image. '''
    # Converting the image data to base64
    image_base64 = base64.b64encode(image_data).decode('utf-8')

    data = {
        'file': image_base64,
        'background_color': background_color,
        'force_rmbg': force_rmbg,
        'content_moderation': content_moderation
    }
    url = "https://engine.prod.bria-api.com/v1/product/packshot"
    headers = {
        'api_token': api_key,
        'Accept': 'application/json',
        'Content-Type': 'application/json'
    }
    # Optional sku data:                  
    if sku:                   
        data['sku'] = sku

    try:
        print(f"Making request to: {url}")
        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()
        print(f"Response status: {response.status_code}")
        print(f"Response body: {response.text}")  
        return response.json()
    
    except Exception as e:
        raise Exception(f"Packshot creation failed: {str(e)}") 