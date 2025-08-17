import streamlit as st
import os
from openai import OpenAI
import requests
from PIL import Image
from io import BytesIO
import time
import json

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
st.markdown("<p style='text-align: center; color: #666; font-size: 1.2rem;'>Transform your ideas into stunning visuals with the power of AI</p>", unsafe_allow_html=True)

# Sidebar configuration
st.sidebar.markdown("## ⚙️ Configuration")

# API Key handling with proper validation
api_key = None
api_key_input = st.sidebar.text_input(
    "OpenAI API Key",
    type="password",
    placeholder="sk-...",
    help="Enter your OpenAI API key. You can get one from https://platform.openai.com/api-keys"
)

# Try to get API key from multiple sources
if api_key_input:
    api_key = api_key_input
elif 'OPENAI_API_KEY' in st.secrets:
    api_key = st.secrets['OPENAI_API_KEY']
elif 'OPENAI_API_KEY' in os.environ:
    api_key = os.environ.get('OPENAI_API_KEY')

# Validate API key
if api_key and api_key.strip():
    if api_key.startswith('sk-'):
        st.session_state.api_key_validated = True
        st.sidebar.success("✅ API Key configured")
    else:
        st.session_state.api_key_validated = False
        st.sidebar.error("❌ Invalid API Key format. It should start with 'sk-'")
else:
    st.session_state.api_key_validated = False
    st.sidebar.warning("⚠️ Please enter your OpenAI API Key to continue")
    st.sidebar.info("""
    **How to get an API Key:**
    1. Go to [OpenAI Platform](https://platform.openai.com)
    2. Sign up or log in
    3. Navigate to API Keys section
    4. Create a new API key
    5. Copy and paste it here
    """)

# Model selection
model_choice = st.sidebar.selectbox(
    "Select Model",
    ["dall-e-3", "dall-e-2"],
    help="DALL-E 3 provides higher quality images with better prompt adherence"
)

# Image settings based on model
if model_choice == "dall-e-3":
    size_options = ["1024x1024", "1024x1792", "1792x1024"]
    quality_options = ["standard", "hd"]
    style_options = ["vivid", "natural"]
    
    size = st.sidebar.selectbox("Image Size", size_options)
    quality = st.sidebar.selectbox("Image Quality", quality_options, help="HD quality provides finer details but costs more")
    style = st.sidebar.selectbox("Style", style_options, help="Vivid: Hyper-real and dramatic | Natural: More natural, less hyper-real")
    n_images = 1  # DALL-E 3 only supports n=1
else:  # dall-e-2
    size_options = ["256x256", "512x512", "1024x1024"]
    size = st.sidebar.selectbox("Image Size", size_options)
    n_images = st.sidebar.slider("Number of Images", 1, 4, 1)
    quality = "standard"
    style = None

# Advanced settings
with st.sidebar.expander("Advanced Settings"):
    response_format = st.selectbox("Response Format", ["url", "b64_json"])
    timeout = st.slider("Timeout (seconds)", 30, 300, 60)
    
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
    
    if model_choice == "dall-e-3":
        estimated_cost = 0.04 if quality == "standard" else 0.08
    else:
        size_costs = {"256x256": 0.016, "512x512": 0.018, "1024x1024": 0.02}
        estimated_cost = size_costs.get(size, 0.02) * n_images
    
    st.metric("Estimated Cost", f"${estimated_cost:.3f}")

# Generate button
if st.button("🎨 Generate Image", type="primary", disabled=not st.session_state.api_key_validated):
    if not st.session_state.api_key_validated:
        st.error("❌ Please enter a valid OpenAI API key in the sidebar to generate images.")
    elif not prompt:
        st.warning("⚠️ Please enter a prompt to generate an image.")
    else:
        try:
            with st.spinner("🎨 Creating your masterpiece... This may take a moment..."):
                # Initialize OpenAI client with validated API key
                client = OpenAI(api_key=api_key.strip())
                
                # Prepare parameters based on model
                params = {
                    "model": model_choice,
                    "prompt": prompt,
                    "size": size,
                    "n": n_images,
                    "response_format": response_format
                }
                
                if model_choice == "dall-e-3":
                    params["quality"] = quality
                    params["style"] = style
                    params["n"] = 1  # DALL-E 3 only supports n=1
                
                # Generate image
                response = client.images.generate(**params)
                
                # Process and display results
                st.success("✅ Image generated successfully!")
                
                # Store in history
                generation_data = {
                    "prompt": prompt,
                    "model": model_choice,
                    "size": size,
                    "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
                    "images": []
                }
                
                # Display generated images
                if n_images == 1:
                    if response_format == "url":
                        image_url = response.data[0].url
                        image_response = requests.get(image_url)
                        img = Image.open(BytesIO(image_response.content))
                        st.image(img, caption=prompt, use_column_width=True)
                        generation_data["images"].append(image_url)
                        
                        # Download button
                        buf = BytesIO()
                        img.save(buf, format="PNG")
                        st.download_button(
                            label="📥 Download Image",
                            data=buf.getvalue(),
                            file_name=f"generated_{int(time.time())}.png",
                            mime="image/png"
                        )
                    else:
                        # Handle base64 response
                        import base64
                        image_data = base64.b64decode(response.data[0].b64_json)
                        img = Image.open(BytesIO(image_data))
                        st.image(img, caption=prompt, use_column_width=True)
                else:
                    # Multiple images (DALL-E 2 only)
                    cols = st.columns(min(n_images, 2))
                    for idx, image_data in enumerate(response.data):
                        with cols[idx % 2]:
                            if response_format == "url":
                                image_url = image_data.url
                                image_response = requests.get(image_url)
                                img = Image.open(BytesIO(image_response.content))
                                st.image(img, caption=f"Image {idx+1}", use_column_width=True)
                                generation_data["images"].append(image_url)
                                
                                # Download button for each image
                                buf = BytesIO()
                                img.save(buf, format="PNG")
                                st.download_button(
                                    label=f"📥 Download Image {idx+1}",
                                    data=buf.getvalue(),
                                    file_name=f"generated_{int(time.time())}_{idx+1}.png",
                                    mime="image/png",
                                    key=f"download_{idx}"
                                )
                
                # Update session state
                st.session_state.generated_images.append(generation_data)
                st.session_state.generation_history.append(generation_data)
                
                # Show generation details
                with st.expander("📋 Generation Details"):
                    st.json({
                        "model": model_choice,
                        "size": size,
                        "quality": quality if model_choice == "dall-e-3" else "standard",
                        "style": style if model_choice == "dall-e-3" else "N/A",
                        "prompt_tokens": len(prompt.split()),
                        "timestamp": generation_data["timestamp"]
                    })
                    
        except Exception as e:
            st.error(f"❌ An error occurred: {str(e)}")
            st.info("Please check your API key and try again. If the problem persists, verify your OpenAI account has access to DALL-E.")

# History section
if st.session_state.generation_history:
    st.markdown("---")
    st.markdown("### 📚 Generation History")
    
    for i, item in enumerate(reversed(st.session_state.generation_history[-5:])):
        with st.expander(f"🕐 {item['timestamp']} - {item['prompt'][:50]}..."):
            st.write(f"**Prompt:** {item['prompt']}")
            st.write(f"**Model:** {item['model']}")
            st.write(f"**Size:** {item['size']}")
            if item.get('images'):
                st.write(f"**Images Generated:** {len(item['images'])}")

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #888;'>
    <p>Built with ❤️ using Streamlit and OpenAI DALL-E | 
    <a href='https://platform.openai.com/docs/guides/images' target='_blank'>API Documentation</a> | 
    <a href='https://openai.com/pricing' target='_blank'>Pricing</a></p>
</div>
""", unsafe_allow_html=True)
