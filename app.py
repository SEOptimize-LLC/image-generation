import streamlit as st
import openai
from openai import OpenAI
import requests
from PIL import Image
from io import BytesIO
import base64

# Page configuration
st.set_page_config(
    page_title="SEOptimize AI Image Generator",
    page_icon="🎨",
    layout="centered"
)

# Professional CSS styling
st.markdown("""
    <style>
    /* Import Google Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    
    /* Root variables */
    :root {
        --seo-green: #00D26A;
        --seo-green-dark: #00A050;
        --bg-primary: #ffffff;
        --bg-secondary: #f8f9fa;
        --text-primary: #212529;
        --text-secondary: #6c757d;
        --border-color: #dee2e6;
        --shadow-sm: 0 2px 4px rgba(0,0,0,0.05);
        --shadow-md: 0 4px 6px rgba(0,0,0,0.07);
    }
    
    /* Global styles */
    .stApp {
        font-family: 'Inter', sans-serif;
        background: linear-gradient(135deg, #f8f9fa 0%, #ffffff 100%);
    }
    
    /* Brand header */
    .brand-header {
        text-align: center;
        padding: 2.5rem 0;
        margin-bottom: 2rem;
        background: white;
        border-radius: 16px;
        box-shadow: var(--shadow-md);
        border: 1px solid var(--border-color);
    }
    
    .brand-title {
        font-size: 3rem;
        font-weight: 700;
        margin-bottom: 0.5rem;
        letter-spacing: -1px;
    }
    
    .brand-seo {
        color: var(--text-primary);
    }
    
    .brand-optimize {
        color: var(--seo-green);
    }
    
    .brand-tagline {
        color: var(--text-secondary);
        font-size: 1.1rem;
        font-weight: 400;
    }
    
    /* Headers */
    h1, h2, h3 {
        color: var(--text-primary) !important;
        font-weight: 600 !important;
    }
    
    /* Main buttons */
    .stButton > button {
        background-color: var(--seo-green) !important;
        color: white !important;
        border-radius: 10px !important;
        padding: 0.75rem 2rem !important;
        font-weight: 600 !important;
        border: none !important;
        transition: all 0.3s ease !important;
        font-size: 1rem !important;
    }
    
    .stButton > button:hover {
        background-color: var(--seo-green-dark) !important;
        transform: translateY(-2px) !important;
        box-shadow: 0 4px 12px rgba(0, 210, 106, 0.3) !important;
    }
    
    /* Input fields */
    .stTextInput > div > div > input,
    .stTextArea > div > div > textarea {
        border-radius: 10px !important;
        border: 2px solid #e0e0e0 !important;
        padding: 0.75rem !important;
        font-size: 1rem !important;
        transition: border-color 0.3s ease !important;
    }
    
    .stTextInput > div > div > input:focus,
    .stTextArea > div > div > textarea:focus {
        border-color: var(--seo-green) !important;
        box-shadow: 0 0 0 2px rgba(0, 210, 106, 0.1) !important;
    }
    
    /* Select boxes */
    .stSelectbox > div > div {
        border-radius: 10px !important;
        border: 2px solid #e0e0e0 !important;
        padding: 0.25rem !important;
    }
    
    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 1rem;
        background-color: transparent !important;
        padding: 0.5rem;
    }
    
    .stTabs [data-baseweb="tab"] {
        padding: 0.75rem 1.5rem !important;
        background-color: white !important;
        border-radius: 10px !important;
        border: 2px solid #e0e0e0 !important;
        color: var(--text-secondary) !important;
        font-weight: 500 !important;
        transition: all 0.3s ease !important;
    }
    
    .stTabs [aria-selected="true"] {
        background-color: var(--seo-green) !important;
        color: white !important;
        border-color: var(--seo-green) !important;
    }
    
    /* Sliders */
    .stSlider > div > div {
        background-color: #e0e0e0 !important;
    }
    
    .stSlider > div > div > div {
        background-color: var(--seo-green) !important;
    }
    
    /* Info boxes */
    .stInfo {
        background-color: rgba(0, 210, 106, 0.1) !important;
        border-left: 4px solid var(--seo-green) !important;
        border-radius: 8px !important;
        padding: 1rem !important;
    }
    
    /* Success/Error messages */
    .stSuccess {
        background-color: rgba(0, 210, 106, 0.1) !important;
        color: var(--seo-green-dark) !important;
        border-radius: 8px !important;
        padding: 1rem !important;
    }
    
    .stError {
        border-radius: 8px !important;
        padding: 1rem !important;
    }
    
    /* Custom card style */
    .custom-card {
        background: white;
        border-radius: 12px;
        padding: 1.5rem;
        box-shadow: var(--shadow-sm);
        border: 1px solid var(--border-color);
        margin-bottom: 1.5rem;
    }
    
    /* Footer */
    .footer {
        text-align: center;
        padding: 2rem 0;
        margin-top: 3rem;
        border-top: 1px solid var(--border-color);
        color: var(--text-secondary);
    }
    
    .footer a {
        color: var(--seo-green);
        text-decoration: none;
        font-weight: 500;
    }
    
    .footer a:hover {
        text-decoration: underline;
    }
    
    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)

# Brand Header
st.markdown("""
    <div class="brand-header">
        <div class="brand-title">
            <span class="brand-seo">SEO</span><span class="brand-optimize">ptimize</span>
        </div>
        <div class="brand-tagline">AI-Powered Image Generation Platform</div>
    </div>
    """, unsafe_allow_html=True)

# Initialize session state
if 'api_key' not in st.session_state:
    st.session_state.api_key = ""
if 'generated_images' not in st.session_state:
    st.session_state.generated_images = []

# Sidebar Configuration
with st.sidebar:
    st.markdown("## ⚙️ Configuration")
    
    api_key = st.text_input(
        "OpenAI API Key",
        type="password",
        value=st.session_state.api_key,
        help="Enter your OpenAI API key to generate images"
    )
    
    if api_key:
        st.session_state.api_key = api_key
        # Fix for proxy error in Streamlit Cloud
        try:
            client = OpenAI(api_key=api_key)
        except TypeError:
            # Fallback if there's a proxy issue
            import os
            os.environ['OPENAI_API_KEY'] = api_key
            client = OpenAI()
    
    st.markdown("---")
    
    st.markdown("### 🎯 Quick Tips")
    st.info("""
    • Be specific and descriptive
    • Include style keywords
    • Mention colors and lighting
    • Add artistic references
    """)
    
    st.markdown("---")
    st.markdown("### 📊 Usage Stats")
    st.metric("Images Generated", len(st.session_state.generated_images))
    
    if st.button("🗑️ Clear Gallery", use_container_width=True):
        st.session_state.generated_images = []
        st.rerun()
    
    st.markdown("---")
    st.markdown("""
    <div style='text-align: center; padding-top: 1rem;'>
        <small>Powered by</small><br>
        <strong style='color: #00D26A;'>SEOptimize LLC</strong>
    </div>
    """, unsafe_allow_html=True)

# Main Content Area
col1, col2 = st.columns([2, 1])

with col1:
    prompt = st.text_area(
        "Enter your prompt",
        placeholder="A professional business photo, modern office, natural lighting, high quality...",
        height=100,
        help="Describe the image you want to generate"
    )

with col2:
    st.markdown("### 🎲 Prompt Enhancers")
    styles = ["Photorealistic", "Digital Art", "Oil Painting", "Watercolor", "3D Render", "Anime", "Minimalist"]
    selected_style = st.selectbox("Style Preset", ["None"] + styles)

# Tabs for settings
tab1, tab2 = st.tabs(["🎨 Basic Settings", "⚡ Advanced Settings"])

with tab1:
    col1, col2 = st.columns(2)
    
    with col1:
        # Model Selection - INCLUDING gpt-image-1
        models = {
            "gpt-image-1": "OpenAI (GPT Image 1)",
            "dall-e-3": "DALL·E 3 (Best Quality)",
            "dall-e-2": "DALL·E 2 (Fast)",
        }
        
        model = st.selectbox(
            "Select Model",
            options=list(models.keys()),
            format_func=lambda x: models[x],
            help="Choose the AI model for image generation"
        )
    
    with col2:
        # Size options based on model
        if model == "dall-e-3":
            sizes = ["1024x1024", "1792x1024", "1024x1792"]
        elif model == "dall-e-2":
            sizes = ["256x256", "512x512", "1024x1024"]
        else:  # gpt-image-1
            sizes = ["256x256", "512x512", "1024x1024"]
        
        size = st.selectbox(
            "Image Size",
            options=sizes,
            help="Resolution of the generated image"
        )
    
    col3, col4 = st.columns(2)
    
    with col3:
        if model == "dall-e-3":
            quality = st.selectbox(
                "Quality",
                options=["standard", "hd"],
                help="HD quality takes longer but produces better results"
            )
        else:
            quality = "standard"
            st.info("Quality setting only available for DALL·E 3")
    
    with col4:
        if model == "dall-e-2":
            max_images = 10
        else:
            max_images = 1
        
        num_images = st.number_input(
            "Number of Images",
            min_value=1,
            max_value=max_images,
            value=1,
            help=f"Maximum {max_images} images for {models[model]}"
        )

with tab2:
    col1, col2 = st.columns(2)
    
    with col1:
        output_format = st.selectbox(
            "Output Format",
            options=["png", "jpeg", "webp"],
            help="File format for downloads"
        )
        
        # FIX: Response format handling for different models
        if model in ["dall-e-2", "dall-e-3"]:
            response_format = st.selectbox(
                "Response Format",
                options=["url", "b64_json"],
                help="URL format is faster, Base64 is more reliable"
            )
        else:
            # gpt-image-1 ALWAYS returns base64, no parameter needed
            st.info("gpt-image-1 always returns base64-encoded images")
            response_format = None  # Don't send this parameter for gpt-image-1
    
    with col2:
        enhance_prompt = st.checkbox(
            "Auto-enhance prompt",
            value=True,
            help="Automatically improve your prompt for better results"
        )
        
        if model == "dall-e-3":
            style_option = st.selectbox(
                "Style Option",
                options=["vivid", "natural"],
                help="Vivid: hyper-real and dramatic. Natural: more natural, less hyper-real"
            )
        else:
            style_option = None

# Process prompt enhancement
if enhance_prompt and prompt:
    enhancement_additions = []
    if selected_style != "None":
        enhancement_additions.append(f"in {selected_style} style")
    
    if enhance_prompt:
        enhancement_additions.extend(["high quality", "detailed", "professional"])
    
    enhanced_prompt = f"{prompt}, {', '.join(enhancement_additions)}" if enhancement_additions else prompt
else:
    enhanced_prompt = prompt

# Display enhanced prompt
if prompt and enhance_prompt:
    with st.expander("📝 Enhanced Prompt"):
        st.text(enhanced_prompt)

# Generate button
if st.button("🎨 Generate Image", type="primary", use_container_width=True):
    if not st.session_state.api_key:
        st.error("⚠️ Please enter your OpenAI API key in the sidebar")
    elif not prompt:
        st.error("⚠️ Please enter a prompt")
    else:
        with st.spinner("🎨 Creating your image..."):
            try:
                # FIX: Build parameters correctly for each model
                params = {
                    "model": model,
                    "prompt": enhanced_prompt,
                    "size": size,
                    "n": num_images
                }
                
                # Add model-specific parameters
                if model == "dall-e-3":
                    params["quality"] = quality
                    if style_option:
                        params["style"] = style_option
                
                # FIX: Only add response_format for dall-e models, NOT for gpt-image-1
                if model in ["dall-e-2", "dall-e-3"] and response_format:
                    params["response_format"] = response_format
                # gpt-image-1 doesn't accept response_format parameter at all
                
                # Generate image
                response = client.images.generate(**params)
                
                # FIX: Process generated images with proper base64 handling
                for img_data in response.data:
                    image_info = {
                        'prompt': enhanced_prompt,
                        'model': model,
                        'size': size,
                        'format': output_format
                    }
                    
                    # FIX: Handle different response types
                    if hasattr(img_data, 'b64_json') and img_data.b64_json:
                        # gpt-image-1 always returns base64, or if b64_json was selected for dall-e
                        image_info['b64_json'] = img_data.b64_json
                        # Decode base64 to PIL Image
                        img_bytes = base64.b64decode(img_data.b64_json)
                        image_info['image'] = Image.open(BytesIO(img_bytes))
                    elif hasattr(img_data, 'url') and img_data.url:
                        # URL format for dall-e models
                        image_info['url'] = img_data.url
                        # Download image for display
                        img_response = requests.get(img_data.url)
                        image_info['image'] = Image.open(BytesIO(img_response.content))
                    else:
                        st.error("Unexpected response format from API")
                        continue
                    
                    st.session_state.generated_images.append(image_info)
                
                st.success(f"✅ Successfully generated {num_images} image(s)!")
                st.balloons()
                
            except Exception as e:
                error_msg = str(e)
                st.error(f"❌ Error: {error_msg}")
                
                if "404" in error_msg or "does not exist" in error_msg:
                    st.info("The selected model may not be available. Try using dall-e-3 or dall-e-2.")
                elif "response_format" in error_msg:
                    st.info("Response format error. Note: gpt-image-1 doesn't support the response_format parameter.")
                else:
                    st.info("Please check your API key and permissions.")

# Display Generated Images
if st.session_state.generated_images:
    st.markdown("---")
    st.markdown("### 🖼️ Generated Images")
    
    for idx, img_data in enumerate(st.session_state.generated_images):
        col1, col2 = st.columns([4, 1])
        
        with col1:
            try:
                # FIX: Display the PIL Image object directly
                if 'image' in img_data:
                    st.image(img_data['image'], caption=f"Image {idx + 1} ({img_data['model']})", use_column_width=True)
                else:
                    st.error(f"Could not display image {idx + 1}")
            except Exception as e:
                st.error(f"Could not display image {idx + 1}: {str(e)}")
        
        with col2:
            try:
                if 'image' in img_data:
                    # Prepare image for download
                    img_bytes = BytesIO()
                    file_format = img_data.get('format', 'png')
                    
                    if file_format == 'webp':
                        img_data['image'].save(img_bytes, format='WEBP', quality=95)
                        mime_type = "image/webp"
                    elif file_format == 'jpeg':
                        img_data['image'].save(img_bytes, format='JPEG', quality=95)
                        mime_type = "image/jpeg"
                    else:
                        img_data['image'].save(img_bytes, format='PNG')
                        mime_type = "image/png"
                    
                    img_bytes = img_bytes.getvalue()
                    
                    st.download_button(
                        label="⬇️ Download",
                        data=img_bytes,
                        file_name=f"seo_image_{idx + 1}.{file_format}",
                        mime=mime_type,
                        key=f"download_{idx}"
                    )
            except Exception as e:
                st.error(f"Download unavailable: {str(e)}")

# Footer
st.markdown("""
    <div class="footer">
        Powered by <a href="https://seoptimizellc.com" target="_blank">SEOptimize LLC</a> 
        • AI Image Generation Platform
    </div>
    """, unsafe_allow_html=True)
