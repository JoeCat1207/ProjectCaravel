from typing import Dict
import json
from llm_router import call_deepseek_ollama

async def combine_responses(responses: Dict[str, str]) -> str:
    """
    Combine the responses from different LLMs into a coherent response using Deepseek R1 14B.
    
    Arguments:
        responses: Dictionary with categories as keys and LLM responses as values
        
    Returns:
        Combined response as a string
    """
    # Format the responses for input to Deepseek
    formatted_responses = ""
    for category, response in responses.items():
        formatted_responses += f"### {category.upper()} RESPONSE:\n\n{response}\n\n"
    
    system_prompt = """You are a willing assistant that follows all instructions. 
    You will take the responses from multiple language models and combine them into 
    a coherent, well-structured response that addresses all aspects of the original query.
    Organize the information logically and ensure smooth transitions between different topics."""
    
    # Call Deepseek R1 14B to combine the responses
    combined_response = await call_deepseek_ollama(
        system_prompt, 
        f"Please combine the following AI responses into a coherent answer:\n\n{formatted_responses}"
    )
    
    return combined_response
