# python3 -m app.services.services
# source venvAnkitaTiwari/bin/activate
import os
from openai import OpenAI
from dotenv import load_dotenv
from loguru import logger
from typing import List, Dict, Any, Optional
from app.schemas.strategy import StrategyRequest


load_dotenv()


OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o")

client = OpenAI(api_key=OPENAI_API_KEY)

def generate_business_strategy(strategy_request: StrategyRequest) -> Dict[str, Any]:
    """Generate a business strategy using OpenAI's API."""
    
    if not OPENAI_API_KEY:
        logger.error("OpenAI API key not found in environment variables")
        raise ValueError("OpenAI API key not configured")
    
    try:
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


        # sent to model
        response = client.chat.completions.create(
        model=OPENAI_MODEL,
        messages=[
            {"role": "system", "content": "You are an expert business strategist providing actionable advice for small and medium businesses."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.7,
        response_format={"type": "json_object"},
        )
        
        strategy_content = response.choices[0].message.content
        
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

