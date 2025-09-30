import os
import streamlit as st
from dotenv import load_dotenv
from PIL import Image
from photo_services import (
    lifestyle_shot_by_image,
    lifestyle_shot_by_text,
    add_shadows,
    create_packshot,
    enhance_prompt,
    generative_fill,
    generate_hd_image,
    erase_foreground
)
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
    st.title('Photo Studio')
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
                        # After you get `result` from generate_hd_image(...)
                        if result:
                            # 1) Direct single URL
                            if isinstance(result, dict) and "result_url" in result and result["result_url"]:
                                st.session_state.edited_image = result["result_url"]
                                st.success("✨ Image generated successfully!")
                            # 2) Direct multiple URLs
                            elif isinstance(result, dict) and "result_urls" in result and result["result_urls"]:
                                # Keep the first one for preview; store all if you want a gallery
                                st.session_state.edited_image = result["result_urls"][0]
                                st.session_state.generated_images = result["result_urls"]
                                st.success("✨ Image generated successfully!")
                            # 3) Nested list under result -> [ { "urls": [...] }, ... ]
                            elif isinstance(result, dict) and "result" in result and isinstance(result["result"], list):
                                urls = []
                                for item in result["result"]:
                                    if isinstance(item, dict) and "urls" in item and item["urls"]:
                                        urls.extend(item["urls"])
                                if urls:
                                    st.session_state.edited_image = urls[0]
                                    st.session_state.generated_images = urls
                                    st.success("✨ Image generated successfully!")
                                else:
                                    st.error("Received response but found no URLs.")
                                    st.json(result)  # helpful debug
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
    # --- Product Photo Tab ---
    with tabs[1]:
        st.header("Product Photo")

        uploaded_file = st.file_uploader(
            "Upload Product Image",
            type=["png", "jpg", "jpeg"],
            key="product_upload"
        )

        def parse_urls(payload):  # Returns unique ordered lists of Image URLs from payload dict
            urls = []
            if not isinstance(payload, dict):
                return urls
            if "result_url" in payload and payload["result_url"]:
                urls.append(payload["result_url"])
            if "result_urls" in payload and payload["result_urls"]:
                urls.extend(payload["result_urls"])
            if "result" in payload and isinstance(payload["result"], list):
                for item in payload["result"]:
                    if isinstance(item, dict) and "urls" in item and item["urls"]:
                        urls.extend(item["urls"])
            # Deduplicate, and keep order in uniq list
            seen = set()
            uniq = []
            for u in urls:
                if u and u not in seen:
                    uniq.append(u)
                    seen.add(u)
            return uniq
        
        colL, colR = st.columns(2)
        with colL:
            if uploaded_file:
                st.image(uploaded_file, caption="Original Image", use_column_width=True)
        if not uploaded_file:
            st.info('Upload an image to continue.')
            st.stop()

        # Action chooser
        st.subheader("Actions")
        action = st.selectbox(
            "Choose an action",
            ["Create Packshot", "Add Shadow", "Lifestyle Shot"]
        )

        # ---Create Packshot---
        if action == 'Create Packshot':
            c1, c2 = st.columns(2)
            with c1:
                bg_color = st.color_picker("Background Color", "#FFFFFF")
                sku = st.text_input("SKU (optional)", "")
            with c2:
                force_rmbg = st.checkbox("Force Background Removal", False)
                content_moderation = st.checkbox("Enable Content Moderation", False)
            
            if st.button("Create Packshot", type="primary"):
                try:
                    with st.spinner("Creating a product packshot..."):
                        result = create_packshot(
                            api_key = st.session_state.api_key,
                            image_data = uploaded_file.getvalue(),
                            background_color = bg_color,
                            sku = sku if sku else None,
                            force_rmbg = force_rmbg,
                            content_moderation = content_moderation
                        )
                    urls = parse_urls(result)
                    if urls:
                        st.success('✨ Packshot created successfully!')
                        st.image(urls[0], caption="Packshot", use_column_width=True)
                        st.session_state.edited_image = urls[0]
                        # Download button
                        img_bytes = download_image(urls[0])
                        if img_bytes:
                            st.download_button(
                                "⬇️ Download",
                                img_bytes,
                                "packshot.png",
                                "image/png"
                            )
                        else:
                            st.error("No result URL found.")
                            st.json(result)
                except Exception as e:
                    st.error(f"Error creating packshot: {e}")

        # ---Add Shadows---   
        if action == 'Add Shadow':
            c1,c2 = st.columns(2)
            with c1:
                shadow_type = st.selectbox("Shadow Type", ["Natural", "Drop", "Float"])
                bg_color = st.color_picker("Background Color (optional)", "#FFFFFF")
                use_transparent_bg = st.checkbox("Use Transparent Background", True)
                shadow_color = st.color_picker("Shadow Color", "#000000")
                sku = st.text_input("SKU (optional)", "")
                st.subheader("Offset")
                offset_x = st.slider("X Offset", -50, 50, 0)
                offset_y = st.slider("Y Offset", -50, 50, 15)     
            with c2:
                shadow_intensity = st.slider("Shadow Intensity", 0, 100, 60)
                # Blur suggestion defaults
                default_blur = 15 if shadow_type.lower() in ["natural", "drop"] else 20
                shadow_blur = st.slider("Shadow Blur", 0, 50, default_blur)
                # Float-only options
                shadow_width = None
                shadow_height = 70
                if shadow_type == "Float":
                    st.subheader("Float Shadow")
                    shadow_width = st.slider("Shadow Width", -100, 100, 0)
                    shadow_height = st.slider("Shadow Height", -100, 100, 70)
                force_rmbg = st.checkbox("Force Background Removal", False)
                content_moderation = st.checkbox("Enable Content Moderation", False)
            
            if st.button('Add Shadow', type='primary'):
                try:
                    with st.spinner('Adding some shadow effects...'):
                        result = add_shadows(
                        api_key = st.session_state.api_key,
                        image_data = uploaded_file.getvalue(),
                        shadow_type = "float" if shadow_type == "Float" else "regular",
                        background_color = None if use_transparent_bg else bg_color,
                        shadow_color = shadow_color,
                        shadow_offset = [offset_x, offset_y],
                        shadow_intensity = shadow_intensity,
                        shadow_blur = shadow_blur,
                        shadow_width = shadow_width,
                        shadow_height = shadow_height,
                        sku = sku if sku else None,
                        force_rmbg = force_rmbg,
                        content_moderation = content_moderation
                    )
                    urls = parse_urls(result)
                    if urls:
                        st.success('✨ Shadow added successfully!')
                        st.image(urls[0], caption="Shadow Result", use_column_width=True)
                        st.session_state.edited_image = urls[0]
                        img_bytes = download_image(urls[0])
                        if img_bytes:
                            st.download_button(
                                "⬇️ Download",
                                img_bytes,
                                "shadow_result.png",
                                "image/png"
                            )
                    else:
                        st.error("No result URL found.")
                        st.json(result)
                except Exception as e:
                    st.error(f"Error adding shadows: {e}")

        # ---Lifestyle Shot---
        if action == 'Lifestyle Shot':
            shot_type = st.radio("Shot Type", ["Text Prompt", "Reference Image"])
            left, right = st.columns(2)

            with left:
                placement_type = st.selectbox(
                    "Placement Type",
                    ["Original", "Automatic", "Manual Placement", "Manual Padding", "Custom Coordinates"]
                )
                num_results = st.slider("Number of Results", 1, 8, 4)
                sync_mode = st.checkbox("Synchronous Mode", True, help="Wait for results rather than polling")
                original_quality = st.checkbox("Original Quality", False)

                # Placement-specific inputs
                positions = []
                if placement_type == "Manual Placement":
                    positions = st.multiselect(
                        "Select Positions",
                        [
                            "Upper Left", "Upper Right", "Bottom Left", "Bottom Right",
                            "Right Center", "Left Center", "Upper Center",
                            "Bottom Center", "Center Vertical", "Center Horizontal"
                        ],
                        ["Upper Left"]
                    )
                elif placement_type == "Manual Padding":
                    st.subheader("Padding (px)")
                    pad_left = st.number_input("Left", 0, 1000, 0)
                    pad_right = st.number_input("Right", 0, 1000, 0)
                    pad_top = st.number_input("Top", 0, 1000, 0)
                    pad_bottom = st.number_input("Bottom", 0, 1000, 0)
                if placement_type in ["Automatic", "Manual Placement", "Custom Coordinates"]:
                    st.subheader("Shot Size")
                    shot_width = st.number_input("Width", 100, 2000, 1000)
                    shot_height = st.number_input("Height", 100, 2000, 1000)

            with right:
                if placement_type == "Custom Coordinates":
                    st.subheader("Product Position")
                    fg_width = st.number_input("Product Width", 50, 1000, 500)
                    fg_height = st.number_input("Product Height", 50, 1000, 500)
                    fg_x = st.number_input("X", -500, 1500, 0)
                    fg_y = st.number_input("Y", -500, 1500, 0)

                sku = st.text_input("SKU (optional)")
                force_rmbg = st.checkbox("Force Background Removal", False)
                content_moderation = st.checkbox("Enable Content Moderation", False)  
                exclude_elements = None
                fast_mode = True
                optimize_desc = True
                if shot_type == "Text Prompt":
                    fast_mode = st.checkbox("Fast Mode", True)
                    optimize_desc = st.checkbox("Optimize Description", True)
                    if not fast_mode:
                        exclude_elements = st.text_area("Exclude Elements (optional)")  
                
                enhance_ref = True
                ref_influence = 1.0
                ref_uploader = None
                if shot_type == "Reference Image":
                    enhance_ref = st.checkbox("Enhance Reference Image", True)
                    ref_influence = st.slider("Reference Influence", 0.0, 1.0, 1.0)
                    ref_uploader = st.file_uploader(
                        "Upload Reference Image",
                        type=["png", "jpg", "jpeg"],
                        key="ref_upload"
                )

            manual_placements = []
            if placement_type == "Manual Placement":
                manual_placements = [p.lower().replace(" ", "_") for p in positions] 

            # Build common args
            size = [shot_width, shot_height] if placement_type != "Original" else [1000, 1000]
            padding = [0, 0, 0, 0]
            if placement_type == "Manual Padding":
                padding = [pad_left, pad_right, pad_top, pad_bottom]
            fg_size = [fg_width, fg_height] if placement_type == "Custom Coordinates" else None
            fg_loc = [fg_x, fg_y] if placement_type == "Custom Coordinates" else None  

            # Handlers
            if shot_type == "Text Prompt":
                scene_prompt = st.text_area("Describe the environment")
                if st.button("Generate Lifestyle Shot", type="primary") and scene_prompt:
                    try:
                        with st.spinner("Generating lifestyle shot..."):
                            result = lifestyle_shot_by_text(
                                api_key=st.session_state.api_key,
                                image_data=uploaded_file.getvalue(),
                                scene_description=scene_prompt,
                                placement_type=placement_type.lower().replace(" ", "_"),
                                num_results=num_results,
                                sync=sync_mode,
                                fast=fast_mode,
                                optimize_description=optimize_desc,
                                shot_size=size,
                                original_quality=original_quality,
                                exclude_elements=exclude_elements if not fast_mode else None,
                                manual_placement_selection=manual_placements if manual_placements else ["upper_left"],
                                padding_values=padding,
                                foreground_image_size=fg_size,
                                foreground_image_location=fg_loc,
                                force_rmbg=force_rmbg,
                                content_moderation=content_moderation,
                                sku=sku if sku else None
                            )
                        urls = parse_urls(result)
                        if urls:
                            st.success("✨ Lifestyle shot generated!")
                            st.image(urls[0], use_column_width=True)
                            st.session_state.edited_image = urls[0]
                            if len(urls) > 1:
                                st.session_state.generated_images = urls
                        else:
                            st.error("No URLs found in response.")
                            st.json(result)
                    except Exception as e:
                        st.error(f"Error: {e}") 

            else:  # Reference Image
                if st.button("Generate Lifestyle Shot (Ref Image)", type="primary") and ref_uploader:
                    try:
                        with st.spinner("Generating lifestyle shot..."):
                            result = lifestyle_shot_by_image(
                                api_key=st.session_state.api_key,
                                image_data=uploaded_file.getvalue(),
                                reference_image=ref_uploader.getvalue(),
                                placement_type=placement_type.lower().replace(" ", "_"),
                                num_results=num_results,
                                sync=sync_mode,
                                shot_size=size,
                                original_quality=original_quality,
                                manual_placement_selection=manual_placements if manual_placements else ["upper_left"],
                                padding_values=padding,
                                foreground_image_size=fg_size,
                                foreground_image_location=fg_loc,
                                force_rmbg=force_rmbg,
                                content_moderation=content_moderation,
                                sku=sku if sku else None,
                                enhance_ref_image=enhance_ref,
                                ref_image_influence=ref_influence
                            )
                        urls = parse_urls(result)
                        if urls:
                            st.success("✨ Lifestyle shot generated!")
                            st.image(urls[0], use_column_width=True)
                            st.session_state.edited_image = urls[0]
                            if len(urls) > 1:
                                st.session_state.generated_images = urls
                        else:
                            st.error("No URLs found in response.")
                            st.json(result)
                    except Exception as e:
                        st.error(f"Error: {e}")
                    

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

