from fastapi import FastAPI, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os
import uuid
import json
import logging
from typing import Dict, List, Optional

from prompt_parser import parse_prompt
from llm_router import route_to_llms, generate_structured_prompt
from api_integration import combine_responses
from config import PARSED_PROMPTS_DIR, GENERATED_PROMPTS_DIR

# Set up logging
logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

app = FastAPI()

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For development; restrict this in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class PromptRequest(BaseModel):
    prompt: str

class PromptResponse(BaseModel):
    session_id: str
    status: str
    parsed_categories: Optional[Dict[str, str]] = None
    generated_prompts: Optional[Dict[str, str]] = None
    responses: Optional[Dict[str, str]] = None
    combined_response: Optional[str] = None
    error: Optional[str] = None

# Create directories if they don't exist
os.makedirs(PARSED_PROMPTS_DIR, exist_ok=True)
os.makedirs(GENERATED_PROMPTS_DIR, exist_ok=True)

# In-memory storage for session data
sessions = {}

@app.post("/api/prompt", response_model=PromptResponse)
async def process_prompt(prompt_request: PromptRequest, background_tasks: BackgroundTasks):
    # Create a new session
    session_id = str(uuid.uuid4())
    sessions[session_id] = {
        "status": "parsing",
        "prompt": prompt_request.prompt
    }
    
    # Start background processing
    background_tasks.add_task(process_prompt_async, session_id, prompt_request.prompt)
    
    return {"session_id": session_id, "status": "parsing"}

@app.get("/api/status/{session_id}", response_model=PromptResponse)
async def get_status(session_id: str):
    if session_id not in sessions:
        return {"session_id": session_id, "status": "not_found"}
    
    return {
        "session_id": session_id,
        **sessions[session_id]
    }

async def process_prompt_async(session_id: str, prompt: str):
    try:
        logger.info(f"Processing session {session_id}")
        
        # Step 1: Parse prompt into categories using Claude 3.7 Sonnet
        logger.info("Step 1: Parsing prompt into categories")
        parsed_categories = await parse_prompt(prompt)
        sessions[session_id]["status"] = "generating_prompts"
        sessions[session_id]["parsed_categories"] = parsed_categories
        
        # Log parsed categories
        try:
            with open(os.path.join(PARSED_PROMPTS_DIR, f"{session_id}.json"), "w") as f:
                json.dump(parsed_categories, f, indent=2)
                logger.info(f"Saved parsed categories to {session_id}.json")
        except Exception as e:
            logger.error(f"Error saving parsed categories: {str(e)}")
        
        # Step 2: Generate structured prompts for each category
        logger.info("Step 2: Generating structured prompts")
        generated_prompts = {}
        for category, content in parsed_categories.items():
            if content != "Not Applicable":
                try:
                    generated_prompts[category] = await generate_structured_prompt(category, content)
                    logger.info(f"Generated prompt for {category}")
                except Exception as e:
                    logger.error(f"Error generating prompt for {category}: {str(e)}")
                    generated_prompts[category] = content  # Use original content as fallback
        
        sessions[session_id]["status"] = "routing_to_llms"
        sessions[session_id]["generated_prompts"] = generated_prompts
        
        # Log generated prompts
        try:
            with open(os.path.join(GENERATED_PROMPTS_DIR, f"{session_id}.json"), "w") as f:
                json.dump(generated_prompts, f, indent=2)
                logger.info(f"Saved generated prompts to {session_id}.json")
        except Exception as e:
            logger.error(f"Error saving generated prompts: {str(e)}")
        
        # Step 3: Route prompts to appropriate LLMs
        logger.info("Step 3: Routing prompts to LLMs")
        responses = await route_to_llms(generated_prompts)
        sessions[session_id]["status"] = "combining_responses"
        sessions[session_id]["responses"] = responses
        
        # Step 4: Combine responses using Claude 3.7 Sonnet
        logger.info("Step 4: Combining responses")
        
        # Only proceed if we have at least one valid response
        if any(isinstance(resp, str) and not resp.startswith("Error") for resp in responses.values()):
            combined_response = await combine_responses(responses)
            sessions[session_id]["status"] = "completed"
            sessions[session_id]["combined_response"] = combined_response
            logger.info("Processing completed successfully")
        else:
            error_msg = "Failed to get valid responses from any LLM"
            sessions[session_id]["status"] = "error"
            sessions[session_id]["error"] = error_msg
            logger.error(error_msg)
        
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        logger.error(f"Error processing prompt: {str(e)}")
        logger.error(error_details)
        sessions[session_id]["status"] = "error"
        sessions[session_id]["error"] = f"{str(e)}\n\nDetails: {error_details}"

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)