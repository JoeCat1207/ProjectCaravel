Named after the Civ-5 Caravel... a swift and agile ship

Project Caravel is my entry into a 3 Week Hackathon with the theme of 'Building Connections'.

When running this project locally, the web UI recieves user input then follows this pipeline:

User Prompt -> Claude 3.7 Sonnett w/ parsing system prompt that splits the prompt into 4 categories (General knowledge, mathematics, coding and reading) 
-> Claude 3.7 creates prompts for each category -> Prompts are logged -> Prompts are sent to their respective LLMs (In this case, Claude 3.5 Haiku, Gemini 2.0 Flash, and Claude 3.7 Sonnet)
-> Responses are combined into a singular response by Claude 3.7 w/ system prompt 
-> Final combined response is displayed.

Originally, this project was supposed to live in a Docker container. However, I'm not the brightest person and can't make it work on my machine.

Instead, you will need to cd into the backend and frontend folders individually in a Powershell (w/ admin privileges) instance.

For the backend:

cd backend_path
pip install -r requirements.txt
python main.py

For the frontend:

cd frontend_path
npm install
npm start

A locally hosted webserver should start at localhost:3000

Note: This entire thing was coded by a maniac, it requires some fiddling to get working. Feel free to play around. You will also need to create an api_keys.env file with your api keys as such:

GEMINI_API_KEY= your key
ANTHROPIC_API_KEY= your key

#below are optional controls for whatever you need
#directories for logging
# PARSED_PROMPTS_DIR=./logs/parsed_prompts
# GENERATED_PROMPTS_DIR=./logs/generated_prompts

#Rate limiting settings in case i run out of credits lol
# RATE_LIMIT_REQUESTS=5
# RATE_LIMIT_WINDOW=60
