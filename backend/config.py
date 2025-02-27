import os
import logging
from dotenv import load_dotenv

# Set up logging
logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Try to load from the specified path
env_path = "backend/api_keys.env"
if os.path.exists(env_path):
    logger.info(f"Loading environment from {env_path}")
    load_dotenv(env_path)
else:
    # Try alternative paths
    alt_paths = [
        "api_keys.env",
        "../api_keys.env",
        os.path.join(os.path.dirname(os.path.abspath(__file__)), "api_keys.env")
    ]
    
    for path in alt_paths:
        if os.path.exists(path):
            logger.info(f"Loading environment from {path}")
            load_dotenv(path)
            break
    else:
        logger.warning("Could not find api_keys.env file")

# API keys
API_KEYS = {
    "gemini": os.getenv("GEMINI_API_KEY"),
    "claude": os.getenv("ANTHROPIC_API_KEY"),
}

# Log status of API keys (without revealing the actual keys)
for key, value in API_KEYS.items():
    if value:
        logger.info(f"{key.upper()} API key is configured")
    else:
        logger.warning(f"{key.upper()} API key is missing")

# Directories for logging
PARSED_PROMPTS_DIR = os.getenv("PARSED_PROMPTS_DIR", "../logs/parsed_prompts")
GENERATED_PROMPTS_DIR = os.getenv("GENERATED_PROMPTS_DIR", "../logs/generated_prompts")

# Create directories if they don't exist
os.makedirs(PARSED_PROMPTS_DIR, exist_ok=True)
os.makedirs(GENERATED_PROMPTS_DIR, exist_ok=True)

# API rate limiting settings
RATE_LIMIT_REQUESTS = int(os.getenv("RATE_LIMIT_REQUESTS", "15"))  # Maximum requests per minute
RATE_LIMIT_WINDOW = int(os.getenv("RATE_LIMIT_WINDOW", "100"))     # Window in seconds