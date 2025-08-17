import streamlit as st
import os
from openai import OpenAI
import requests
from PIL import Image
from io import BytesIO
import time
import json
import base64

# Page configuration
st.set_page_config(
    page_title="AI Image Generator",
    page_icon="🎨",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for styling
st.markdown("""
    <style>
    .main {
        padding: 0rem 0rem;
    }
    .stButton>button {
        width: 100%;
        background-color: #4CAF50;
        color: white;
        font-weight: bold;
        border-radius: 10px;
        padding: 0.5rem;
        border: none;
        transition: all 0.3s;
    }
    .stButton>button:hover {
        background-color: #45a049;
        transform: scale(1.02);
    }
    .css-1d391kg {
        padding-top: 3rem;
    }
    .stTextInput>div>div>input {
        border-radius: 10px;
    }
    .stSelectbox>div>div>div {
        border-radius: 10px;
    }
    .generated-image {
        border-radius: 15px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    h1 {
        background: linear-gradient(45deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        font-size: 3rem;
        font-weight: bold;
        margin-bottom: 2rem;
    }
    h2, h3 {
        color: #333;
    }
    .sidebar .sidebar-content {
        background-color: #f5f5f5;
        border-radius: 10px;
        padding: 1rem;
    }
    .info-box {
        background-color: #e3f2fd;
        border-left: 4px solid #2196F3;
        padding: 1rem;
        border-radius: 5px;
        margin: 1rem 0;
    }
    .warning-box {
        background-color: #fff3e0;
        border-left: 4px solid #ff9800;
        padding: 1rem;
        border-radius: 5px;
        margin: 1rem 0;
    }
    .success-box {
        background-color: #e8f5e9;
        border-left: 4px solid #4caf50;
        padding: 1rem;
        border-radius: 5px;
        margin: 1rem 0;
    }
    .error-box {
        background-color: #ffebee;
        border-left: 4px solid #f44336;
        padding: 1rem;
        border-radius: 5px;
        margin: 1rem 0;
    }
    </style>
    """, unsafe_allow_html=True)

# Initialize session state
if 'generated_images' not in st.session_state:
    st.session_state.generated_images = []
if 'generation_history' not in st.session_state:
    st.session_state.generation_history = []
if 'api_key_validated' not in st.session_state:
    st.session_state.api_key_validated = False

# Title and description
st.markdown("<h1>🎨 AI Image Generator</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #666; font-size: 1.2rem;'>Transform your ideas into stunning visuals with GPT-Image-1</p>", unsafe_allow_html=True)

# Sidebar configuration
st.sidebar.markdown("## ⚙️ Configuration")

# API Key handling - Prioritize Streamlit Secrets
api_key = None

# First check Streamlit secrets
if 'OPENAI_API_KEY' in st.secrets:
    api_key = st.secrets['OPENAI_API_KEY']
    st.session_state.api_key_validated = True
    st.sidebar.success("✅ API Key configured from secrets")
else:
    # If no secrets, allow manual input
    api_key_input = st.sidebar.text_input(
        "OpenAI API Key",
        type="password",
        placeholder="sk-...",
        help="Enter your OpenAI API key. You can get one from https://platform.openai.com/api-keys"
    )
    
    if api_key_input:
        api_key = api_key_input
        if api_key.startswith('sk-'):
            st.session_state.api_key_validated = True
            st.sidebar.success("✅ API Key configured")
        else:
            st.session_state.api_key_validated = False
            st.sidebar.error("❌ Invalid API Key format")
    else:
        st.session_state.api_key_validated = False
        st.sidebar.warning("⚠️ Please configure your OpenAI API Key in Streamlit Secrets or enter it above")

# Image generation settings for gpt-image-1
st.sidebar.markdown("### Image Settings")

# Number of images
n_images = st.sidebar.slider(
    "Number of Images",
    min_value=1,
    max_value=10,
    value=1,
    help="Generate up to 10 images at once"
)

# Image size - gpt-image-1 specific sizes
size = st.sidebar.selectbox(
    "Image Size",
    ["auto", "1024x1024", "1536x1024", "1024x1536"],
    help="auto: Let the model decide | 1024x1024: Square | 1536x1024: Landscape | 1024x1536: Portrait"
)

# Image quality - gpt-image-1 specific options
quality = st.sidebar.selectbox(
    "Image Quality",
    ["auto", "high", "medium", "low"],
    help="auto: Model selects best quality | high: Best quality | medium: Balanced | low: Faster generation"
)

# Output format - gpt-image-1 specific
output_format = st.sidebar.selectbox(
    "Output Format",
    ["png", "jpeg", "webp"],
    help="Choose the file format for your generated images"
)

# Background - gpt-image-1 specific
background = st.sidebar.selectbox(
    "Background",
    ["auto", "transparent", "opaque"],
    help="auto: Model decides | transparent: Requires PNG or WebP format | opaque: Solid background"
)

# Validate background/format combination
if background == "transparent" and output_format == "jpeg":
    st.sidebar.warning("⚠️ JPEG doesn't support transparency. Switching to PNG.")
    output_format = "png"

# Advanced settings
with st.sidebar.expander("Advanced Settings"):
    # Output compression - only for JPEG and WebP
    if output_format in ["jpeg", "webp"]:
        output_compression = st.slider(
            "Compression Level (%)",
            min_value=0,
            max_value=100,
            value=100,
            help="Lower values = smaller file size but lower quality"
        )
    else:
        output_compression = None
    
    user_id = st.text_input(
        "User ID (Optional)",
        help="A unique identifier for end-user tracking"
    )

# Tips section
with st.sidebar.expander("💡 Prompt Tips"):
    st.markdown("""
    **For better results:**
    - Be specific and descriptive
    - Include style references (e.g., "oil painting", "photorealistic")
    - Mention lighting and mood
    - Specify colors and composition
    - Add artistic references
    
    **Example prompts:**
    - "A serene Japanese garden at sunset, oil painting style"
    - "Futuristic city with flying cars, cyberpunk aesthetic, neon lights"
    - "Portrait of a cat wearing a space suit, digital art style"
    """)

# Main content area
col1, col2 = st.columns([2, 1])

with col1:
    st.markdown("### 📝 Enter Your Prompt")
    prompt = st.text_area(
        "Describe the image you want to generate",
        placeholder="E.g., A majestic lion sitting on a throne in a medieval castle, oil painting style, dramatic lighting",
        height=100,
        help="Be as descriptive as possible for better results"
    )
    
    # Quick prompt suggestions
    st.markdown("**Quick Ideas:**")
    quick_prompts = [
        "A cozy coffee shop on a rainy day, warm lighting, watercolor style",
        "Abstract geometric patterns in vibrant colors, modern art style",
        "A magical forest with glowing mushrooms, fantasy art, ethereal atmosphere",
        "Retro-futuristic robot in a 1950s diner, vintage poster style"
    ]
    
    cols = st.columns(2)
    for i, quick_prompt in enumerate(quick_prompts):
        if cols[i % 2].button(f"💡 Idea {i+1}", key=f"quick_{i}"):
            st.session_state.quick_prompt = quick_prompt
            st.rerun()
    
    if 'quick_prompt' in st.session_state:
        prompt = st.session_state.quick_prompt
        del st.session_state.quick_prompt

with col2:
    st.markdown("### 📊 Generation Stats")
    st.metric("Total Images Generated", len(st.session_state.generated_images))
    st.metric("Current Session", len(st.session_state.generation_history))
    
    # Estimate cost (approximate)
    estimated_cost = 0.04 * n_images  # Adjust based on actual pricing
    st.metric("Estimated Cost", f"${estimated_cost:.3f}")

# Generate button
if st.button("🎨 Generate Image", type="primary", disabled=not st.session_state.api_key_validated):
    if not st.session_state.api_key_validated:
        st.error("❌ Please configure your OpenAI API key in the sidebar.")
    elif not prompt:
        st.warning("⚠️ Please enter a prompt to generate an image.")
    else:
        try:
            with st.spinner(f"🎨 Generating {n_images} image(s)... This may take a moment..."):
                # Initialize OpenAI client
                client = OpenAI(api_key=api_key)
                
                # Prepare parameters for gpt-image-1
                params = {
                    "model": "dall-e-3",  # This is what the API expects
                    "prompt": prompt,
                    "n": 1,  # API limitation - will loop if n_images > 1
                    "size": size,
                    "quality": quality,
                    "output_format": output_format,
                    "background": background
                }
                
                # Add compression if applicable
                if output_compression is not None:
                    params["output_compression"] = output_compression
                
                # Add optional user parameter
                if user_id:
                    params["user"] = user_id
                
                # Handle multiple images (make multiple API calls)
                all_images = []
                if n_images > 1:
                    progress_bar = st.progress(0)
                    for i in range(n_images):
                        response = client.images.generate(**params)
                        # gpt-image-1 always returns b64_json
                        img_data = base64.b64decode(response.data[0].b64_json)
                        img = Image.open(BytesIO(img_data))
                        all_images.append(img)
                        progress_bar.progress((i + 1) / n_images)
                    progress_bar.empty()
                else:
                    response = client.images.generate(**params)
                    # gpt-image-1 always returns b64_json
                    img_data = base64.b64decode(response.data[0].b64_json)
                    img = Image.open(BytesIO(img_data))
                    all_images.append(img)
                
                # Process and display results
                st.success(f"✅ {n_images} image(s) generated successfully!")
                
                # Store in history
                generation_data = {
                    "prompt": prompt,
                    "model": "gpt-image-1",
                    "size": size,
                    "quality": quality,
                    "background": background,
                    "output_format": output_format,
                    "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
                    "images_count": n_images
                }
                
                # Display generated images
                if n_images == 1:
                    st.image(all_images[0], caption=prompt, use_column_width=True)
                    
                    # Download button
                    buf = BytesIO()
                    if output_format == "png":
                        all_images[0].save(buf, format="PNG")
                        mime_type = "image/png"
                    elif output_format == "jpeg":
                        all_images[0].save(buf, format="JPEG", quality=output_compression or 100)
                        mime_type = "image/jpeg"
                    else:  # webp
                        all_images[0].save(buf, format="WEBP", quality=output_compression or 100)
                        mime_type = "image/webp"
                    
                    st.download_button(
                        label="📥 Download Image",
                        data=buf.getvalue(),
                        file_name=f"generated_{int(time.time())}.{output_format}",
                        mime=mime_type
                    )
                else:
                    # Multiple images
                    cols = st.columns(min(n_images, 3))
                    for idx, img in enumerate(all_images):
                        with cols[idx % 3]:
                            st.image(img, caption=f"Image {idx+1}", use_column_width=True)
                            
                            # Download button for each image
                            buf = BytesIO()
                            if output_format == "png":
                                img.save(buf, format="PNG")
                                mime_type = "image/png"
                            elif output_format == "jpeg":
                                img.save(buf, format="JPEG", quality=output_compression or 100)
                                mime_type = "image/jpeg"
                            else:  # webp
                                img.save(buf, format="WEBP", quality=output_compression or 100)
                                mime_type = "image/webp"
                            
                            st.download_button(
                                label=f"📥 Download {idx+1}",
                                data=buf.getvalue(),
                                file_name=f"generated_{int(time.time())}_{idx+1}.{output_format}",
                                mime=mime_type,
                                key=f"download_{idx}"
                            )
                
                # Update session state
                st.session_state.generated_images.extend([generation_data for _ in range(n_images)])
                st.session_state.generation_history.append(generation_data)
                
                # Show generation details
                with st.expander("📋 Generation Details"):
                    details = {
                        "model": "gpt-image-1",
                        "size": size,
                        "quality": quality,
                        "background": background,
                        "output_format": output_format,
                        "images_generated": n_images,
                        "prompt_tokens": len(prompt.split()),
                        "timestamp": generation_data["timestamp"],
                        "total_cost": f"${estimated_cost:.3f}"
                    }
                    if output_compression is not None:
                        details["compression"] = f"{output_compression}%"
                    st.json(details)
                    
        except Exception as e:
            st.error(f"❌ An error occurred: {str(e)}")
            st.info("Please check your API key and try again. If the problem persists, verify your OpenAI account has access to image generation.")

# History section
if st.session_state.generation_history:
    st.markdown("---")
    st.markdown("### 📚 Generation History")
    
    for i, item in enumerate(reversed(st.session_state.generation_history[-5:])):
        with st.expander(f"🕐 {item['timestamp']} - {item['prompt'][:50]}..."):
            st.write(f"**Prompt:** {item['prompt']}")
            st.write(f"**Model:** gpt-image-1")
            st.write(f"**Size:** {item['size']}")
            st.write(f"**Quality:** {item['quality']}")
            st.write(f"**Background:** {item['background']}")
            st.write(f"**Format:** {item['output_format']}")
            st.write(f"**Images Generated:** {item['images_count']}")

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #888;'>
    <p>Built with ❤️ using Streamlit and OpenAI GPT-Image-1 | 
    <a href='https://platform.openai.com/docs/guides/images' target='_blank'>API Documentation</a> | 
    <a href='https://openai.com/pricing' target='_blank'>Pricing</a></p>
</div>
""", unsafe_allow_html=True)
