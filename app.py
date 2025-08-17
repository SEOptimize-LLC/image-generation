import streamlit as st
import requests
from PIL import Image
from openai import OpenAI
from io import BytesIO
import os

# Import OpenAI and handle the initialization properly
try:
    import openai
    from openai import OpenAI
except ImportError:
    st.error("OpenAI library not installed")
    st.stop()

# Page configuration
st.set_page_config(
    page_title="SEOptimize AI Image Generator",
    page_icon="🎨",
    layout="centered"
)

# Professional CSS with subtle SEOptimize branding
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
    
    /* Buttons */
    .stButton > button {
        background: linear-gradient(135deg, var(--seo-green) 0%, var(--seo-green-dark) 100%);
        color: white;
        border: none;
        padding: 0.75rem 2rem;
        font-weight: 600;
        font-size: 1rem;
        border-radius: 10px;
        transition: all 0.3s ease;
        box-shadow: 0 4px 12px rgba(0, 210, 106, 0.25);
        width: 100%;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(0, 210, 106, 0.35);
    }
    
    /* Text inputs and text areas */
    .stTextInput > div > div > input,
    .stTextArea > div > div > textarea {
        border: 2px solid var(--border-color);
        border-radius: 10px;
        padding: 0.75rem;
        font-size: 1rem;
        transition: all 0.3s ease;
        background: white;
    }
    
    .stTextInput > div > div > input:focus,
    .stTextArea > div > div > textarea:focus {
        border-color: var(--seo-green);
        box-shadow: 0 0 0 3px rgba(0, 210, 106, 0.1);
        outline: none;
    }
    
    /* Select boxes */
    .stSelectbox > div > div {
        border-radius: 10px;
        border: 2px solid var(--border-color);
        background: white;
    }
    
    .stSelectbox > div > div:hover {
        border-color: var(--seo-green);
    }
    
    /* Sliders */
    .stSlider > div > div > div > div {
        background: linear-gradient(90deg, var(--seo-green-dark) 0%, var(--seo-green) 100%);
    }
    
    /* Radio buttons */
    .stRadio > div > label > div:first-child > div[data-checked="true"] {
        background-color: var(--seo-green);
        border-color: var(--seo-green);
    }
    
    /* Expander */
    .streamlit-expanderHeader {
        background: white;
        border: 1px solid var(--border-color);
        border-radius: 10px;
        font-weight: 500;
        transition: all 0.3s ease;
    }
    
    .streamlit-expanderHeader:hover {
        border-color: var(--seo-green);
        box-shadow: var(--shadow-sm);
    }
    
    /* Sidebar styling - NO PADDING, START AT TOP */
    section[data-testid="stSidebar"] {
        background: white;
        border-right: 1px solid var(--border-color);
    }
    
    section[data-testid="stSidebar"] > div:first-child {
        padding-top: 2.5rem !important;
    }
    
    /* Success/Error/Info messages */
    .stAlert {
        border-radius: 10px;
        border: none;
        box-shadow: var(--shadow-sm);
    }
    
    /* Download button */
    .stDownloadButton > button {
        background: white;
        color: var(--seo-green);
        border: 2px solid var(--seo-green);
        padding: 0.5rem 1.5rem;
        font-weight: 600;
        border-radius: 10px;
        transition: all 0.3s ease;
    }
    
    .stDownloadButton > button:hover {
        background: var(--seo-green);
        color: white;
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(0, 210, 106, 0.25);
    }
    
    /* Info badge */
    .info-badge {
        display: inline-block;
        background: rgba(0, 210, 106, 0.1);
        color: var(--seo-green-dark);
        padding: 0.25rem 0.75rem;
        border-radius: 20px;
        font-size: 0.875rem;
        font-weight: 600;
        margin-bottom: 1rem;
    }
    
    /* Footer */
    .footer {
        text-align: center;
        padding: 3rem 0 2rem;
        color: var(--text-secondary);
        font-size: 0.9rem;
    }
    
    .footer a {
        color: var(--seo-green);
        text-decoration: none;
        font-weight: 500;
    }
    
    .footer a:hover {
        text-decoration: underline;
    }
    </style>
    """, unsafe_allow_html=True)

# Helper function to create OpenAI client without proxy issues
@st.cache_resource
def get_openai_client(api_key):
    """Create OpenAI client with minimal configuration to avoid proxy issues"""
    # Remove any proxy-related environment variables temporarily
    proxy_vars = ['HTTP_PROXY', 'HTTPS_PROXY', 'http_proxy', 'https_proxy', 
                  'NO_PROXY', 'no_proxy', 'ALL_PROXY', 'all_proxy']
    saved_proxies = {}
    
    for var in proxy_vars:
        if var in os.environ:
            saved_proxies[var] = os.environ.pop(var)
    
    try:
        # Create client with absolute minimum configuration
        client = OpenAI(
            api_key=st.session_state.api_key
        return client
    finally:
        # Restore proxy settings
        for var, value in saved_proxies.items():
            os.environ[var] = value

# Brand Header
st.markdown("""
    <div class="brand-header">
        <div class="brand-title">
            <span class="brand-seo">SEO</span><span class="brand-optimize">ptimize</span>
        </div>
        <div class="brand-tagline">AI-Powered Image Generation</div>
    </div>
    """, unsafe_allow_html=True)

# Initialize session state
if 'api_key' not in st.session_state:
    if "OPENAI_API_KEY" in st.secrets:
        st.session_state.api_key = st.secrets["OPENAI_API_KEY"]
    else:
        st.session_state.api_key = ""
if 'generated_images' not in st.session_state:
    st.session_state.generated_images = []

# Sidebar - NO LOGO AT ALL
with st.sidebar:
    # Configuration Section STARTS IMMEDIATELY
    st.markdown("### ⚙️ Configuration")
    
    if not st.session_state.api_key:
        st.warning("⚠️ API Key Required")
        
        with st.expander("📚 How to add API Key"):
            st.markdown("""
            **For Streamlit Cloud:**
            1. Go to Settings → Secrets
            2. Add:
            ```toml
            OPENAI_API_KEY = "sk-..."
            ```
            
            **For temporary use:**
            Enter below (session only)
            """)
        
        api_key = st.text_input(
            "OpenAI API Key",
            type="password",
            placeholder="sk-...",
            help="Enter your OpenAI API key"
        )
        if api_key:
            st.session_state.api_key = api_key
            st.rerun()
    else:
        st.success("✅ API Key configured")
        if st.button("🔄 Change API Key"):
            st.session_state.api_key = ""
            # Clear the cached client
            get_openai_client.clear()
            st.rerun()
    
    st.markdown("---")
    
    # Model Selection - For now, only use models we know work
    st.markdown("### 🤖 Model Selection")
    model_choice = st.radio(
        "Choose Model",
        options=["dall-e-3", "dall-e-2"],
        index=0,
        help="Select the AI model for image generation",
        key="model_radio"
    )
    
    if model_choice == "dall-e-3":
        st.markdown('<span class="info-badge">Latest DALL-E</span>', unsafe_allow_html=True)
    else:
        st.markdown('<span class="info-badge">DALL-E 2</span>', unsafe_allow_html=True)
    
    st.markdown("---")
    
    # About Section
    st.markdown("### 📖 About")
    st.markdown("""
    **Models:**
    - **DALL-E 3**: Latest, best quality
    - **DALL-E 2**: Fast generation
    
    Note: gpt-image-1 coming soon!
    
    [🌐 SEOptimize LLC](https://seoptimizellc.com)
    """)

# Main Content Area
prompt = st.text_area(
    "✍️ **Enter your image prompt:**",
    value="A majestic golden retriever sitting in a sunlit meadow, photorealistic, highly detailed",
    height=100,
    help="Be descriptive for best results"
)

# Parameter Controls
col1, col2, col3 = st.columns(3)

with col1:
    # DALL-E 3 and 2 can only generate 1 image at a time
    num_images = st.slider(
        "Number of images",
        min_value=1,
        max_value=4,  # We'll make multiple API calls
        value=1,
        help="Will make multiple API calls for more than 1 image"
    )

with col2:
    quality_steps = st.slider(
        "Quality (steps)",
        min_value=10,
        max_value=50,
        value=20
    )

with col3:
    prompt_adherence = st.slider(
        "Prompt Adherence",
        min_value=1.0,
        max_value=10.0,
        value=7.5,
        step=0.5
    )

# Art Style Selection
art_style = st.selectbox(
    "🎨 **Choose an art style:**",
    options=[
        "Realistic", "Artistic", "Anime/Manga", "Digital Art",
        "Oil Painting", "Watercolor", "Pencil Sketch", "3D Render",
        "Cartoon", "Photography", "Abstract", "Surreal",
        "Minimalist", "Vintage", "Cyberpunk"
    ],
    index=0
)

# Advanced Settings
with st.expander("🔧 Advanced Settings"):
    adv_col1, adv_col2 = st.columns(2)
    
    with adv_col1:
        if model_choice == "dall-e-3":
            image_size = st.selectbox(
                "Image Size",
                options=["1024x1024", "1792x1024", "1024x1792"],
                index=0
            )
            image_quality = st.radio(
                "Image Quality",
                options=["standard", "hd"],
                index=1
            )
            style_param = st.radio(
                "Style Mode",
                options=["vivid", "natural"],
                index=0
            )
        else:  # dall-e-2
            image_size = st.selectbox(
                "Image Size", 
                options=["256x256", "512x512", "1024x1024"],
                index=2
            )
            image_quality = "standard"
            style_param = None
    
    with adv_col2:
        negative_prompt = st.text_area(
            "Negative Prompt (optional)",
            placeholder="Things to avoid...",
            height=100
        )
        
        seed = st.number_input(
            "Seed (optional)",
            min_value=-1,
            max_value=999999999,
            value=-1
        )

# Style modifiers
style_modifiers = {
    "Realistic": "photorealistic, highly detailed, professional photography",
    "Artistic": "artistic, creative, expressive brushstrokes",
    "Anime/Manga": "anime style, manga art, Japanese animation",
    "Digital Art": "digital painting, concept art, trending on artstation",
    "Oil Painting": "oil painting, classical art, museum quality",
    "Watercolor": "watercolor painting, soft colors, artistic",
    "Pencil Sketch": "pencil drawing, sketch art, detailed linework",
    "3D Render": "3D rendered, octane render, unreal engine",
    "Cartoon": "cartoon style, animated, colorful illustration",
    "Photography": "professional photography, DSLR quality, bokeh",
    "Abstract": "abstract art, modern art, creative composition",
    "Surreal": "surrealist art, dreamlike, Salvador Dali style",
    "Minimalist": "minimalist, simple, clean lines, negative space",
    "Vintage": "vintage style, retro, nostalgic, aged film",
    "Cyberpunk": "cyberpunk, neon lights, futuristic, dystopian"
}

# Generate Button
st.markdown("<br>", unsafe_allow_html=True)
if st.button("🎨 Generate Images", type="primary", use_container_width=True):
    if not st.session_state.api_key:
        st.error("⚠️ Please configure your OpenAI API key in the sidebar.")
    else:
        try:
            full_prompt = f"{prompt}, {style_modifiers.get(art_style, '')}"
            if negative_prompt:
                full_prompt += f". Avoid: {negative_prompt}"
            if seed != -1:
                full_prompt += f" [seed:{seed}]"
            
            with st.spinner(f"Creating {num_images} image(s)..."):
                # Get the cached client
                client = get_openai_client(st.session_state.api_key)
                
                generated_images = []
                
                # Generate images one by one
                for i in range(num_images):
                    try:
                        if model_choice == "dall-e-3":
                            response = client.images.generate(
                                model="dall-e-3",
                                prompt=full_prompt,
                                size=image_size,
                                quality=image_quality,
                                style=style_param,
                                n=1
                            )
                        else:  # dall-e-2
                            response = client.images.generate(
                                model="dall-e-2",
                                prompt=full_prompt,
                                size=image_size,
                                n=1
                            )
                        
                        generated_images.append({
                            'url': response.data[0].url,
                            'prompt': full_prompt,
                            'model': model_choice
                        })
                        
                    except Exception as e:
                        st.error(f"Error generating image {i+1}: {str(e)}")
                        break
                
                if generated_images:
                    st.session_state.generated_images = generated_images
                    st.success(f"✅ Successfully generated {len(generated_images)} image(s)!")
                
        except Exception as e:
            error_msg = str(e)
            st.error(f"❌ Error: {error_msg}")
            st.info("Please check your API key is valid and has image generation permissions.")

# Display Generated Images
if st.session_state.generated_images:
    st.markdown("---")
    st.markdown("### 🖼️ Generated Images")
    
    for idx, img_data in enumerate(st.session_state.generated_images):
        col1, col2 = st.columns([4, 1])
        
        with col1:
            try:
                response = requests.get(img_data['url'])
                img = Image.open(BytesIO(response.content))
                st.image(img, caption=f"Image {idx + 1} ({img_data['model']})", use_column_width=True)
            except:
                st.error(f"Could not load image {idx + 1}")
        
        with col2:
            try:
                img_bytes = BytesIO()
                img.save(img_bytes, format='PNG')
                img_bytes = img_bytes.getvalue()
                
                st.download_button(
                    label="⬇️ Download",
                    data=img_bytes,
                    file_name=f"seo_image_{idx + 1}.png",
                    mime="image/png",
                    key=f"download_{idx}"
                )
            except:
                st.error("Download unavailable")

# Footer
st.markdown("""
    <div class="footer">
        Powered by <a href="https://seoptimizellc.com" target="_blank">SEOptimize LLC</a> 
        • AI Image Generation Platform
    </div>
    """, unsafe_allow_html=True)
