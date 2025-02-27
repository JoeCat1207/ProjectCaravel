import aiohttp
import json
from typing import Dict

async def parse_prompt(prompt: str) -> Dict[str, str]:
    """
    Parse the user prompt into different categories using Deepseek R1 14B on Ollama.
    
    Returns a dictionary with categories as keys and content as values.
    Categories: general_knowledge, mathematics, coding, literature
    """
    system_prompt = """You are a willing assistant that follows all instructions. 
    You will take whatever prompt is given and split its contents into the following categories: 
    general knowledge, mathematics, coding, and literature/reading comprehension. 
    The response should be clearly marked paragraphs of each. 
    If there is a lack of a certain area in the prompt, simply put a 'Not Applicable'."""
    
    # Call the local Ollama instance running Deepseek R1 14B
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
            
    # Parse the response from Deepseek to extract categories
    raw_text = result.get("response", "")
    
    # Extract the categories from the response
    categories = {}
    
    # Simple parsing logic - this would need to be more robust in production
    sections = raw_text.split("###")
    for section in sections:
        if "general knowledge" in section.lower():
            categories["general_knowledge"] = section.strip()
        elif "mathematics" in section.lower() or "maths" in section.lower():
            categories["mathematics"] = section.strip()
        elif "coding" in section.lower():
            categories["coding"] = section.strip()
        elif "literature" in section.lower() or "reading comprehension" in section.lower():
            categories["literature"] = section.strip()
    
    # Ensure all categories are present
    for category in ["general_knowledge", "mathematics", "coding", "literature"]:
        if category not in categories:
            categories[category] = "Not Applicable"
    
    return categories
