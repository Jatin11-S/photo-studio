Title
Photo Studio · AI Product Image Toolkit 

Overview
Photo Studio is a Streamlit app for creating studio‑grade product visuals in minutes: generate images from text, make clean packshots, add realistic shadows, compose lifestyle scenes, perform generative fill with a brush mask, and erase unwanted elements — all powered by Bria AI.

Features

Text‑to‑Image: HD generation with styles, aspect ratios, seed, and quality tweaks. 
Packshot: Clean product cutouts on custom or transparent backgrounds. 
Shadows: Natural, drop, and float shadows with intensity, blur, and offsets. 
Lifestyle shots: Scene composition via text prompt or a reference image, with smart placement controls. 
Generative Fill: Brush‑based mask to add or replace content contextually. 
Erase Elements: Remove distracting objects and regenerate the background. 
One‑click preview and download for every result. 

Demo

Local: streamlit run app.py 
Cloud: add BRIA_API_KEY to secrets and deploy on Streamlit Cloud. 

Project structure

photo-studio/
├─ app.py                  # Streamlit UI, tabs, and flow 
├─ photo_services/         # Service wrappers for Bria AI (requests + base64)
│  ├─ __init__.py          # Re-exports: enhance_prompt, generate_hd_image, ...
│  ├─ prompt_enhancement.py  # enhance_prompt() 
│  ├─ hd_image_generation.py  # generate_hd_image() 
│  ├─ packshot.py            # create_packshot() 
│  ├─ shadow.py              # add_shadow() 
│  ├─ lifestyle_shot.py      # lifestyle_shot_by_text(), lifestyle_shot_by_image()
│  ├─ generative_fill.py     # generative_fill() 
│  └─ erase_foreground.py    # erase_foreground() 
├─ components/             # Optional UI helpers (uploader, previews) 
├─ requirements.txt        # Python deps 
└─ .env                    # BRIA_API_KEY=... (not committed)

Requirements

Python 3.10+ recommended. [e4e40436]
Streamlit, Pillow, NumPy, requests, python‑dotenv, streamlit‑drawable‑canvas. [7863dc43]
A Bria AI API key (place in .env). [e4e40436]

Quick start

Clone and set up a venv
python -m venv venv
venv\Scripts\Activate.ps1 # Windows
source venv/bin/activate # macOS/Linux 
Install dependencies
pip install -r requirements.txt 
Add environment variable
Create .env with: BRIA_API_KEY=your_key_here 
Run
streamlit run app.py 

Usage

Generate: Enter a prompt, optionally enhance it, choose style/aspect/seed, and generate HD images. 
Product Photo:
Packshot: Picks background color and outputs a clean product shot. 
Shadow: Choose shadow type, intensity, blur, offset; optional transparent background. 
Lifestyle: Use a text scene or reference image; choose placement (automatic/manual/padding/custom). 
Generative Fill: Upload, draw a mask on the canvas, describe what to generate, and run. 
Erase Elements: Upload, paint over regions to remove, and run erase. 


