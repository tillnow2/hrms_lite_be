from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime, date
from enum import Enum

class AttendanceStatus(str, Enum):
    PRESENT = "Present"
    ABSENT = "Absent"

class AttendanceBase(BaseModel):
    employee_id: str
    date: date
    status: AttendanceStatus
    remarks: Optional[str] = None

class AttendanceCreate(AttendanceBase):
    pass

class AttendanceUpdate(BaseModel):
    status: Optional[AttendanceStatus] = None
    remarks: Optional[str] = None

class AttendanceResponse(BaseModel):
    id: str = Field(..., alias="_id")
    employee_id: str
    employee_name: Optional[str] = None
    date: date
    status: str
    remarks: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
        populate_by_name = True

class AttendanceInDB(AttendanceBase):
    created_at: datetime
    updated_at: datetime

class AttendanceSummary(BaseModel):
    employee_id: str
    employee_name: str
    total_days: int
    present_days: int
    absent_days: int
    attendance_percentage: float
