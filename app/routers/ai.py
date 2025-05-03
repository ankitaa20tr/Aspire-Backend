# python3 -m app.routers.ai
# source .venv/bin/activate

import json
from typing import List, Dict

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from loguru import logger

from app.database.database import get_db
from app.database.models import User, Conversation, Message
from app.auth.utils import get_active_user
from app.schemas.strategy import StrategyRequest, StrategyResponse
from app.schemas.chat import ChatRequest, ChatResponse, ChatMessage
from app.services import (
    generate_business_strategy,
    generate_chatbot_response,
    GeminiQuotaExceededError,
    GeminiAPIError,
    GeminiContentFilterError
)

router = APIRouter(
    prefix="/ai",
    tags=["AI Services"],
    responses={401: {"description": "Unauthorized"}},
)

@router.post("/generate-strategy", response_model=StrategyResponse)
async def generate_strategy(
    strategy_request: StrategyRequest,
    current_user: User = Depends(get_active_user),
    db: Session = Depends(get_db)
):
    """
    Generate a business strategy using AI.
    """
    try:
        logger.info(f"Generating strategy for {strategy_request.business_name}, user: {current_user.email}")
        strategy = generate_business_strategy(strategy_request)

       # Fix action_plan if it's a list of dicts
        if isinstance(strategy.get('action_plan'), list):
            new_action_plan = []
            for step in strategy['action_plan']:
                if isinstance(step, dict):
                    # Format dict into a readable string
                    formatted_step = f"Step {step.get('step')}: {step.get('action')} (Timeline: {step.get('timeline')}, Budget: {step.get('budget')})"
                    new_action_plan.append(formatted_step)
                else:
                    new_action_plan.append(str(step))  # If already a string, just keep
                strategy['action_plan'] = new_action_plan

        # Fix resources similarly if needed (optional, depends on your model)
        if isinstance(strategy.get('resources'), list):
            new_resources = []
            for res in strategy['resources']:
                if isinstance(res, dict):
                    name = res.get('type') or res.get('name') or "Unknown Resource"
                    purpose = res.get('purpose') or f"Purpose for {name}"  # Default/fallback
                    items = res.get('items') or []

                    new_resources.append({
                        "name": name,
                        "purpose": purpose,
                        "items": items
                    })
            strategy['resources'] = new_resources

        return strategy

    except GeminiQuotaExceededError as e:
        logger.error(f"Gemini quota exceeded or rate limited: {e}")
        raise HTTPException(
            status_code=status.HTTP_402_PAYMENT_REQUIRED,
            detail="Gemini API quota exceeded or rate limited. This may be due to free tier limitations. Please try again later."
        )

    except GeminiContentFilterError as e:
        logger.error(f"Gemini content filter blocked the request: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Your request was blocked by Gemini's content filter. Please modify your business details to avoid potentially sensitive content."
        )

    except GeminiAPIError as e:
        filter_type = getattr(e, 'filter_type', 'unknown')
        logger.error(f"Gemini content filter blocked the request: {filter_type}")

        # Customize message based on filter type
        guidance_message = "Your request was blocked by Gemini's content filter. "

        if filter_type == "sexually_explicit":
            guidance_message += "Please modify your business details to avoid terms that could be interpreted as sexually explicit."
        elif filter_type == "hate_speech":
            guidance_message += "Please ensure your business details don't contain language that could be interpreted as hate speech or discriminatory."
        elif filter_type == "harassment":
            guidance_message += "Please modify your business details to avoid language that could be interpreted as harassment."
        elif filter_type == "dangerous_content":
            guidance_message += "Please modify your business details to avoid terms related to dangerous activities or products."
        else:
            guidance_message += "Please modify your business details to avoid potentially sensitive content."

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=guidance_message
        )

    except ValueError as e:
        logger.error(f"Value error in strategy generation: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

    except Exception as e:
        logger.error(f"Error generating strategy: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate strategy. Please try again later."
        )

@router.post("/chatbot", response_model=ChatResponse)
async def chatbot(
    chat_request: ChatRequest,
    current_user: User = Depends(get_active_user),
    db: Session = Depends(get_db)
):
    """
    Chat with the AI business consultant.
    """
    try:
        conversation = None

        if chat_request.conversation_id:
            conversation = db.query(Conversation).filter(
                Conversation.id == chat_request.conversation_id,
                Conversation.user_id == current_user.id
            ).first()

            if not conversation:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Conversation not found."
                )
        else:
            # New conversation
            conversation = Conversation(
                user_id=current_user.id,
                title=chat_request.message[:30] + "..." if len(chat_request.message) > 30 else chat_request.message
            )
            db.add(conversation)
            db.commit()
            db.refresh(conversation)

        # Fetch conversation history
        history = []
        if conversation.id:
            messages = db.query(Message).filter(
                Message.conversation_id == conversation.id
            ).order_by(Message.created_at).all()

            for msg in messages:
                history.append({"role": msg.role, "content": msg.content})

        # Generate AI response
        response_text = generate_chatbot_response(chat_request.message, history)

        # Save user message
        user_message = Message(
            conversation_id=conversation.id,
            content=chat_request.message,
            role="user"
        )
        db.add(user_message)

        # Save AI response
        ai_message = Message(
            conversation_id=conversation.id,
            content=response_text,
            role="assistant"
        )
        db.add(ai_message)

        db.commit()

        logger.info(f"Chatbot response generated for user {current_user.email}, conversation {conversation.id}")

        return ChatResponse(message=response_text, conversation_id=conversation.id)

    except HTTPException:
        raise 

    except Exception as e:
        db.rollback()
        logger.error(f"Error in chatbot endpoint: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to process chatbot request. Please try again later."
        )

@router.get("/conversations", response_model=List[Dict])
async def get_conversations(
    current_user: User = Depends(get_active_user),
    db: Session = Depends(get_db)
):
    """
    Get all conversations for the current user.
    """
    try:
        conversations = db.query(Conversation).filter(
            Conversation.user_id == current_user.id
        ).order_by(Conversation.updated_at.desc()).all()

        result = []
        for conv in conversations:
            messages = db.query(Message).filter(
                Message.conversation_id == conv.id
            ).order_by(Message.created_at).all()

            last_message = messages[-1].content if messages else ""

            result.append({
                "id": conv.id,
                "title": conv.title,
                "created_at": conv.created_at,
                "updated_at": conv.updated_at,
                "last_message": last_message[:100] + "..." if len(last_message) > 100 else last_message
            })

        return result

    except Exception as e:
        logger.error(f"Error getting conversations: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve conversations."
        )

@router.get("/conversations/{conversation_id}", response_model=List[ChatMessage])
async def get_conversation_messages(
    conversation_id: str,
    current_user: User = Depends(get_active_user),
    db: Session = Depends(get_db)
):
    """
    Get all messages in a conversation.
    """
    try:
        conversation = db.query(Conversation).filter(
            Conversation.id == conversation_id,
            Conversation.user_id == current_user.id
        ).first()

        if not conversation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Conversation not found."
            )

        messages = db.query(Message).filter(
            Message.conversation_id == conversation_id
        ).order_by(Message.created_at).all()

        return [
            ChatMessage(
                role=msg.role,
                content=msg.content,
                created_at=msg.created_at
            ) for msg in messages
        ]

    except HTTPException:
        raise

    except Exception as e:
        logger.error(f"Error getting conversation messages: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve conversation messages."
        )

if __name__ == "__main__":
    print("AI Router script is running")
