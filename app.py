import streamlit as st
import os
from dotenv import load_dotenv
from services import (
    lifestyle_shot_by_image,
    lifestyle_shot_by_text,
    add_shadow,
    create_packshot,
    enhance_prompt,
    generative_fill,
    generate_hd_image,
    erase_foreground
)
from PIL import Image
import io
import requests
import json
import time
import base64
from streamlit_drawable_canvas import st_canvas
import numpy as np

# Configure Streamlit page
st.set_page_config(
    page_title="My Photo Studio",
    page_icon="🖼️",
    layout="wide",
    initial_sidebar_state="expanded"
)
# Load environment variables
load_dotenv(verbose=True)
api_key = os.getenv("BRIA_API_KEY")
print(f"API Key present: {bool(api_key)}")
print(f"API Key value: {api_key if api_key else 'Not found'}")
print(f"Current working directory: {os.getcwd()}")

def initialize_session_state():
    """ Initializes all the session state keys the app relies on """
    if 'api_key' not in st.session_state:
        st.session_state.api_key = os.getenv('BRIA_API_KEY')
    if 'generated_images' not in st.session_state:
        st.session_state.generated_images = []
    if 'current_image' not in st.session_state:
        st.session_state.current_image = None
    if 'pending_urls' not in st.session_state:
        st.session_state.pending_urls = []
    if 'edited_image' not in st.session_state:
        st.session_state.edited_image = None
    if 'original_prompt' not in st.session_state:
        st.session_state.original_prompt = ""
    if 'enhanced_prompt' not in st.session_state:
        st.session_state.enhanced_prompt = None

def download_image(url):
    """Download image from URL and return raw data as bytes."""
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.content
    except Exception as e:
        st.error(f"Error downloading the image: {str(e)}")
        return None

def main():
    st.title('AI Photo Studio')
    initialize_session_state()
    # Sidebar for API key
    with st.sidebar:
        st.header("Settings")
        api_key = st.text_input(
            "Enter your API key:", 
            value = st.session_state.api_key if st.session_state.api_key else "",
            type = "password"
        )
        if api_key:
            st.session_state.api_key = api_key
    # Main tabs
    tabs = st.tabs([
        "🖼️ Photo Generation",
        "🎥 Product Photo",
        "🎨 Generative Fill", 
        "🧼 Erase Elements"
    ])

    # Tab 1: Photo Generation
    with tabs[0]:
        st.header('Generate the Photo from text.')
        col1, col2 = st.columns([2, 1])
        with col1:
            # Text Prompt
            prompt = st.text_area(
                "Enter your prompt",
                value="",
                height=100,
                placeholder="Example: A red coffee mug on a wooden table with soft lighting"
            )
             # Store original prompt in session state when it changes
            if "original_prompt" not in st.session_state:
                st.session_state.original_prompt = prompt
            elif prompt != st.session_state.original_prompt:
                st.session_state.original_prompt = prompt
                st.session_state.enhanced_prompt = None  # Reset enhanced prompt when original changes\

            # Enhance Prompt button
            if st.button("✨ Enhance Prompt"):
                if not prompt:
                    st.warning("Please enter a prompt to enhance.")
                elif not st.session_state.api_key:
                    st.error("Please enter your API key in the sidebar.")
                else:
                    with st.spinner("Enhancing prompt..."):
                        try:
                            result = enhance_prompt(st.session_state.api_key, prompt)
                            if result != prompt:
                                st.session_state.enhanced_prompt = result
                                st.success("Prompt enhanced!")
                                st.markdown(f"**Enhanced:** *{result}*")
                        except Exception as e:
                            st.error(f"Error enhancing prompt: {str(e)}")
        with col2:
            num_images = st.slider("Number of images", 1, 4, 1)
            aspect_ratio = st.selectbox("Aspect ratio", ["1:1", "16:9", "9:16", "4:3", "3:4"])
            enhance_img = st.checkbox("Enhance image quality", value=True)
            
            style = st.selectbox("Image Style", [
                "Realistic", "Artistic", "Cartoon", "Sketch",
                "Watercolor", "Oil Painting", "Digital Art"
            ])
        
        # Generate button
        if st.button("🎨 Generate Images", type="primary"):
            if not st.session_state.api_key:
                st.error("Please enter your API key in the sidebar.")
            elif not prompt:
                st.error("Please enter a prompt.")
            else:
                final_prompt = st.session_state.enhanced_prompt or prompt
                if style and style != "Realistic":
                    final_prompt = f"{final_prompt}, in {style.lower()} style"
            
                with st.spinner("🎨 Generating your image..."):
                    try:
                        result = generate_hd_image(
                            prompt=final_prompt,
                            api_key=st.session_state.api_key,
                            num_results=num_images,
                            aspect_ratio=aspect_ratio,
                            sync=True,
                            enhance_image=enhance_img,
                            medium="art" if style != "Realistic" else "photography",
                            content_moderation=True
                        )
                        if result:
                            # Handle different response formats
                            if "result_url" in result:
                                st.session_state.edited_image = result["result_url"]
                                st.success("✨ Image generated successfully!")
                            elif "result_urls" in result:
                                st.session_state.edited_image = result["result_urls"]
                                st.success("✨ Image generated successfully!")
                            else:
                                st.error("Unexpected response format")
                                st.json(result)
                                
                    except Exception as e:
                        st.error(f"Error generating images: {str(e)}")
        # Display result
        if st.session_state.edited_image:
            st.image(st.session_state.edited_image, caption="Generated Image")
            image_data = download_image(st.session_state.edited_image)
            if image_data:
                st.download_button(
                    "⬇️ Download Image",
                    image_data,
                    "generated_image.png",
                    "image/png"
                )
    with tabs[1]:
        st.header("Product Photo")
        st.write("Upload a product image and choose editing options.")
        # Add product photography functionality
        
    with tabs[2]:
        st.header("Generative Fill")
        st.write("Draw a mask and describe what to generate.")
        # Add generative fill functionality
        
    with tabs[3]:
        st.header("Erase Elements")
        st.write("Select areas to remove from your image.")
        # Add erase functionality

if __name__ == "__main__":
    main()            

