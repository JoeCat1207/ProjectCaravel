from typing import Dict
import json
import logging
from llm_router import call_claude_37

# Set up logging
logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

async def combine_responses(responses: Dict[str, str]) -> str:
    """
    Combine the responses from different LLMs into a coherent response using Claude 3.7 Sonnet.
    
    Arguments:
        responses: Dictionary with categories as keys and LLM responses as values
        
    Returns:
        Combined response as a string
    """
    # Check if we have any valid responses
    valid_responses = {k: v for k, v in responses.items() 
                       if isinstance(v, str) and not v.startswith("Error")}
    
    if not valid_responses:
        error_msg = "No valid responses to combine"
        logger.error(error_msg)
        return error_msg
    
    # Format the responses for input to Claude
    formatted_responses = ""
    for category, response in valid_responses.items():
        formatted_responses += f"### {category.upper()} RESPONSE:\n\n{response}\n\n"
    
    logger.info("Combining responses with Claude 3.7")
    
    system_prompt = """You are an expert at synthesizing information from multiple sources.
    
    You will receive responses from different AI models addressing various aspects of a user's query.
    Your task is to combine these responses into a single, coherent, well-structured answer.
    
    Guidelines:
    1. Maintain the accuracy and technical correctness of each specialized response
    2. Create smooth transitions between different topics
    3. Eliminate redundancies while preserving all unique information
    4. Organize the information in a logical flow
    5. Present a unified voice throughout the response
    
    Your combined response should feel like it was written by a single expert who has deep knowledge
    across all the relevant domains."""
    
    try:
        # Call Claude 3.7 Sonnet to combine the responses
        combined_response = await call_claude_37(
            system_prompt, 
            f"Please combine the following AI responses into a coherent answer:\n\n{formatted_responses}"
        )
        
        return combined_response
    except Exception as e:
        logger.error(f"Error combining responses: {str(e)}")
        return f"Error combining responses: {str(e)}\n\nHere are the individual responses:\n\n{formatted_responses}"