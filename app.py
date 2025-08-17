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
        client = OpenAI(api_key=api_key)
    
    st.markdown("---")
    st.markdown("### About")
    st.markdown("""
    This app uses OpenAI's DALL-E 3 API to generate images based on your prompts.
    
    **Note:** The interface mimics Stable Diffusion parameters for familiarity, 
    but uses DALL-E 3 for generation.
    """)

# Main content
col1, col2 = st.columns([3, 1])

with col1:
    prompt = st.text_area(
        "Enter your image prompt:",
        value="A majestic golden retriever sitting in a sunlit meadow, photorealistic, highly detailed",
        height=100,
        help="Describe the image you want to generate"
    )

with col2:
    st.markdown("<br>", unsafe_allow_html=True)
    
# Parameter sliders in three columns
col1, col2, col3 = st.columns(3)

with col1:
    num_images = st.slider(
        "Number of images",
        min_value=1,
        max_value=4,
        value=1,
        help="Number of images to generate (1-4)"
    )

with col2:
    quality_steps = st.slider(
        "Quality (steps)",
        min_value=10,
        max_value=50,
        value=20,
        help="Higher values = better quality but slower generation"
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
        "Surreal"
    ],
    index=0,
    help="Select the artistic style for your image"
)

# Advanced Settings
with st.expander("🔧 Advanced Settings"):
    adv_col1, adv_col2 = st.columns(2)
    
    with adv_col1:
        image_size = st.selectbox(
            "Image Size",
            options=["1024x1024", "1792x1024", "1024x1792"],
            index=0,
            help="Select the resolution of the generated image"
        )
        
        image_quality = st.radio(
            "Image Quality",
            options=["standard", "hd"],
            index=1,
            help="HD quality provides more detail but costs more"
        )
    
    with adv_col2:
        negative_prompt = st.text_area(
            "Negative Prompt (optional)",
            placeholder="Things to avoid in the image...",
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

# Style modification based on selection
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
    "Surreal": "surrealist art, dreamlike, Salvador Dali style"
}

# Generate button
if st.button("🎨 Generate Images", type="primary", use_container_width=True):
    if not st.session_state.api_key:
        st.error("⚠️ Please enter your OpenAI API key in the sidebar to generate images.")
    else:
        try:
            # Combine prompt with style modifier
            full_prompt = f"{prompt}, {style_modifiers.get(art_style, '')}"
            
            # Add negative prompt context if provided
            if negative_prompt:
                full_prompt += f". Avoid: {negative_prompt}"
            
            # Show loading state
            with st.spinner(f"🎨 Generating {num_images} image(s)..."):
                client = OpenAI(api_key=st.session_state.api_key)
                
                # Generate images
                generated_images = []
                for i in range(num_images):
                    response = client.images.generate(
                        model="dall-e-3",
                        prompt=full_prompt,
                        size=image_size,
                        quality=image_quality,
                        n=1  # DALL-E 3 only supports n=1
                    )
                    
                    image_url = response.data[0].url
                    generated_images.append({
                        'url': image_url,
                        'prompt': full_prompt,
                        'revised_prompt': response.data[0].revised_prompt
                    })
                
                st.session_state.generated_images = generated_images
                st.success(f"✅ Successfully generated {num_images} image(s)!")
                
        except Exception as e:
            st.error(f"❌ Error generating images: {str(e)}")
            if "api_key" in str(e).lower():
                st.info("💡 Make sure your OpenAI API key is valid and has access to DALL-E 3.")

# Display generated images
if st.session_state.generated_images:
    st.markdown("---")
    st.markdown("### 🖼️ Generated Images")
    
    for idx, img_data in enumerate(st.session_state.generated_images):
        col1, col2 = st.columns([3, 1])
        
        with col1:
            # Display image
            response = requests.get(img_data['url'])
            img = Image.open(BytesIO(response.content))
            st.image(img, caption=f"Image {idx + 1}", use_column_width=True)
            
            # Show revised prompt in expander
            with st.expander(f"📝 Prompt Details for Image {idx + 1}"):
                st.markdown("**Your prompt:**")
                st.text(img_data['prompt'])
                st.markdown("**DALL-E 3 interpreted prompt:**")
                st.text(img_data['revised_prompt'])
        
        with col2:
            # Download button
            img_bytes = BytesIO()
            img.save(img_bytes, format='PNG')
            img_bytes = img_bytes.getvalue()
            
            st.download_button(
                label=f"⬇️ Download",
                data=img_bytes,
                file_name=f"generated_image_{idx + 1}.png",
                mime="image/png",
                key=f"download_{idx}"
            )

# Footer
st.markdown("---")
st.markdown(
    """
    <div style='text-align: center; color: #888; padding: 1rem;'>
    Built with Streamlit and OpenAI DALL-E 3 API
    </div>
    """,
    unsafe_allow_html=True
)
