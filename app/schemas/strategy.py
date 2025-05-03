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

<<<<<<< HEAD
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

=======
>>>>>>> 10ea94d63b78da66bb861a7ac7de7cf034028959
class StrategyResponse(BaseModel):
    title: str
    summary: str
    strategies: List[str]
    action_plan: List[str]
<<<<<<< HEAD
    resources: List[ResourceItem]
=======
    resources: Optional[List[str]] = None
>>>>>>> 10ea94d63b78da66bb861a7ac7de7cf034028959

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
