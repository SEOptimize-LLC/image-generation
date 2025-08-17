# ✨ Fast AI Image Generator ✨

A Streamlit-based web application for generating AI images using OpenAI's latest gpt-image-1 and DALL-E 3 APIs with an intuitive, Stable Diffusion-inspired interface.

## 🎯 Features

- **Dual Model Support**: Choose between gpt-image-1 (latest) and DALL-E 3
- **User-Friendly Interface**: Clean, modern UI with intuitive controls
- **Multiple Art Styles**: Choose from 15+ different artistic styles
- **Advanced Settings**: Control image size, quality, style, and generation parameters
- **Batch Generation**: Generate up to 10 images at once (gpt-image-1) or 1 (DALL-E 3)
- **Download Support**: Save generated images in PNG or JPEG format
- **Prompt Enhancement**: Automatic style modifiers based on selected art style
- **Negative Prompts**: Specify what you don't want in your images
- **Streamlit Secrets Integration**: Secure API key management

## 🚀 Live Demo

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://your-app-name.streamlit.app)

## 📦 Installation

### Local Development

1. Clone the repository:
```bash
git clone https://github.com/yourusername/fast-ai-image-generator.git
cd fast-ai-image-generator
```

2. **Quick Setup (Recommended):**
   - **Unix/macOS:** Run `bash setup.sh`
   - **Windows:** Run `setup.bat`
   
   Or manually:

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Configure your API key in `.streamlit/secrets.toml`:
```toml
OPENAI_API_KEY = "sk-your-api-key-here"
```

5. Run the app:
```bash
streamlit run app.py
```

6. Open your browser and navigate to `http://localhost:8501`

### Deployment to Streamlit Cloud

See [DEPLOYMENT.md](DEPLOYMENT.md) for detailed deployment instructions.

### Deployment to Streamlit Cloud

1. Fork this repository to your GitHub account

2. Go to [Streamlit Cloud](https://streamlit.io/cloud)

3. Click "New app" and select your forked repository

4. Set the main file path to `app.py`

5. Add your OpenAI API key in the Streamlit Cloud secrets:
   - Go to App Settings → Secrets
   - Add your secret in TOML format:
   ```toml
   OPENAI_API_KEY = "your-api-key-here"
   ```

6. Deploy! Your app will be live at `https://your-app-name.streamlit.app`

## 🔧 Configuration

### API Key Setup (Using Streamlit Secrets - Recommended)

For secure API key management, use Streamlit Secrets:

**For Local Development:**
1. Create a `.streamlit/secrets.toml` file in your project directory:
```toml
OPENAI_API_KEY = "sk-your-api-key-here"
```

**For Streamlit Cloud Deployment:**
1. Go to your app's dashboard on Streamlit Cloud
2. Click on **Settings** → **Secrets**
3. Add your secret in TOML format:
```toml
OPENAI_API_KEY = "sk-your-api-key-here"
```
4. Save and the app will automatically restart with the configured key

The app will automatically detect and use the API key from Streamlit Secrets.

### Model Access Requirements

**gpt-image-1 (Latest Model):**
- May require organization verification
- Visit [OpenAI Organization Settings](https://platform.openai.com/settings/organization/general) to verify
- Offers batch generation (up to 10 images per request)
- Higher quality outputs with better text rendering

**DALL-E 3:**
- Generally available without additional verification
- Single image generation per request
- Still produces excellent results

### Environment Variables

Create a `.env` file in the root directory (optional):
```env
OPENAI_API_KEY=your-api-key-here
```

## 📱 Usage

1. **API Key Configuration**: 
   - The app automatically detects API keys from Streamlit Secrets
   - Or enter manually in the sidebar for testing
2. **Select Model**: Choose between gpt-image-1 (recommended) or DALL-E 3
3. **Write Your Prompt**: Describe the image you want to generate
4. **Adjust Parameters**:
   - Number of images (1-10 for gpt-image-1, 1 for DALL-E 3)
   - Quality steps (visual indicator)
   - Prompt adherence (affects style parameter)
5. **Select Art Style**: Choose from 15+ artistic styles
6. **Advanced Settings** (Optional):
   - Image size (1024x1024, 1792x1024, 1024x1792)
   - Quality (standard/HD)
   - Style mode (vivid/natural)
   - Output format (PNG/JPEG for gpt-image-1)
   - Negative prompts
   - Seed for reproducibility
7. **Generate**: Click the "Generate Images" button
8. **Download**: Save your generated images

## 🎨 Available Art Styles

- Realistic
- Artistic
- Anime/Manga
- Digital Art
- Oil Painting
- Watercolor
- Pencil Sketch
- 3D Render
- Cartoon
- Photography
- Abstract
- Surreal
- Minimalist
- Vintage
- Cyberpunk

## 💰 Pricing

This app uses OpenAI's Image Generation API. Current pricing (as of 2025):

**gpt-image-1:**
- Standard Quality: ~$0.040 per image
- HD Quality: ~$0.080-0.120 per image (varies by size)

**DALL-E 3:**
- Standard Quality: $0.040 per image
- HD Quality: $0.080-0.120 per image (varies by size)

Check [OpenAI's pricing page](https://openai.com/pricing) for current rates.

## 🛠️ Tech Stack

- **Frontend**: Streamlit
- **Image Generation**: OpenAI gpt-image-1 & DALL-E 3 APIs
- **Image Processing**: Pillow (PIL)
- **HTTP Requests**: Requests library
- **Security**: Streamlit Secrets for API key management

## 📝 Project Structure

```
fast-ai-image-generator/
│
├── app.py                      # Main Streamlit application
├── requirements.txt            # Python dependencies
├── README.md                   # Project documentation
├── DEPLOYMENT.md              # Deployment guide
├── setup.sh                   # Unix/macOS setup script
├── setup.bat                  # Windows setup script
├── .gitignore                 # Git ignore file
└── .streamlit/                # Streamlit configuration
    ├── config.toml            # Theme and app settings
    ├── secrets.toml.example   # Example secrets file
    └── secrets.toml           # Your API keys (create this, don't commit!)
```

## ⚙️ Streamlit Configuration

Create `.streamlit/config.toml` for custom theme:

```toml
[theme]
primaryColor = "#ef4444"
backgroundColor = "#ffffff"
secondaryBackgroundColor = "#f0f2f6"
textColor = "#262730"
font = "sans serif"

[server]
maxUploadSize = 10
```

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- OpenAI for the DALL-E 3 API
- Streamlit for the amazing web framework
- The open-source community for inspiration

## 🐛 Known Issues

- gpt-image-1 may require organization verification for some accounts
- DALL-E 3 only supports generating 1 image per API call (batch generation makes multiple calls)
- Some style modifiers may conflict with certain prompts
- Rate limits apply based on your OpenAI account tier
- Image generation costs vary based on model, quality, and size settings

## 📧 Support

For support, please open an issue in the GitHub repository or contact [your-email@example.com]

## 🔮 Future Enhancements

- [ ] Image editing capabilities (using gpt-image-1's edit features)
- [ ] Image variations generation
- [ ] Prompt history and favorites
- [ ] Gallery of generated images with database storage
- [ ] Integration with other AI models
- [ ] Image-to-image generation
- [ ] Prompt templates library
- [ ] Export to various formats (WebP, AVIF)
- [ ] Social sharing features
- [ ] Cost tracking and usage analytics
- [ ] Custom style presets
- [ ] Bulk download functionality

---

Made with ❤️ using Streamlit and OpenAI's gpt-image-1 & DALL-E 3 APIs
