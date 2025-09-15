def generative_fill(
    api_key: str,
    image_data: bytes,
    mask_data: bytes,
    prompt: str,
    negative_prompt: Optional[str] = None,
    num_results: int = 4,
    sync: bool = False,
    seed: Optional[int] = None,
    content_moderation: bool = False,
    mask_type: str = "manual"
    ) -> Dict[str, Any]:
    ''' It enables the generation of objects by prompt in a specific mask area'''

    pass