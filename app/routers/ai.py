# python3 -m app.routers.ai
# source venvAnkitaTiwari/bin/activate
from fastapi import APIRouter, Depends, HTTPException, status, Body
from sqlalchemy.orm import Session
from typing import List, Dict
from app.database.database import get_db
from app.database.models import User, Conversation, Message
from app.auth.utils import get_active_user
from app.schemas.strategy import StrategyRequest, StrategyResponse
from app.schemas.chat import ChatRequest, ChatResponse, ChatMessage
from loguru import logger

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
        return strategy

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
        
        # create a conversation
        if chat_request.conversation_id:
            conversation = db.query(Conversation).filter(
                Conversation.id == chat_request.conversation_id,
                Conversation.user_id == current_user.id
            ).first()
            

            if not conversation:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Conversation not found"
                )

        else:
            # new conversation
            conversation = Conversation(
                user_id=current_user.id,
                title=chat_request.message[:30] + "..." if len(chat_request.message) > 30 else chat_request.message
            )
            db.add(conversation)
            db.commit()
            db.refresh(conversation)
        
  
        history = []
        if conversation.id:
            messages = db.query(Message).filter(
                Message.conversation_id == conversation.id
            ).order_by(Message.created_at).all()
            
            for msg in messages:
                history.append({"role": msg.role, "content": msg.content})
        
        # Generate AI response
        response_text = generate_chatbot_response(chat_request.message, history)
        
        # Save message
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
        
        # Update conversation timestamp
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
            # Get first and last message
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
        # First check if conversation belongs to user
        conversation = db.query(Conversation).filter(
            Conversation.id == conversation_id,
            Conversation.user_id == current_user.id
        ).first()
        
        if not conversation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Conversation not found"
            )
            

        # Get messages
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
    # Put your main execution code here
    print("AI Router script is running")
