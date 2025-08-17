#!/bin/bash

# Fast AI Image Generator - Setup Script
# This script helps you set up the project quickly

echo "✨ Fast AI Image Generator - Setup Script ✨"
echo "==========================================="
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.8+ first."
    exit 1
fi

echo "✅ Python 3 found: $(python3 --version)"
echo ""

# Create virtual environment
echo "📦 Creating virtual environment..."
python3 -m venv venv

# Activate virtual environment
echo "🔧 Activating virtual environment..."
if [[ "$OSTYPE" == "msys" ]] || [[ "$OSTYPE" == "win32" ]]; then
    # Windows
    source venv/Scripts/activate
else
    # Unix-like (Linux, macOS)
    source venv/bin/activate
fi

# Upgrade pip
echo "⬆️ Upgrading pip..."
pip install --upgrade pip

# Install requirements
echo "📚 Installing requirements..."
pip install -r requirements.txt

# Create .streamlit directory if it doesn't exist
if [ ! -d ".streamlit" ]; then
    echo "📁 Creating .streamlit directory..."
    mkdir .streamlit
fi

# Copy example secrets file if secrets.toml doesn't exist
if [ ! -f ".streamlit/secrets.toml" ]; then
    if [ -f ".streamlit/secrets.toml.example" ]; then
        echo "📋 Copying example secrets file..."
        cp .streamlit/secrets.toml.example .streamlit/secrets.toml
        echo ""
        echo "⚠️  IMPORTANT: Edit .streamlit/secrets.toml and add your OpenAI API key!"
        echo ""
    fi
fi

echo ""
echo "✅ Setup complete!"
echo ""
echo "Next steps:"
echo "1. Edit .streamlit/secrets.toml and add your OpenAI API key"
echo "2. Run the app with: streamlit run app.py"
echo ""
echo "For Streamlit Cloud deployment:"
echo "1. Push your code to GitHub (excluding secrets.toml)"
echo "2. Deploy on share.streamlit.io"
echo "3. Add OPENAI_API_KEY in the Streamlit Cloud Secrets tab"
echo ""
echo "Happy generating! 🎨"
