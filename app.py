import streamlit as st
import openai
from openai import OpenAI
import requests
from PIL import Image
from io import BytesIO
import base64
import os

# Page configuration
st.set_page_config(
    page_title="SEOptimize AI Image Generator",
    page_icon="🎨",
    layout="centered"
)

# Custom CSS with SEOptimize branding (green theme from logo)
st.markdown("""
    <style>
    /* Main theme colors from SEOptimize */
    :root {
        --seo-green: #00D26A;
        --seo-dark: #1a1a1a;
        --seo-darker: #0d0d0d;
        --seo-light: #f5f5f5;
    }
    
    /* Dark theme background */
    .stApp {
        background-color: #0d0d0d;
    }
    
    /* Main content area */
    .main {
        padding-top: 2rem;
        background-color: #0d0d0d;
    }
    
    /* Headers and text */
    h1, h2, h3 {
        color: #ffffff !important;
    }
    
    /* Brand header */
    .brand-header {
        text-align: center;
        padding: 2rem 0;
        margin-bottom: 2rem;
        background: linear-gradient(135deg, #0d0d0d 0%, #1a1a1a 100%);
        border-radius: 12px;
        border: 1px solid #00D26A20;
    }
    
    .brand-text {
        font-size: 3rem;
        font-weight: 800;
        letter-spacing: -1px;
    }
    
    .seo-text {
        color: #ffffff;
    }
    
    .optimize-text {
        color: #00D26A;
    }
    
    .tagline {
        color: #888;
        font-size: 1.1rem;
        margin-top: 0.5rem;
    }
    
    /* Buttons with SEOptimize green */
    .stButton > button {
        background: linear-gradient(135deg, #00D26A 0%, #00B55A 100%);
        color: white;
        border-radius: 8px;
        padding: 0.75rem 2rem;
        font-weight: 600;
        border: none;
        width: 100%;
        margin-top: 1rem;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(0, 210, 106, 0.3);
    }
    
    .stButton > button:hover {
        background: linear-gradient(135deg, #00B55A 0%, #00A050 100%);
        box-shadow: 0 6px 20px rgba(0, 210, 106, 0.4);
        transform: translateY(-2px);
    }
    
    /* Sidebar styling */
    .css-1d391kg, [data-testid="stSidebar"] {
        background-color: #1a1a1a;
        border-right: 1px solid #00D26A20;
    }
    
    /* Input fields */
    .stTextInput > div > div > input,
    .stTextArea > div > div > textarea,
    .stSelectbox > div > div > div,
    .stNumberInput > div > div > input {
        background-color: #1a1a1a;
        color: #ffffff;
        border: 1px solid #00D26A30;
        border-radius: 8px;
    }
    
    .stTextInput > div > div > input:focus,
    .stTextArea > div > div > textarea:focus {
        border-color: #00D26A;
        box-shadow: 0 0 0 1px #00D26A40;
    }
    
    /* Sliders with green accent */
    .stSlider > div > div > div > div {
        background-color: #00D26A;
    }
    
    .stSlider > div > div > div > div > div {
        background-color: #00D26A;
        border: 2px solid #ffffff;
    }
    
    /* Radio buttons and checkboxes */
    .stRadio > div > label > div:first-child > div,
    .stCheckbox > label > div:first-child > div {
        border-color: #00D26A;
    }
    
    .stRadio > div > label > div:first-child > div[data-checked="true"],
    .stCheckbox > label > div:first-child > div[data-checked="true"] {
        background-color: #00D26A;
        border-color: #00D26A;
    }
    
    /* Expander styling */
    .streamlit-expanderHeader {
        background-color: #1a1a1a;
        color: #ffffff;
        border: 1px solid #00D26A30;
        border-radius: 8px;
    }
    
    .streamlit-expanderHeader:hover {
        border-color: #00D26A;
    }
    
    /* Success/Error/Warning messages */
    .stAlert > div {
        background-color: #1a1a1a;
        border-left: 4px solid #00D26A;
        color: #ffffff;
    }
    
    /* Info boxes */
    .info-box {
        background: linear-gradient(135deg, #1a1a1a 0%, #222 100%);
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #00D26A;
        margin-bottom: 1rem;
        color: #ffffff;
    }
    
    /* Download buttons */
    .stDownloadButton > button {
        background-color: #1a1a1a;
        border: 1px solid #00D26A;
        color: #00D26A;
    }
    
    .stDownloadButton > button:hover {
        background-color: #00D26A;
        color: #ffffff;
    }
    
    /* Footer styling */
    .footer {
        text-align: center;
        color: #888;
        padding: 2rem;
        border-top: 1px solid #00D26A20;
        margin-top: 3rem;
    }
    
    .footer a {
        color: #00D26A;
        text-decoration: none;
    }
    
    .footer a:hover {
        text-decoration: underline;
    }
    
    /* Selectbox dropdown */
    [data-baseweb="select"] {
        background-color: #1a1a1a;
    }
    
    /* Labels */
    .stSlider > label,
    .stTextInput > label,
    .stTextArea > label,
    .stSelectbox > label,
    .stNumberInput > label {
        color: #ffffff !important;
    }
    </style>
    """, unsafe_allow_html=True)

# SEOptimize Branded Header
st.markdown("""
    <div class="brand-header">
        <div class="brand-text">
            <span class="seo-text">SEO</span><span class="optimize-text">ptimize</span>
        </div>
        <div class="tagline">AI Image Generator</div>
    </div>
    """, unsafe_allow_html=True)

# Initialize session state
if 'api_key' not in st.session_state:
    # Check for API key in Streamlit secrets first (for deployment)
    if "OPENAI_API_KEY" in st.secrets:
        st.session_state.api_key = st.secrets["OPENAI_API_KEY"]
    else:
        st.session_state.api_key = ""
if 'generated_images' not in st.session_state:
    st.session_state.generated_images = []
if 'num_images' not in st.session_state:
    st.session_state.num_images = 1
if 'previous_model' not in st.session_state:
    st.session_state.previous_model = "gpt-image-1"

# API Key configuration in sidebar
with st.sidebar:
    st.markdown("""
        <div style="text-align: center; padding: 1rem 0; border-bottom: 1px solid #00D26A30;">
            <span style="color: #ffffff; font-size: 1.5rem; font-weight: 700;">
                SEO<span style="color: #00D26A;">ptimize</span>
            </span>
        </div>
    """, unsafe_allow_html=True)
    
    st.header("⚙️ Configuration")
    
    # API Key Management
    if not st.session_state.api_key:
        st.warning("⚠️ API Key Required")
        
        # Show instructions for Streamlit Secrets
        with st.expander("📚 How to add API Key"):
            st.markdown("""
            **For Streamlit Cloud (Recommended):**
            1. Go to your app's settings
            2. Navigate to **Secrets** tab
            3. Add the following:
            ```toml
            OPENAI_API_KEY = "sk-..."
            ```
            
            **For temporary use:**
            Enter your API key below (session only)
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
            st.rerun()
    
    st.markdown("---")
    
    # Model Selection
    st.subheader("🤖 Model Selection")
    model_choice = st.radio(
        "Choose Model",
        options=["gpt-image-1", "dall-e-3"],
        index=0,
        help="gpt-image-1 is the latest and most advanced model"
    )
    
    # Reset num_images when model changes
    if model_choice != st.session_state.previous_model:
        st.session_state.num_images = 1
        st.session_state.previous_model = model_choice
    
    if model_choice == "gpt-image-1":
        st.info("💫 Latest gpt-image-1 model")
    else:
        st.info("🎨 DALL-E 3 model")
    
    st.markdown("---")
    st.markdown("### About")
    st.markdown("""
    **Image Generation Models:**
    
    **gpt-image-1** 
    - Latest model
    - Up to 10 images
    - WebP support
    - Compression control
    
    **DALL-E 3**
    - Proven quality
    - Style modes
    - Single image
    """)
    
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; padding-top: 1rem;">
        <a href="https://seoptimizellc.com" target="_blank" style="color: #00D26A; text-decoration: none;">
            🌐 SEOptimize LLC
        </a>
    </div>
    """, unsafe_allow_html=True)

# Main content
col1, col2 = st.columns([3, 1])

with col1:
    prompt = st.text_area(
        "Enter your image prompt:",
        value="A majestic golden retriever sitting in a sunlit meadow, photorealistic, highly detailed",
        height=100,
        help="Describe the image you want to generate in detail"
    )

with col2:
    st.markdown("<br>", unsafe_allow_html=True)
    
# Parameter sliders in three columns
col1, col2, col3 = st.columns(3)

with col1:
    # Adjust max images based on model
    max_images = 10 if model_choice == "gpt-image-1" else 1
    
    # Ensure the current value doesn't exceed the max for the selected model
    current_value = min(st.session_state.num_images, max_images)
    
    num_images = st.slider(
        "Number of images",
        min_value=1,
        max_value=max_images,
        value=current_value,
        key="num_images_slider",
        help=f"Generate up to {max_images} images" + (" (batch generation)" if max_images > 1 else " (DALL-E 3 limit)")
    )
    st.session_state.num_images = num_images

with col2:
    quality_steps = st.slider(
        "Quality (steps)",
        min_value=10,
        max_value=50,
        value=20,
        help="Visual indicator - actual quality set in Advanced Settings"
    )

with col3:
    prompt_adherence = st.slider(
        "Prompt Adherence",
        min_value=1.0,
        max_value=10.0,
        value=7.5,
        step=0.5,
        help="How closely to follow the prompt"
    )

# Art style dropdown
art_style = st.selectbox(
    "Choose an art style",
    options=[
        "Realistic",
        "Artistic",
        "Anime/Manga",
        "Digital Art",
        "Oil Painting",
        "Watercolor",
        "Pencil Sketch",
        "3D Render",
        "Cartoon",
        "Photography",
        "Abstract",
        "Surreal",
        "Minimalist",
        "Vintage",
        "Cyberpunk"
    ],
    index=0,
    help="Select the artistic style for your image"
)

# Advanced Settings - DYNAMIC BASED ON MODEL
with st.expander("🔧 Advanced Settings"):
    adv_col1, adv_col2 = st.columns(2)
    
    with adv_col1:
        # Image Size - Different options for each model
        if model_choice == "gpt-image-1":
            image_size = st.selectbox(
                "Image Size",
                options=["1024x1024", "1536x1024", "1792x1024", "1024x1792"],
                index=0,
                help="Select the resolution (square images generate faster)"
            )
        else:  # DALL-E 3
            image_size = st.selectbox(
                "Image Size",
                options=["1024x1024", "1792x1024", "1024x1792"],
                index=0,
                help="Select the resolution (square images generate faster)"
            )
        
        # Image Quality - Different options for each model
        if model_choice == "gpt-image-1":
            image_quality = st.radio(
                "Image Quality",
                options=["high", "medium", "low"],
                index=0,
                help="Higher quality provides better details but costs more"
            )
        else:  # DALL-E 3
            image_quality = st.radio(
                "Image Quality",
                options=["standard", "hd"],
                index=1,
                help="HD provides finer details but costs more and takes longer"
            )
        
        # Style parameter - ONLY for DALL-E 3
        if model_choice == "dall-e-3":
            style_param = st.radio(
                "Style Mode",
                options=["vivid", "natural"],
                index=0,
                help="Vivid: More dramatic and hyper-real | Natural: More realistic and subdued"
            )
        else:
            style_param = None
        
        # Output Format - Different options for each model
        if model_choice == "gpt-image-1":
            output_format = st.selectbox(
                "Output Format",
                options=["png", "jpeg", "webp"],
                index=0,
                help="Choose the output image format (WebP offers better compression)"
            )
        else:  # DALL-E 3 typically only supports PNG
            output_format = "png"
            st.info("ℹ️ DALL-E 3 outputs PNG format")
    
    with adv_col2:
        negative_prompt = st.text_area(
            "Negative Prompt (optional)",
            placeholder="Things to avoid: blurry, low quality, distorted...",
            height=100,
            help="Describe what you don't want in the image"
        )
        
        seed = st.number_input(
            "Seed (optional)",
            min_value=-1,
            max_value=999999999,
            value=-1,
            help="Use -1 for random, or set a specific seed for reproducibility"
        )
        
        # gpt-image-1 specific parameters
        if model_choice == "gpt-image-1":
            st.markdown("**gpt-image-1 Settings:**")
            
            # Background parameter
            background_option = st.selectbox(
                "Background",
                options=["default", "transparent", "white", "black"],
                index=0,
                help="Set the background for images with transparency support"
            )
            
            # Output Compression
            output_compression = st.slider(
                "Output Compression",
                min_value=0,
                max_value=100,
                value=100,
                help="0 = no compression, 100 = maximum compression"
            )
        else:
            background_option = None
            output_compression = None

# Style modification based on selection
style_modifiers = {
    "Realistic": "photorealistic, highly detailed, professional photography, sharp focus",
    "Artistic": "artistic, creative, expressive brushstrokes, masterpiece",
    "Anime/Manga": "anime style, manga art, Japanese animation, cel shaded",
    "Digital Art": "digital painting, concept art, trending on artstation, highly detailed",
    "Oil Painting": "oil painting, classical art, museum quality, textured canvas",
    "Watercolor": "watercolor painting, soft colors, artistic, flowing pigments",
    "Pencil Sketch": "pencil drawing, sketch art, detailed linework, graphite",
    "3D Render": "3D rendered, octane render, unreal engine, ray tracing",
    "Cartoon": "cartoon style, animated, colorful illustration, cel animation",
    "Photography": "professional photography, DSLR quality, bokeh, rule of thirds",
    "Abstract": "abstract art, modern art, creative composition, non-representational",
    "Surreal": "surrealist art, dreamlike, Salvador Dali style, impossible geometry",
    "Minimalist": "minimalist, simple, clean lines, negative space, modern design",
    "Vintage": "vintage style, retro, nostalgic, aged film, classic aesthetic",
    "Cyberpunk": "cyberpunk, neon lights, futuristic, dystopian, tech noir"
}

# Generate button
if st.button("🎨 Generate Images", type="primary", use_container_width=True):
    if not st.session_state.api_key:
        st.error("⚠️ Please enter your OpenAI API key to generate images.")
        st.info("💡 Add your API key in the sidebar or configure it in Streamlit Secrets.")
    else:
        try:
            # Combine prompt with style modifier
            full_prompt = f"{prompt}, {style_modifiers.get(art_style, '')}"
            
            # Add negative prompt context if provided
            if negative_prompt:
                full_prompt += f". Avoid: {negative_prompt}"
            
            # Add seed to prompt if specified
            if seed != -1:
                full_prompt += f" [seed:{seed}]"
            
            # Show loading state
            with st.spinner(f"🎨 Generating {num_images} image(s) with {model_choice}..."):
                # Initialize OpenAI client without proxies parameter
                client = OpenAI(api_key=st.session_state.api_key)
                
                generated_images = []
                
                # Build parameters based on model
                if model_choice == "gpt-image-1":
                    # gpt-image-1 parameters
                    params = {
                        'model': model_choice,
                        'prompt': full_prompt,
                        'size': image_size,
                        'quality': image_quality,
                        'n': num_images,
                        'response_format': output_format
                    }
                    
                    # Add optional parameters if not default
                    if background_option and background_option != "default":
                        params['background'] = background_option
                    if output_compression is not None and output_compression != 100:
                        params['output_compression'] = output_compression
                    
                    try:
                        response = client.images.generate(**params)
                        
                        for img_data in response.data:
                            generated_images.append({
                                'url': img_data.url,
                                'prompt': full_prompt,
                                'revised_prompt': getattr(img_data, 'revised_prompt', full_prompt),
                                'model': model_choice,
                                'format': output_format
                            })
                    except Exception as e:
                        # Fallback to individual requests if batch fails
                        st.warning("Batch generation failed, generating individually...")
                        params['n'] = 1
                        for i in range(num_images):
                            response = client.images.generate(**params)
                            
                            generated_images.append({
                                'url': response.data[0].url,
                                'prompt': full_prompt,
                                'revised_prompt': getattr(response.data[0], 'revised_prompt', full_prompt),
                                'model': model_choice,
                                'format': output_format
                            })
                
                else:  # DALL-E 3
                    # DALL-E 3 requires individual requests
                    for i in range(num_images):
                        params = {
                            'model': model_choice,
                            'prompt': full_prompt,
                            'size': image_size,
                            'quality': image_quality,
                            'n': 1
                        }
                        
                        # Add style parameter for DALL-E 3
                        if style_param:
                            params['style'] = style_param
                        
                        response = client.images.generate(**params)
                        
                        generated_images.append({
                            'url': response.data[0].url,
                            'prompt': full_prompt,
                            'revised_prompt': getattr(response.data[0], 'revised_prompt', full_prompt),
                            'model': model_choice,
                            'format': 'png'
                        })
                
                st.session_state.generated_images = generated_images
                st.success(f"✅ Successfully generated {len(generated_images)} image(s) using {model_choice}!")
                
        except openai.AuthenticationError:
            st.error("❌ Authentication failed. Please check your API key.")
            st.info("💡 Make sure your API key is valid and has the necessary permissions.")
        except openai.PermissionDeniedError:
            st.error("❌ Permission denied. Your API key may not have access to this model.")
            st.info("💡 Try using the dall-e-3 model or check your API key permissions.")
        except Exception as e:
            st.error(f"❌ Error generating images: {str(e)}")
            if "gpt-image-1" in str(e).lower() or "model" in str(e).lower():
                st.info("💡 Try switching to dall-e-3 model in the sidebar if gpt-image-1 is not available for your account.")

# Display generated images
if st.session_state.generated_images:
    st.markdown("---")
    st.markdown("### 🖼️ Generated Images")
    
    # Display info about the generation
    st.info(f"Generated using **{st.session_state.generated_images[0]['model']}** model")
    
    for idx, img_data in enumerate(st.session_state.generated_images):
        col1, col2 = st.columns([3, 1])
        
        with col1:
            # Display image
            try:
                response = requests.get(img_data['url'])
                img = Image.open(BytesIO(response.content))
                st.image(img, caption=f"Image {idx + 1} ({img_data['model']})", use_column_width=True)
                
                # Show revised prompt in expander
                with st.expander(f"📝 Prompt Details for Image {idx + 1}"):
                    st.markdown("**Your prompt:**")
                    st.text(img_data['prompt'])
                    if img_data['revised_prompt'] != img_data['prompt']:
                        st.markdown("**AI interpreted prompt:**")
                        st.text(img_data['revised_prompt'])
            except Exception as e:
                st.error(f"Failed to load image {idx + 1}: {str(e)}")
        
        with col2:
            # Download button
            try:
                img_bytes = BytesIO()
                # Determine format based on the actual format used
                file_format = img_data.get('format', 'png')
                
                if file_format == 'webp':
                    # Save as WebP
                    img.save(img_bytes, format='WEBP', quality=95)
                    mime_type = "image/webp"
                elif file_format == 'jpeg':
                    img.save(img_bytes, format='JPEG', quality=95)
                    mime_type = "image/jpeg"
                else:  # PNG
                    img.save(img_bytes, format='PNG')
                    mime_type = "image/png"
                
                img_bytes = img_bytes.getvalue()
                
                st.download_button(
                    label=f"⬇️ Download",
                    data=img_bytes,
                    file_name=f"seo_image_{idx + 1}.{file_format}",
                    mime=mime_type,
                    key=f"download_{idx}"
                )
            except Exception as e:
                st.error(f"Download error: {str(e)}")

# Footer
st.markdown("---")
st.markdown(
    f"""
    <div class="footer">
        Powered by <a href="https://seoptimizellc.com" target="_blank">SEOptimize LLC</a> 
        | Model: {model_choice if 'model_choice' in locals() else 'gpt-image-1'}
        | <a href="https://platform.openai.com/docs/guides/image-generation" target="_blank">API Docs</a>
    </div>
    """,
    unsafe_allow_html=True
)
