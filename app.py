import streamlit as st
import openai
from openai import OpenAI
import requests
from PIL import Image
from io import BytesIO
import base64

# Page configuration
st.set_page_config(
    page_title="Fast AI Image Generator",
    page_icon="✨",
    layout="centered"
)

# Custom CSS for styling (keeping your original)
st.markdown("""
    <style>
    .main {
        padding-top: 2rem;
    }
    .stButton > button {
        background-color: #ef4444;
        color: white;
        border-radius: 8px;
        padding: 0.5rem 2rem;
        font-weight: 600;
        border: none;
        width: 100%;
        margin-top: 1rem;
    }
    .stButton > button:hover {
        background-color: #dc2626;
    }
    h1 {
        text-align: center;
        padding-bottom: 2rem;
    }
    .stSelectbox > div > div {
        border-radius: 8px;
    }
    </style>
    """, unsafe_allow_html=True)

# Title
st.markdown("# ✨ Fast AI Image Generator ✨")
st.markdown("Generate AI images with optimized Stable Diffusion", unsafe_allow_html=True)

# Initialize session state
if 'api_key' not in st.session_state:
    st.session_state.api_key = ""
if 'generated_images' not in st.session_state:
    st.session_state.generated_images = []

# API Key input in sidebar
with st.sidebar:
    st.header("⚙️ Configuration")
    api_key = st.text_input(
        "OpenAI API Key",
        type="password",
        value=st.session_state.api_key,
        help="Enter your OpenAI API key to generate images"
    )
    if api_key:
        st.session_state.api_key = api_key
        # Fix for proxy error - use minimal initialization
        try:
            client = OpenAI(api_key=api_key)
        except TypeError:
            # Fallback for Streamlit Cloud proxy issues
            import os
            os.environ['OPENAI_API_KEY'] = api_key
            client = OpenAI()
    
    st.markdown("---")
    st.markdown("### About")
    st.markdown("""
    This app uses OpenAI's DALL-E 3 API to generate images based on your prompts.
    
    **Note:** The interface mimics Stable Diffusion parameters for familiarity, 
    but uses DALL-E 3 for generation.
    """)

# Main UI
prompt = st.text_area(
    "Enter your prompt",
    placeholder="A beautiful sunset over mountains, highly detailed, 8k resolution",
    height=100
)

# Model selection with gpt-image-1
col1, col2 = st.columns(2)

with col1:
    model = st.selectbox(
        "Model",
        options=["gpt-image-1", "dall-e-3", "dall-e-2"],
        format_func=lambda x: {
            "gpt-image-1": "OpenAI (GPT Image 1)",
            "dall-e-3": "DALL-E 3 (HD)",
            "dall-e-2": "DALL-E 2 (Fast)"
        }[x]
    )

with col2:
    if model == "dall-e-3":
        sizes = ["1024x1024", "1792x1024", "1024x1792"]
    else:
        sizes = ["256x256", "512x512", "1024x1024"]
    
    size = st.selectbox("Image Size", sizes)

# Advanced settings in expander
with st.expander("⚙️ Advanced Settings"):
    col1, col2 = st.columns(2)
    
    with col1:
        if model == "dall-e-3":
            quality = st.selectbox("Quality", ["standard", "hd"])
        else:
            quality = "standard"
        
        if model == "dall-e-2":
            num_images = st.slider("Number of Images", 1, 10, 1)
        else:
            num_images = 1
    
    with col2:
        # Response format - handle gpt-image-1 differently
        if model in ["dall-e-2", "dall-e-3"]:
            response_format = st.selectbox(
                "Response Format",
                ["url", "b64_json"],
                help="URL is faster, Base64 is more reliable"
            )
        else:
            # gpt-image-1 doesn't support response_format parameter
            st.info("gpt-image-1 always returns base64")
            response_format = None  # Don't send this parameter

# Generate button
if st.button("🎨 Generate", type="primary"):
    if not api_key:
        st.error("Please enter your OpenAI API key in the sidebar")
    elif not prompt:
        st.error("Please enter a prompt")
    else:
        with st.spinner("Generating..."):
            try:
                # Build parameters
                params = {
                    "model": model,
                    "prompt": prompt,
                    "size": size,
                    "n": num_images
                }
                
                # Add optional parameters
                if model == "dall-e-3":
                    params["quality"] = quality
                
                # Only add response_format for dall-e models
                if model in ["dall-e-2", "dall-e-3"]:
                    params["response_format"] = response_format
                
                # Generate image
                response = client.images.generate(**params)
                
                # Process response
                for img_data in response.data:
                    image_info = {
                        'prompt': prompt,
                        'model': model,
                        'size': size
                    }
                    
                    # Handle base64 response (gpt-image-1 always returns this)
                    if hasattr(img_data, 'b64_json') and img_data.b64_json:
                        # Decode base64
                        img_bytes = base64.b64decode(img_data.b64_json)
                        img = Image.open(BytesIO(img_bytes))
                        image_info['image'] = img
                    elif hasattr(img_data, 'url') and img_data.url:
                        # Download from URL
                        response = requests.get(img_data.url)
                        img = Image.open(BytesIO(response.content))
                        image_info['image'] = img
                        image_info['url'] = img_data.url
                    
                    st.session_state.generated_images.append(image_info)
                
                st.success(f"✅ Generated {num_images} image(s)!")
                
            except Exception as e:
                st.error(f"❌ Error: {str(e)}")
                if "response_format" in str(e):
                    st.info("Response format error detected. gpt-image-1 doesn't support response_format parameter.")
                else:
                    st.info("Please check your API key and model availability.")

# Display images
if st.session_state.generated_images:
    st.markdown("---")
    st.markdown("### Generated Images")
    
    for idx, img_data in enumerate(st.session_state.generated_images):
        col1, col2 = st.columns([4, 1])
        
        with col1:
            if 'image' in img_data:
                st.image(img_data['image'], caption=f"Image {idx + 1}", use_column_width=True)
            else:
                st.error(f"Could not load image {idx + 1}")
        
        with col2:
            if 'image' in img_data:
                # Download button
                img_bytes = BytesIO()
                img_data['image'].save(img_bytes, format='PNG')
                img_bytes = img_bytes.getvalue()
                
                st.download_button(
                    label="⬇️ Download",
                    data=img_bytes,
                    file_name=f"generated_{idx + 1}.png",
                    mime="image/png",
                    key=f"download_{idx}"
                )
