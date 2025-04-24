# python3 -m app.schemas.user
from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime

class UserBase(BaseModel):
    email: EmailStr

class UserCreate(UserBase):
    password: str = Field(..., min_length=8, description="Password must be at least 8 characters")
    full_name: Optional[str] = None

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[str] = None
    user_id: Optional[str] = None

class UserResponse(UserBase):
    id: str
    email: EmailStr
    full_name: Optional[str] = None
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True
        orm_mode = True
        
    def from_orm(cls, obj):
        obj_dict = obj.__dict__
        obj_dict['id'] = str(obj_dict['id'])  # Convert UUID to string
        return super().from_orm(obj_dict)

def main():
    print("Yupp running")

if __name__ == "__main__":
    main()
