import os
from typing import Optional
from decouple import config as env_config

class Config:
    """Application configuration"""
    
    # Email Configuration
    EMAIL_ADDRESS: str = env_config('EMAIL_ADDRESS', default='')
    EMAIL_PASSWORD: str = env_config('EMAIL_PASSWORD', default='')
    SMTP_SERVER: str = env_config('SMTP_SERVER', default='smtp.gmail.com')
    SMTP_PORT: int = env_config('SMTP_PORT', default=587, cast=int)
    
    # Company Information
    COMPANY_NAME: str = env_config('COMPANY_NAME', default='HireSense AI')
    
    # Database Configuration
    DATABASE_URL: str = env_config('DATABASE_URL', default='sqlite:///hiring_assistant.db')
    
    # API Configuration
    API_HOST: str = env_config('API_HOST', default='0.0.0.0')
    API_PORT: int = env_config('API_PORT', default=8000, cast=int)
    
    # Security
    SECRET_KEY: str = env_config('SECRET_KEY', default='dev-secret-key-change-in-production')
    
    # AI Services (Free alternatives available)
    OPENAI_API_KEY: Optional[str] = env_config('OPENAI_API_KEY', default=None)  # Paid
    GROQ_API_KEY: Optional[str] = env_config('GROQ_API_KEY', default=None)  # Free tier available
    HUGGINGFACE_API_KEY: Optional[str] = env_config('HUGGINGFACE_API_KEY', default=None)  # Free
    MISTRAL_API_KEY: Optional[str] = env_config('MISTRAL_API_KEY', default=None)  # Affordable
    GEMINI_API_KEY: Optional[str] = env_config('GEMINI_API_KEY', default=None)  # Free tier available
    ANTHROPIC_API_KEY: Optional[str] = env_config('ANTHROPIC_API_KEY', default=None)  # Paid
    
    # Cloud Storage (Optional)
    AWS_ACCESS_KEY_ID: Optional[str] = env_config('AWS_ACCESS_KEY_ID', default=None)
    AWS_SECRET_ACCESS_KEY: Optional[str] = env_config('AWS_SECRET_ACCESS_KEY', default=None)
    AWS_BUCKET_NAME: Optional[str] = env_config('AWS_BUCKET_NAME', default=None)
    
    # Development Settings
    DEBUG: bool = env_config('DEBUG', default='True').lower() == 'true'
    LOG_LEVEL: str = env_config('LOG_LEVEL', default='INFO')
    
    # Local AI Configuration
    OLLAMA_HOST: str = env_config('OLLAMA_HOST', default='http://localhost:11434')
    OLLAMA_MODEL: str = env_config('OLLAMA_MODEL', default='llama2')
    LOCAL_AI_ENABLED: bool = env_config('LOCAL_AI_ENABLED', default='True').lower() == 'true'
    
    @classmethod
    def is_email_configured(cls) -> bool:
        """Check if email is properly configured"""
        return bool(cls.EMAIL_ADDRESS and cls.EMAIL_PASSWORD)
    
    @classmethod
    def get_email_config(cls) -> dict:
        """Get email configuration"""
        return {
            'server': cls.SMTP_SERVER,
            'port': cls.SMTP_PORT,
            'address': cls.EMAIL_ADDRESS,
            'password': cls.EMAIL_PASSWORD,
            'enabled': cls.is_email_configured()
        }
    
    @classmethod
    def print_config_status(cls):
        """Print configuration status for debugging"""
        print("🔧 Configuration Status:")
        print(f"   Company: {cls.COMPANY_NAME}")
        print(f"   Email: {'✅ Configured' if cls.is_email_configured() else '❌ Not configured'}")
        print(f"   Database: {cls.DATABASE_URL}")
        print(f"   Debug Mode: {'✅ Enabled' if cls.DEBUG else '❌ Disabled'}")
        print(f"   API: {cls.API_HOST}:{cls.API_PORT}")
        
        # AI Services Status
        print("🤖 AI Services:")
        ai_services = []
        if cls.GROQ_API_KEY:
            ai_services.append("✅ Groq (Free)")
        if cls.HUGGINGFACE_API_KEY:
            ai_services.append("✅ Hugging Face (Free)")
        if cls.GEMINI_API_KEY:
            ai_services.append("✅ Gemini (Free)")
        if cls.MISTRAL_API_KEY:
            ai_services.append("✅ Mistral (Affordable)")
        if cls.OPENAI_API_KEY:
            ai_services.append("✅ OpenAI (Paid)")
        if cls.ANTHROPIC_API_KEY:
            ai_services.append("✅ Anthropic (Paid)")
        
        # Check local options
        try:
            import requests
            response = requests.get(f"{cls.OLLAMA_HOST}/api/tags", timeout=2)
            if response.status_code == 200:
                ai_services.append("✅ Ollama (Local)")
        except:
            pass
        
        try:
            from transformers import pipeline
            ai_services.append("✅ Transformers (Local)")
        except ImportError:
            pass
        
        if ai_services:
            for service in ai_services:
                print(f"   {service}")
        else:
            print("   ❌ No AI services configured - using templates only")

# Create global config instance
config = Config() 