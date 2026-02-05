from pydantic import BaseModel, Field, EmailStr
from typing import Optional
from datetime import datetime

class EmployeeBase(BaseModel):
    employee_id: str
    full_name: str
    email: EmailStr
    department: str

class EmployeeCreate(EmployeeBase):
    pass

class EmployeeUpdate(BaseModel):
    full_name: Optional[str] = None
    email: Optional[EmailStr] = None
    department: Optional[str] = None

class EmployeeResponse(BaseModel):
    id: str = Field(..., alias="_id")
    employee_id: str
    full_name: str
    email: str
    department: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
        populate_by_name = True

class EmployeeInDB(EmployeeBase):
    created_at: datetime
    updated_at: datetime
