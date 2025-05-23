# python3 -m app.schemas.strategy
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

class StrategyBase(BaseModel):
    business_name: str
    industry: str
    challenges: Optional[str] = None
    goals: Optional[str] = None
    target_audience: Optional[str] = None
    timeframe: Optional[str] = None
    budget: Optional[str] = None

class StrategyRequest(StrategyBase):
    pass

# class StrategyItem(BaseModel):
#     title: str
#     description: str

# class ActionPlanItem(BaseModel):
#     step: str
#     timeline: str
#     budget: str

class ResourceItem(BaseModel):
    name: str
    purpose: str

# class StrategyResponse(BaseModel):
#     title: str
#     summary: str
#     strategies: List[StrategyItem]
#     action_plan: List[ActionPlanItem]
#     resources: List[ResourceItem]

class StrategyResponse(BaseModel):
    title: str
    summary: str
    strategies: List[str]
    action_plan: List[str]
    resources: List[ResourceItem]

class SaveStrategyRequest(BaseModel):
    title: str
    content: str
    business_name: Optional[str] = None
    industry: Optional[str] = None

class SavedStrategyResponse(BaseModel):
    id: str
    title: str
    business_name: Optional[str] = None
    industry: Optional[str] = None
    content: str
    created_at: datetime
    
    class Config:
        from_attributes = True

def main():
    print("Making Strategies")

if __name__ == "__main__":
    main()