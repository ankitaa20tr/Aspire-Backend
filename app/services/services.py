# python3 -m app.services.services
# source venvAnkitaTiwari/bin/activate
import os
import sys
from openai import OpenAI
from dotenv import load_dotenv, find_dotenv
from loguru import logger
from pathlib import Path
from typing import List, Dict, Any, Optional
from app.schemas.strategy import StrategyRequest

# Determine project root and locate .env
BASE_DIR = Path(__file__).resolve().parents[2]  
ENV_PATH = BASE_DIR / ".env"
load_dotenv(dotenv_path=ENV_PATH, override=True)
print("Looking for .env at:", ENV_PATH)
logger.info(f"Loading environment variables from {ENV_PATH}")

# Fetch OpenAI configuration
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o")

if OPENAI_API_KEY:
    print(f"OpenAI API Key: {OPENAI_API_KEY}")
else:
    print("❌ OpenAI API key not found.")

# Initialize OpenAI client
client = OpenAI(api_key=OPENAI_API_KEY)

# # Load environment variables with improved debugging
# dotenv_path = find_dotenv()
# if not dotenv_path:
#     logger.error("No .env file found. Please create one based on .env.example")
    
# if load_dotenv(dotenv_path):
#     logger.info(f"Loaded environment variables from {dotenv_path}")
# else:
#     logger.warning("Could not load .env file. Using environment variables directly")

# # Get API key from environment variable
# OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
# OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o")

# if __name__ == "__main__":
#     # This will run when the module is executed directly
#     print(f"Key: {OPENAI_API_KEY}")
#     if OPENAI_API_KEY and OPENAI_API_KEY != "your-openai-api-key":
#         print("✅ OpenAI service is ready!")
#     else:
#         print("❌ OpenAI API key not found or is using the default example value.")
#         print("Please set the OPENAI_API_KEY environment variable in your .env file.")
#         print(f".env file location searched: {dotenv_path or 'Not found'}")


def generate_business_strategy(strategy_request: StrategyRequest) -> Dict[str, Any]:
    """Generate a business strategy using OpenAI's API."""
    
    if not OPENAI_API_KEY:
        logger.error("OpenAI API key not found in environment variables")
        raise ValueError("OpenAI API key not configured")
    
    if OPENAI_API_KEY == "your-openai-api-key":
        logger.error("OpenAI API key is using the default example value")
        raise ValueError("Please set a valid OpenAI API key in your .env file")
    
    try:
        # ... keep existing code (prompt creation and API call)
        prompt = f"""
        You are an expert business strategist. Generate a comprehensive business strategy for the following business:
        
        Business Name: {strategy_request.business_name}
        Industry: {strategy_request.industry}
        Challenges: {strategy_request.challenges or 'Not specified'}
        Goals: {strategy_request.goals or 'Not specified'}
        Target Audience: {strategy_request.target_audience or 'Not specified'}
        Timeframe: {strategy_request.timeframe or 'Not specified'}
        Budget Considerations: {strategy_request.budget or 'Not specified'}
        
        Please provide:
        1. A catchy title for this strategy
        2. An executive summary
        3. 3-5 key strategic recommendations
        4. A specific action plan with steps
        5. Resource recommendations
        
        Format your response in JSON with these keys:
        - title
        - summary
        - strategies (array)
        - action_plan (array)
        - resources (array)
        """

        response = client.chat.completions.create(
            model=OPENAI_MODEL,
            messages=[
                {"role": "system", "content": "You are an expert business strategist providing actionable advice for small and medium businesses."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            response_format={"type": "json_object"},
        )
        
        # Extract the generated content
        strategy_content = response.choices[0].message.content
        
        # Log successful API call
        logger.info(f"Successfully generated strategy for {strategy_request.business_name}")
        
        import json
        # Parse JSON response
        try:
            return json.loads(strategy_content)
        except json.JSONDecodeError:
            logger.error(f"Failed to parse AI response as JSON: {strategy_content[:100]}...")
            # Fallback response
            return {
                "title": f"Strategic Plan for {strategy_request.business_name}",
                "summary": "The AI generated a response but it couldn't be parsed as JSON. Please try again.",
                "strategies": ["Please try again with more specific details about your business."],
                "action_plan": ["Contact support if this issue persists."],
                "resources": []
            }
        
    except Exception as e:
        logger.error(f"Error generating strategy: {e}")
        raise

def generate_chatbot_response(message: str, conversation_history: List[Dict[str, str]] = None) -> str:
    """Generate a chatbot response using OpenAI's API."""
    
    if not OPENAI_API_KEY:
        logger.error("OpenAI API key not found in environment variables")
        raise ValueError("OpenAI API key not configured")
    
    if OPENAI_API_KEY == "your-openai-api-key":
        logger.error("OpenAI API key is using the default example value")
        raise ValueError("Please set a valid OpenAI API key in your .env file")
    
    if conversation_history is None:
        conversation_history = []


        
    try:
        messages = [
            {"role": "system", 
            "content": """You are an expert business consultant for Aspire, 
            providing practical advice and strategies for small and medium-sized businesses. 
            Keep your responses concise, actionable, and evidence-based. When appropriate, use 
            examples and case studies to illustrate your points. Your goal is to help businesses 
            grow and overcome challenges with practical, implementable advice."""}
        ]
        
        # Add conversation history
        messages.extend(conversation_history)
        
        # Add current user message
        messages.append({"role": "user", "content": message})

        response = client.chat.completions.create(
            model=OPENAI_MODEL,
            messages=messages,
            temperature=0.7,
        )
        
        # Extract the response content
        response_content = response.choices[0].message.content
        
        return response_content
        
    except Exception as e:
        logger.error(f"Error generating chatbot response: {e}")
        return "I'm sorry, I encountered an error while processing your request. Please try again later."

if __name__ == "__main__":
    print("✅ OpenAI service is ready!")

# with open(ENV_PATH, "r") as f:
#     print("=== .env content ===")
#     print(f.read())

