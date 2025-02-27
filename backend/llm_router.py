import aiohttp
import os
import json
from typing import Dict
import time
from config import API_KEYS

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
    
    # Process each category in parallel
    for category, prompt in generated_prompts.items():
        if prompt != "Not Applicable":
            if category == "mathematics":
                task = process_math_with_gemini(prompt)
            elif category == "coding":
                task = process_coding_with_claude_37(prompt)
            elif category == "literature":
                task = process_literature_with_claude_35(prompt)
            elif category == "general_knowledge":
                task = process_general_with_deepseek(prompt)
            else:
                continue
                
            tasks.append((category, task))
    
    # Await all tasks
    for category, task in tasks:
        responses[category] = await task
    
    return responses

async def call_deepseek_ollama(system_prompt: str, prompt: str) -> str:
    """Call the local Ollama instance running Deepseek R1 14B."""
    async with aiohttp.ClientSession() as session:
        async with session.post(
            "http://ollama:11434/api/generate",
            json={
                "model": "deepseek-r1:14b",
                "prompt": prompt,
                "system": system_prompt,
                "stream": False
            }
        ) as response:
            result = await response.json()
            
    return result.get("response", "")

async def process_general_with_deepseek(prompt: str) -> str:
    """Process general knowledge queries with Deepseek R1 14B."""
    return await call_deepseek_ollama("You are a helpful assistant answering general knowledge questions.", prompt)

async def process_math_with_gemini(prompt: str) -> str:
    """Process math queries with Gemini 2.0 Flash."""
    api_key = API_KEYS["gemini"]
    
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
            }
        ) as response:
            result = await response.json()
    
    # Extract the response from Gemini API response
    try:
        return result["candidates"][0]["content"]["parts"][0]["text"]
    except (KeyError, IndexError):
        return f"Error processing mathematics with Gemini: {json.dumps(result)}"

async def process_coding_with_claude_37(prompt: str) -> str:
    """Process coding queries with Claude 3.7 Sonnet."""
    api_key = API_KEYS["claude"]
    
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
                "messages": [
                    {"role": "user", "content": prompt}
                ]
            }
        ) as response:
            result = await response.json()
    
    # Extract the response from Claude API response
    try:
        return result["content"][0]["text"]
    except (KeyError, IndexError):
        return f"Error processing coding with Claude 3.7: {json.dumps(result)}"

async def process_literature_with_claude_35(prompt: str) -> str:
    """Process literature/reading comprehension with Claude 3.5 Sonnet."""
    api_key = API_KEYS["claude"]
    
    async with aiohttp.ClientSession() as session:
        async with session.post(
            "https://api.anthropic.com/v1/messages",
            headers={
                "x-api-key": api_key,
                "anthropic-version": "2023-06-01",
                "content-type": "application/json"
            },
            json={
                "model": "claude-3-5-sonnet-20240229",
                "max_tokens": 4096,
                "messages": [
                    {"role": "user", "content": prompt}
                ]
            }
        ) as response:
            result = await response.json()
    
    # Extract the response from Claude API response
    try:
        return result["content"][0]["text"]
    except (KeyError, IndexError):
        return f"Error processing literature with Claude 3.5: {json.dumps(result)}"
