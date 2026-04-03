from pydantic import BaseModel, EmailStr, Field

class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8)
    name: str = Field(..., min_length=3)
    is_active: bool

class UserResponse(BaseModel): 
    id: int
    email: EmailStr
    name: str
    is_active: bool

    model_config = {
        "from_attributes": True
    }

class UserRead(BaseModel):
    id: int
    email: EmailStr
    name: str
    is_active: bool

    model_config = {
        "from_attributes": True
    }
class CalculatorCreate(BaseModel):
    operator: str = Field(..., max_length=10)
    operand1: int
    operand2: int
class CalculatorRead(BaseModel):
    operator: str
    operand1: int
    operand2: int
    result: int

    model_config = {
        "from_attributes": True
    }
