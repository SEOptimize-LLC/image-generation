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
    page_title="Fast AI Image Generator",
    page_icon="✨",
    layout="centered"
)

# Custom CSS for styling
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
    .info-box {
        background-color: #fef3c7;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #f59e0b;
        margin-bottom: 1rem;
    }
    </style>
    """, unsafe_allow_html=True)

# Title
st.markdown("# ✨ Fast AI Image Generator ✨")
st.markdown("Generate AI images with OpenAI's latest image generation models", unsafe_allow_html=True)

# Initialize session state
if 'api_key' not in st.session_state:
    # Check for API key in Streamlit secrets first (for deployment)
    if "OPENAI_API_KEY" in st.secrets:
        st.session_state.api_key = st.secrets["OPENAI_API_KEY"]
    else:
        st.session_state.api_key = ""
if 'generated_images' not in st.session_state:
    st.session_state.generated_images = []

# API Key configuration in sidebar
with st.sidebar:
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
    
    if model_choice == "gpt-image-1":
        st.info("💫 Using latest gpt-image-1 model with enhanced capabilities")
    
    st.markdown("---")
    st.markdown("### About")
    st.markdown("""
    This app uses OpenAI's image generation API:
    
    **gpt-image-1** (Recommended)
    - Latest multimodal model
    - Higher quality outputs
    - Better text rendering
    - Multiple images per request
    - WebP format support
    - Compression control
    
    **DALL-E 3**
    - Previous generation
    - Still very capable
    - Single image per request
    - Style modes (vivid/natural)
    
    [API Documentation](https://platform.openai.com/docs/guides/image-generation)
    """)

# Check for organization verification notice
if st.session_state.api_key and model_choice == "gpt-image-1":
    with st.container():
        st.markdown("""
        <div class="info-box">
        <b>📋 Note:</b> The gpt-image-1 model may require organization verification. 
        If you encounter access issues, please verify your organization at 
        <a href="https://platform.openai.com/settings/organization/general" target="_blank">OpenAI Settings</a>.
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
    num_images = st.slider(
        "Number of images",
        min_value=1,
        max_value=max_images,
        value=1,
        help=f"Generate up to {max_images} images" + (" (gpt-image-1 supports batch generation)" if max_images > 1 else " (DALL-E 3 limitation)")
    )

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
            st.markdown("**gpt-image-1 Specific Settings:**")
            
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
                    if background_option != "default":
                        params['background'] = background_option
                    if output_compression != 100:
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
            st.error("❌ Permission denied. Your organization may need verification.")
            st.info("""
            📋 To use gpt-image-1, you may need to:
            1. Verify your organization at https://platform.openai.com/settings/organization/general
            2. Ensure your API key has image generation permissions
            3. Try using dall-e-3 model instead
            """)
        except Exception as e:
            st.error(f"❌ Error generating images: {str(e)}")
            if "gpt-image-1" in str(e).lower():
                st.info("💡 Try switching to dall-e-3 model in the sidebar if gpt-image-1 is not available.")

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
                    file_name=f"generated_{img_data['model']}_{idx + 1}.{file_format}",
                    mime=mime_type,
                    key=f"download_{idx}"
                )
            except Exception as e:
                st.error(f"Download error: {str(e)}")

# Footer
st.markdown("---")
st.markdown(
    f"""
    <div style='text-align: center; color: #888; padding: 1rem;'>
    Built with Streamlit and OpenAI's Image Generation API<br>
    Current Model: {model_choice if 'model_choice' in locals() else 'gpt-image-1'}<br>
    <a href="https://platform.openai.com/docs/guides/image-generation" target="_blank">API Documentation</a> | 
    <a href="https://platform.openai.com/settings/organization/general" target="_blank">Verify Organization</a>
    </div>
    """,
    unsafe_allow_html=True
)
