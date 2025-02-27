import aiohttp
import json
import logging
from typing import Dict, List, Optional
from config import API_KEYS

# Set up logging
logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

async def route_to_llms(generated_prompts: Dict[str, str]) -> Dict[str, str]:
    """
    Route each prompt to the appropriate LLM based on the category.
    
    Arguments:
        generated_prompts: Dictionary with categories as keys and generated prompts as values
        
    Returns:
        Dictionary with categories as keys and LLM responses as values
    """
    responses = {}
    tasks = []
    
    # Check if keys exist
    if not API_KEYS.get("gemini"):
        logger.error("Gemini API key is missing")
    if not API_KEYS.get("claude"):
        logger.error("Claude API key is missing")
    
    # Process each category in parallel
    for category, prompt in generated_prompts.items():
        if prompt != "Not Applicable":
            if category == "mathematics" and API_KEYS.get("gemini"):
                task = process_math_with_gemini(prompt)
                tasks.append((category, task))
            elif category == "coding" and API_KEYS.get("claude"):
                task = process_coding_with_claude_37(prompt)
                tasks.append((category, task))
            elif category == "literature" and API_KEYS.get("claude"):
                task = process_literature_with_claude_35(prompt)
                tasks.append((category, task))
            elif category == "general_knowledge" and API_KEYS.get("claude"):
                task = process_general_with_claude_37(prompt)
                tasks.append((category, task))
            else:
                logger.warning(f"Skipping category {category} due to missing API key or unsupported category")
                responses[category] = f"Cannot process {category} - missing API key or unsupported category"
    
    # Await all tasks
    for category, task in tasks:
        try:
            responses[category] = await task
            logger.info(f"Successfully processed {category}")
        except Exception as e:
            logger.error(f"Error processing {category}: {str(e)}")
            responses[category] = f"Error processing {category}: {str(e)}"
    
    return responses

async def process_general_with_claude_37(prompt: str) -> str:
    """Process general knowledge queries with Claude 3.7 Sonnet."""
    logger.info("Processing general knowledge with Claude 3.7")
    return await call_claude_37(
        "You are a helpful assistant addressing general knowledge questions.",
        prompt
    )

async def process_math_with_gemini(prompt: str) -> str:
    """Process math queries with Gemini 2.0 Flash."""
    logger.info("Processing mathematics with Gemini 2.0 Flash")
    api_key = API_KEYS["gemini"]
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(
                "https://generativelanguage.googleapis.com/v1/models/gemini-2.0-flash:generateContent",
                params={"key": api_key},
                json={
                    "contents": [
                        {
                            "role": "user",
                            "parts": [{"text": prompt}]
                        }
                    ],
                    "generationConfig": {
                        "temperature": 0.2,
                        "maxOutputTokens": 2048
                    }
                },
                timeout=aiohttp.ClientTimeout(total=30)
            ) as response:
                if response.status != 200:
                    error_text = await response.text()
                    logger.error(f"Gemini API Error (Status {response.status}): {error_text}")
                    return f"Error from Gemini API (Status {response.status}): {error_text}"
                    
                result = await response.json()
        
        # Extract the response from Gemini API response
        try:
            return result["candidates"][0]["content"]["parts"][0]["text"]
        except (KeyError, IndexError) as e:
            logger.error(f"Error extracting Gemini response: {e}")
            logger.error(f"Gemini result: {json.dumps(result)}")
            return f"Error processing mathematics with Gemini: {str(e)}"
    except Exception as e:
        logger.error(f"Exception calling Gemini API: {str(e)}")
        return f"Error calling Gemini API: {str(e)}"

async def process_coding_with_claude_37(prompt: str) -> str:
    """Process coding queries with Claude 3.7 Sonnet."""
    logger.info("Processing coding with Claude 3.7")
    return await call_claude_37(
        "You are a helpful programming assistant that explains code clearly and provides well-structured, efficient solutions.",
        prompt
    )

async def process_literature_with_claude_35(prompt: str) -> str:
    """Process literature/reading comprehension with Claude 3.5 Haiku."""
    logger.info("Processing literature with Claude 3.5 Haiku")
    api_key = API_KEYS["claude"]
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(
                "https://api.anthropic.com/v1/messages",
                headers={
                    "x-api-key": api_key,
                    "anthropic-version": "2023-06-01",
                    "content-type": "application/json"
                },
                json={
                    "model": "claude-3-5-haiku-20241022",
                    "max_tokens": 4096,
                    "system": "You are a literary analysis and reading comprehension expert who provides insightful, nuanced interpretations.",
                    "messages": [
                        {"role": "user", "content": prompt}
                    ]
                },
                timeout=aiohttp.ClientTimeout(total=30)
            ) as response:
                if response.status != 200:
                    error_text = await response.text()
                    logger.error(f"Claude API Error (Status {response.status}): {error_text}")
                    return f"Error from Claude API (Status {response.status}): {error_text}"
                    
                result = await response.json()
        
        # Extract the response from Claude API response
        try:
            return result["content"][0]["text"]
        except (KeyError, IndexError) as e:
            logger.error(f"Error extracting Claude 3.5 response: {e}")
            logger.error(f"Claude result: {json.dumps(result)}")
            return f"Error processing literature with Claude 3.5 Haiku: {str(e)}"
    except Exception as e:
        logger.error(f"Exception calling Claude 3.5 API: {str(e)}")
        return f"Error calling Claude 3.5 API: {str(e)}"

async def call_claude_37(system_prompt: str, prompt: str) -> str:
    """Call Claude 3.7 Sonnet API with the given system prompt and user prompt."""
    api_key = API_KEYS["claude"]
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(
                "https://api.anthropic.com/v1/messages",
                headers={
                    "x-api-key": api_key,
                    "anthropic-version": "2023-06-01",
                    "content-type": "application/json"
                },
                json={
                    "model": "claude-3-7-sonnet-20250219",
                    "max_tokens": 4096,
                    "system": system_prompt,
                    "messages": [
                        {"role": "user", "content": prompt}
                    ]
                },
                timeout=aiohttp.ClientTimeout(total=30)
            ) as response:
                if response.status != 200:
                    error_text = await response.text()
                    logger.error(f"Claude API Error (Status {response.status}): {error_text}")
                    return f"Error from Claude API (Status {response.status}): {error_text}"
                    
                result = await response.json()
        
        # Extract the response
        try:
            return result["content"][0]["text"]
        except (KeyError, IndexError) as e:
            logger.error(f"Error extracting Claude 3.7 response: {e}")
            logger.error(f"Claude result: {json.dumps(result)}")
            return f"Error processing with Claude 3.7: {str(e)}"
    except Exception as e:
        logger.error(f"Exception calling Claude 3.7 API: {str(e)}")
        return f"Error calling Claude 3.7 API: {str(e)}"

async def generate_structured_prompt(category: str, content: str) -> str:
    """
    Generate an optimized prompt for a specific category using Claude 3.7 Sonnet.
    
    Arguments:
        category: The category of the content
        content: The raw content to structure
        
    Returns:
        A structured prompt optimized for the target LLM
    """
    logger.info(f"Generating structured prompt for {category}")
    category_descriptions = {
        "general_knowledge": "general knowledge questions",
        "mathematics": "mathematical problems or equations",
        "coding": "programming tasks or code explanations",
        "literature": "literary analysis or reading comprehension"
    }
    
    system_prompt = f"""You are an expert at creating structured prompts for AI language models.
    Take the provided content related to {category_descriptions.get(category, "a specific topic")} and create
    a clear, well-structured prompt that will help another AI model provide the best possible response.
    
    Focus on:
    1. Clarifying any ambiguities in the original content
    2. Organizing the information logically
    3. Highlighting key questions or requirements
    4. Providing necessary context
    
    Your output should be just the reformulated prompt with no additional explanations or meta-commentary."""
    
    return await call_claude_37(system_prompt, content)