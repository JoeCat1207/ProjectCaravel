import aiohttp
import json
from typing import Dict
from config import API_KEYS
import asyncio
import traceback
import os
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

async def parse_prompt(prompt: str) -> Dict[str, str]:
    """
    Parse the user prompt into different categories using Claude 3.7 Sonnet.
    
    Returns a dictionary with categories as keys and content as values.
    Categories: general_knowledge, mathematics, coding, literature
    """
    system_prompt = """You are an expert at analyzing and categorizing content.
    Take the provided prompt and split its contents into these specific categories:
    1. general_knowledge
    2. mathematics
    3. coding
    4. literature/reading comprehension
    
    For each category, extract only the relevant portion of the prompt. If a category doesn't
    apply to the prompt, simply respond with 'Not Applicable' for that category.
    
    Format your response as a structured JSON object with the following keys:
    {
        "general_knowledge": "extracted content or Not Applicable",
        "mathematics": "extracted content or Not Applicable",
        "coding": "extracted content or Not Applicable",
        "literature": "extracted content or Not Applicable"
    }
    
    Provide only the JSON object in your response with no additional text."""
    
    # Number of retry attempts
    max_retries = 3
    retry_delay = 2  # seconds
    
    # Check if API key exists
    if not API_KEYS.get("claude"):
        logger.error("Claude API key is missing")
        return {
            "general_knowledge": prompt,
            "mathematics": "Not Applicable",
            "coding": "Not Applicable",
            "literature": "Not Applicable"
        }
    
    for attempt in range(max_retries):
        try:
            logger.info(f"Parsing prompt attempt {attempt+1}/{max_retries}")
            # Call Claude 3.7 Sonnet API
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    "https://api.anthropic.com/v1/messages",
                    headers={
                        "x-api-key": API_KEYS["claude"],
                        "anthropic-version": "2023-06-01",
                        "content-type": "application/json"
                    },
                    json={
                        "model": "claude-3-7-sonnet-20250219",
                        "max_tokens": 1024,
                        "system": system_prompt,
                        "messages": [
                            {"role": "user", "content": prompt}
                        ],
                        "temperature": 0.2
                    },
                    timeout=aiohttp.ClientTimeout(total=30)  # 30 second timeout
                ) as response:
                    if response.status != 200:
                        error_text = await response.text()
                        logger.error(f"API Error (Status {response.status}): {error_text}")
                        raise ValueError(f"API returned status code {response.status}: {error_text}")
                    
                    result = await response.json()
                    logger.info("Successfully received response from Claude API")
            
            # Extract and parse the JSON response
            try:
                response_text = result["content"][0]["text"]
                logger.info(f"Raw response: {response_text[:100]}...")
                
                # Extract JSON object if it's wrapped in ```json ``` or other formatting
                if "```json" in response_text:
                    json_text = response_text.split("```json")[1].split("```")[0].strip()
                elif "```" in response_text:
                    json_text = response_text.split("```")[1].split("```")[0].strip()
                else:
                    json_text = response_text.strip()
                
                categories = json.loads(json_text)
                
                # Ensure all expected categories are present
                for category in ["general_knowledge", "mathematics", "coding", "literature"]:
                    if category not in categories:
                        categories[category] = "Not Applicable"
                
                return categories
                
            except (KeyError, IndexError, json.JSONDecodeError) as e:
                logger.error(f"Error parsing response: {e}")
                logger.error(f"Response content: {result}")
                if attempt < max_retries - 1:
                    logger.info(f"Retrying in {retry_delay} seconds...")
                    await asyncio.sleep(retry_delay)
                else:
                    raise e
                
        except Exception as e:
            logger.error(f"API connection error (attempt {attempt+1}/{max_retries}): {str(e)}")
            traceback.print_exc()
            
            if attempt < max_retries - 1:
                logger.info(f"Retrying in {retry_delay} seconds...")
                await asyncio.sleep(retry_delay)
            else:
                logger.error(f"Failed to connect to Claude API after {max_retries} attempts")
                return {
                    "general_knowledge": prompt,
                    "mathematics": "Not Applicable",
                    "coding": "Not Applicable",
                    "literature": "Not Applicable"
                }