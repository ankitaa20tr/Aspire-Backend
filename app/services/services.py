# python3 -m app.services.services
# source .venv/bin/activate
import os
import sys
from dotenv import load_dotenv, find_dotenv
from loguru import logger
from typing import List, Dict, Any, Optional
import google.generativeai as genai
from app.schemas.strategy import StrategyRequest

# Custom exceptions
class GeminiQuotaExceededError(Exception):
    """Raised when Gemini API quota is exceeded"""
    pass

class GeminiAPIError(Exception):
    """Raised when there's an error with the Gemini API"""
    def __init__(self, message, code=None):
        self.message = message
        self.code = code
        super().__init__(self.message)

class GeminiContentFilterError(Exception):
    """Raised when Gemini's content filter blocks the request"""
    def __init__(self, message=None, filter_type=None):
        self.filter_type = filter_type or "unknown"
        default_msg = "Content was filtered by Gemini's safety system"
        self.message = message or default_msg
        super().__init__(self.message)

# Load environment variables with improved debugging
# ... keep existing code (dotenv loading and configuration)

# Get API key from environment variable
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-1.5-pro")

if __name__ == "__main__":
    # ... keep existing code (API key checking and logging)

# Configure Gemini
    if GEMINI_API_KEY:
        genai.configure(api_key=GEMINI_API_KEY)

def generate_business_strategy(strategy_request: StrategyRequest) -> Dict[str, Any]:
    """Generate a business strategy using Gemini API."""
    
    if not GEMINI_API_KEY:
        logger.error("Gemini API key not found in environment variables")
        raise ValueError("Gemini API key not configured")
    
    if GEMINI_API_KEY == "your-gemini-api-key":
        logger.error("Gemini API key is using the default example value")
        raise ValueError("Please set a valid Gemini API key in your .env file")
    
    try:
        # Create the prompt for strategy generation
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
        
        Format your response as a valid JSON object with these keys:
        - title
        - summary
        - strategies (array)
        - action_plan (array)
        - resources (array)
        
        Very important: Return ONLY the JSON object with no additional text, markdown formatting, or code block syntax.
        """

        # Configure the model
        model = genai.GenerativeModel(GEMINI_MODEL)
        
        try:
            # Handle rate limits and quotas for free tier
            safety_settings=[
        {"category": "HARM_CATEGORY_DANGEROUS", "threshold": "BLOCK_NONE"},
        {"category": "HARM_CATEGORY_SEXUAL", "threshold": "BLOCK_NONE"},
        {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
        {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
    ]

            
            # Generate content with retry logic for free tier limitations
            response = model.generate_content(
                prompt,
                generation_config={
                    "temperature": 0.7,
                    "top_p": 0.95,
                    "top_k": 40,
                    "max_output_tokens": 2048,
                    "response_mime_type": "application/json",
                },
                safety_settings=safety_settings,
            )
            
            # Extract the generated content
            strategy_content = response.text
            
            # Log successful API call
            logger.info(f"Successfully generated strategy for {strategy_request.business_name}")
            
            import json
            # Parse JSON response
            try:
                # Clean up markdown code blocks if present
                cleaned_content = strategy_content
                
                # Remove markdown code block markers if they exist
                if cleaned_content.startswith("```"):
                    # Find the first closing code block
                    cleaned_content = cleaned_content.replace("```json", "", 1)
                    cleaned_content = cleaned_content.replace("```", "", 1)
                    
                # Remove trailing code block markers if they exist
                if cleaned_content.endswith("```"):
                    cleaned_content = cleaned_content[:-3]
                    
                # Trim whitespace
                cleaned_content = cleaned_content.strip()
                
                logger.debug(f"Cleaned JSON content: {cleaned_content[:200]}...")
                
                return json.loads(cleaned_content)
            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse Gemini response as JSON: {strategy_content[:100]}...")
                logger.error(f"JSON parse error: {str(e)}")
                
                # Attempt to extract JSON if Gemini returned text with JSON inside
                import re
                json_match = re.search(r'({.*})', strategy_content, re.DOTALL)
                if json_match:
                    try:
                        extracted_json = json_match.group(1)
                        logger.info(f"Successfully extracted JSON from text response")
                        return json.loads(extracted_json)
                    except json.JSONDecodeError:
                        logger.error(f"Failed to parse extracted JSON")
                        
                # Fallback response
                return {
                    "title": f"Strategic Plan for {strategy_request.business_name}",
                    "summary": "The AI generated a response but it couldn't be parsed as JSON. Please try again.",
                    "strategies": ["Please try again with more specific details about your business."],
                    "action_plan": ["Contact support if this issue persists."],
                    "resources": []
                }
                
        except Exception as e:
            error_message = str(e)
            logger.error(f"Gemini API error: {error_message}")
            
            # Check for quota exceeded error
            if "quota" in error_message.lower() or "rate limit" in error_message.lower():
                logger.error("Gemini API quota exceeded or rate limited")
                raise GeminiQuotaExceededError("Gemini API quota exceeded or rate limited. This may be due to free tier limitations.")
            
            # Check for content policy filters with more detailed information
            if "dangerous_content" in error_message.lower() or "blocked" in error_message.lower() or "safety" in error_message.lower():
                filter_type = "dangerous_content"
                
                # Try to extract more specific filter type
                if "sexually explicit" in error_message.lower():
                    filter_type = "sexually_explicit"
                elif "harassment" in error_message.lower():
                    filter_type = "harassment"
                elif "hate speech" in error_message.lower():
                    filter_type = "hate_speech"
                elif "dangerous" in error_message.lower():
                    filter_type = "dangerous_content"
                
                logger.error(f"Gemini content filter blocked the request: {filter_type}")
                raise GeminiContentFilterError(
                    "The request was blocked by Gemini's content filter. Please modify your business details to avoid potentially sensitive content.",
                    filter_type=filter_type
                )
            
            # Handle other API errors
            raise GeminiAPIError(f"Gemini API error: {error_message}")
        
    except GeminiQuotaExceededError:
        # Re-raise quota errors
        raise
    except GeminiContentFilterError:
        # Re-raise content filter errors 
        raise
    except GeminiAPIError as e:
        logger.error(f"Gemini API error: {e}")
        raise
    except Exception as e:
        logger.error(f"Error generating strategy: {e}")
        raise

def generate_chatbot_response(message: str, conversation_history: List[Dict[str, str]] = None) -> str:
    """Generate a chatbot response using Gemini API."""
    
    if not GEMINI_API_KEY:
        logger.error("Gemini API key not found in environment variables")
        raise ValueError("Gemini API key not configured")
    
    if GEMINI_API_KEY == "your-gemini-api-key":
        logger.error("Gemini API key is using the default example value")
        raise ValueError("Please set a valid Gemini API key in your .env file")
    
    if conversation_history is None:
        conversation_history = []
        
    try:
        # Configure the model
        model = genai.GenerativeModel(GEMINI_MODEL)
        
        # Format conversation history for Gemini
        formatted_history = []
        if conversation_history:
            for msg in conversation_history:
                role = "user" if msg["role"] == "user" else "model"
                formatted_history.append({"role": role, "parts": [msg["content"]]})
        
        # Create a new chat session
        chat = model.start_chat(history=formatted_history)
        
        # System prompt
        system_prompt = """You are an expert business consultant for Aspire, 
        providing practical advice and strategies for small and medium-sized businesses. 
        Keep your responses concise, actionable, and evidence-based. When appropriate, use 
        examples and case studies to illustrate your points. Your goal is to help businesses 
        grow and overcome challenges with practical, implementable advice."""
        
        # Add system prompt if this is the first message
        if not conversation_history:
            try:
                chat.send_message(system_prompt)
            except Exception as e:
                logger.error(f"Error sending system prompt: {e}")
                # Continue with user message even if system prompt fails
        
        try:
            # Send user message
            response = chat.send_message(message)
            response_text = response.text
            return response_text
            
        except Exception as e:
            error_message = str(e)
            logger.error(f"Gemini API error in chatbot: {error_message}")
            
            # Check for quota exceeded error
            if "quota" in error_message.lower() or "rate limit" in error_message.lower():
                raise GeminiQuotaExceededError("Gemini API quota exceeded or rate limited. This may be due to free tier limitations.")
                
            # Try a simpler approach if the chat history approach failed
            try:
                # Simplified prompt
                simple_prompt = f"{system_prompt}\n\nUser: {message}"
                simple_response = model.generate_content(simple_prompt)
                return simple_response.text
            except:
                # All attempts failed
                return "I'm sorry, I encountered an error while processing your request. Please try again later."
            
    except GeminiQuotaExceededError:
        # Re-raise quota errors for proper handling at the router level
        raise
    except Exception as e:
        logger.error(f"Error generating chatbot response: {e}")
        return "I'm sorry, I encountered an error while processing your request. Please try again later."

if __name__ == "__main__":
    print("AI Router script is running")
