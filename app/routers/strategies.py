# python3 -m app.routers.strategies
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.database.database import get_db
from app.database.models import User, SavedStrategy
from app.auth.utils import get_active_user
from app.schemas.strategy import SaveStrategyRequest, SavedStrategyResponse
from loguru import logger

router = APIRouter(
    prefix="/strategies",
    tags=["Saved Strategies"],
    responses={401: {"description": "Unauthorized"}},
)

@router.post("/", response_model=SavedStrategyResponse, status_code=status.HTTP_201_CREATED)
async def save_strategy(
    strategy: SaveStrategyRequest,
    current_user: User = Depends(get_active_user),
    db: Session = Depends(get_db)
):
    """
    Save a generated strategy for future reference.
    """
    try:
        db_strategy = SavedStrategy(
            title=strategy.title,
            business_name=strategy.business_name,
            industry=strategy.industry,
            content=strategy.content,
            user_id=current_user.id
        )
        db.add(db_strategy)
        db.commit()
        db.refresh(db_strategy)
        
        logger.info(f"Strategy saved for user {current_user.email}, id: {db_strategy.id}")
        return db_strategy
    except Exception as e:
        db.rollback()
        logger.error(f"Error saving strategy: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to save strategy. Please try again later."
        )

@router.get("/", response_model=List[SavedStrategyResponse])
async def get_user_strategies(
    current_user: User = Depends(get_active_user),
    db: Session = Depends(get_db)
):
    """
    Get all strategies saved by the current user.
    """
    strategies = db.query(SavedStrategy).filter(
        SavedStrategy.user_id == current_user.id
    ).all()
    
    return strategies

@router.get("/{strategy_id}", response_model=SavedStrategyResponse)
async def get_strategy(
    strategy_id: str,
    current_user: User = Depends(get_active_user),
    db: Session = Depends(get_db)
):
    """
    Get a specific saved strategy.
    """
    strategy = db.query(SavedStrategy).filter(
        SavedStrategy.id == strategy_id,
        SavedStrategy.user_id == current_user.id
    ).first()
    
    if strategy is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Strategy not found"
        )
    
    return strategy

@router.delete("/{strategy_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_strategy(
    strategy_id: str,
    current_user: User = Depends(get_active_user),
    db: Session = Depends(get_db)
):
    """
    Delete a saved strategy.
    """
    strategy = db.query(SavedStrategy).filter(
        SavedStrategy.id == strategy_id,
        SavedStrategy.user_id == current_user.id
    ).first()
    
    if strategy is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Strategy not found"
        )
    
    db.delete(strategy)
    db.commit()
    
    logger.info(f"Strategy {strategy_id} deleted by user {current_user.email}")
    return None

# For example, in your app/routers/auth.py
if __name__ == "__main__":
    print("Strategies module is running")
