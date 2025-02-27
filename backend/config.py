import os
from dotenv import load_dotenv

# Load API keys from environment
load_dotenv("api_keys.env")

# API keys
API_KEYS = {
    "gemini": os.getenv("GEMINI_API_KEY"),
    "claude": os.getenv("ANTHROPIC_API_KEY"),
}

# Directories for logging
PARSED_PROMPTS_DIR = "../logs/parsed_prompts"
GENERATED_PROMPTS_DIR = "../logs/generated_prompts"
