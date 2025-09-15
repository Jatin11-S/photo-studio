from typing import Dict, Any, List, Optional
import requests
import base64

def add_shadows(api_key: str,
    image_data: bytes = None,
    image_url: str = None,
    shadow_type: str = "regular",
    background_color: Optional[str] = None,
    shadow_color: str = "#000000",
    shadow_offset: List[int] = [0, 15],
    shadow_intensity: int = 60,
    shadow_blur: Optional[int] = None,
    shadow_width: Optional[int] = None,
    shadow_height: Optional[int] = 70,
    sku: Optional[str] = None,
    force_rmbg: bool = False,
    content_moderation: bool = False    
    ) -> Dict[str, Any]:
    ''' Adds shadow to an image. '''
    data = {
        'shadow_type': shadow_type,
        'shadow_color': shadow_color,
        'shadow_intensity': shadow_intensity,
        'force_rmbg': force_rmbg,
        'content_moderation': content_moderation,
        'shadow_offset': shadow_offset
    }
    url = "https://engine.prod.bria-api.com/v1/product/shadow"
    headers = {
        'api_token': api_key,
        'Accept': 'application/json',
        'Content-Type': 'application/json'
    }
    # image data can be provided in both url and base64 data
    if image_url:
        data['image_url'] = image_url
    elif image_data:
        data['file'] = base64.b64encode(image_data).decode('utf-8')
    else:
        raise ValueError("Either image_data or image_url must be provided")
    # Optional parameters, if required:
    if background_color:
        data['background_color'] = background_color
    if shadow_blur is not None:
        data['shadow_blur'] = shadow_blur
    if shadow_width is not None:
        data['shadow_width'] = shadow_width
    if shadow_height is not None:
        data['shadow_height'] = shadow_height
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
        raise Exception(f"Shadow addition failed: {str(e)}") 