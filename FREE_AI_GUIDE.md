# 🆓 Free AI Alternatives Guide

This guide shows you how to use **completely free** AI services instead of paid OpenAI for your Agentic AI Hiring Assistant.

## 🌟 Why Use Free Alternatives?

- **💰 Zero Cost**: No API fees or subscription costs
- **🔒 Privacy**: Local models keep your data private
- **🚀 Performance**: Some free services are faster than OpenAI
- **🌍 Accessibility**: Available worldwide without payment restrictions

## 🆓 Free AI Options (Ranked by Ease of Use)

### 1. 🚀 Groq API (Recommended - FREE Tier)

**Best for**: Fast, high-quality AI responses with minimal setup

- **Cost**: FREE tier with generous limits (100+ requests/day)
- **Speed**: Extremely fast inference (faster than OpenAI)
- **Quality**: Uses Mixtral-8x7B model (comparable to GPT-3.5)
- **Setup**: Just need a free API key

**Setup Steps**:
1. Visit [console.groq.com](https://console.groq.com/)
2. Sign up for free account
3. Generate API key
4. Add to your `.env` file: `GROQ_API_KEY=your_key_here`

### 2. 🤗 Hugging Face API (FREE)

**Best for**: Access to many different models for free

- **Cost**: Completely FREE
- **Models**: Access to thousands of open-source models
- **Quality**: Good for most HR tasks
- **Setup**: Just need a free account

**Setup Steps**:
1. Visit [huggingface.co](https://huggingface.co/)
2. Sign up for free account
3. Generate access token in Settings
4. Add to your `.env` file: `HUGGINGFACE_API_KEY=your_token_here`

### 3. 🏠 Ollama (Local AI - Completely FREE)

**Best for**: Complete privacy and unlimited usage

- **Cost**: Completely FREE (runs on your computer)
- **Privacy**: 100% local, no data sent anywhere
- **Models**: Llama 2, Mistral, CodeLlama, and more
- **Quality**: Excellent for HR tasks

**Setup Steps**:
1. Install Ollama from [ollama.ai](https://ollama.ai/)
2. Download a model: `ollama pull llama2`
3. The system will auto-detect Ollama when running

### 4. 🤖 Local Transformers (Completely FREE)

**Best for**: Offline usage and complete control

- **Cost**: Completely FREE
- **Privacy**: 100% local processing
- **Models**: Automatically downloads small, efficient models
- **Quality**: Good for basic HR tasks

**Setup Steps**:
1. Install with: `pip install transformers torch`
2. Models download automatically on first use
3. Enable in `.env`: `LOCAL_AI_ENABLED=True`

## 📊 Comparison Table

| Service | Cost | Speed | Quality | Privacy | Setup Difficulty |
|---------|------|-------|---------|---------|------------------|
| Groq API | FREE | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| Hugging Face | FREE | ⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐ |
| Ollama | FREE | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ |
| Local Transformers | FREE | ⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| OpenAI | PAID | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐ | ⭐⭐⭐⭐⭐ |

## 🚀 Quick Start with Free AI

### Option 1: Groq (Fastest Setup)
```bash
# 1. Run setup script
python setup_real_functionality.py

# 2. When prompted for AI services:
#    - Skip local models if you want
#    - Enter your Groq API key
#    - Skip other services

# 3. Start the system
cd backend && python main.py
```

### Option 2: Local Models (Most Private)
```bash
# 1. Install dependencies
pip install transformers torch

# 2. Run setup script
python setup_real_functionality.py

# 3. When prompted:
#    - Enable local AI models
#    - Skip API services

# 4. Start the system
cd backend && python main.py
```

### Option 3: Ollama (Best Balance)
```bash
# 1. Install Ollama from ollama.ai
# 2. Download a model
ollama pull llama2

# 3. Run setup script
python setup_real_functionality.py

# 4. When prompted, confirm Ollama is installed

# 5. Start the system
cd backend && python main.py
```

## 🔧 Configuration Examples

### Groq Only (.env file)
```env
COMPANY_NAME=YourCompany
GROQ_API_KEY=gsk_your_groq_key_here
LOCAL_AI_ENABLED=False
```

### Local Models Only (.env file)
```env
COMPANY_NAME=YourCompany
LOCAL_AI_ENABLED=True
```

### Multiple Free Services (.env file)
```env
COMPANY_NAME=YourCompany
GROQ_API_KEY=gsk_your_groq_key_here
HUGGINGFACE_API_KEY=hf_your_token_here
LOCAL_AI_ENABLED=True
OLLAMA_MODEL=llama2
```

## 🎯 How the System Chooses AI Services

The system automatically tries services in this order:

1. **Groq API** (if configured) - Fastest
2. **Ollama** (if running) - Local and private
3. **Hugging Face API** (if configured) - Free cloud
4. **Local Transformers** (if installed) - Offline
5. **OpenAI** (if configured) - Paid fallback
6. **Templates** - Always works

## 💡 Tips for Best Results

### For Groq:
- Free tier has generous limits (100+ requests/day)
- Very fast responses (faster than OpenAI)
- High-quality Mixtral model
- Sign up at console.groq.com

### For Local Models:
- First run downloads models (may take time)
- Models are cached for future use
- Works completely offline
- No usage limits

### For Ollama:
- Install different models: `ollama pull mistral`
- Larger models = better quality but slower
- Runs in background automatically
- Great for development

## 🔍 Troubleshooting

### "No AI services configured"
- Check your `.env` file has at least one AI service
- Run `python setup_real_functionality.py` to reconfigure

### Groq API errors
- Verify your API key is correct
- Check you haven't exceeded free tier limits
- Ensure internet connection

### Local models slow
- First run downloads models (normal)
- Use smaller models for faster responses
- Consider using Groq for speed

### Ollama not detected
- Ensure Ollama is running: `ollama serve`
- Check if models are installed: `ollama list`
- Verify port 11434 is not blocked

## 🎉 Success! You're Using Free AI

Once configured, your system will:
- ✅ Generate personalized candidate messages
- ✅ Create professional email content
- ✅ Provide AI-powered insights
- ✅ Work without any paid subscriptions
- ✅ Maintain your privacy (with local options)

## 🆚 Free vs Paid Comparison

| Feature | Free AI | Paid AI (OpenAI) |
|---------|---------|------------------|
| Cost | $0/month | $20+/month |
| Quality | Excellent | Excellent |
| Speed | Very Fast (Groq) | Fast |
| Privacy | High (local options) | Medium |
| Limits | Generous/Unlimited | Pay per token |
| Setup | Easy | Easy |

**Recommendation**: Start with free options! They provide excellent results for HR tasks without any cost.

---

**Need Help?** 
- Run the setup script: `python setup_real_functionality.py`
- Check the main README.md for general setup
- All free options work great for HR assistant tasks! 