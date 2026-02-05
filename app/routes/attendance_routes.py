from fastapi import APIRouter, HTTPException, status, Query
from typing import List, Optional
from app.models.attendance import (
    AttendanceCreate, 
    AttendanceResponse, 
    AttendanceUpdate,
    AttendanceSummary
)
from app.schemas.response import ResponseModel
from app.config.database import get_database
from datetime import datetime, date
from bson import ObjectId
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

def attendance_helper(attendance, employee_name=None) -> dict:
    return {
        "_id": str(attendance["_id"]),
        "employee_id": attendance["employee_id"],
        "employee_name": employee_name,
        "date": attendance["date"],
        "status": attendance["status"],
        "remarks": attendance.get("remarks"),
        "created_at": attendance["created_at"],
        "updated_at": attendance["updated_at"]
    }

@router.post("/attendance", response_model=AttendanceResponse, status_code=status.HTTP_201_CREATED)
async def mark_attendance(attendance: AttendanceCreate):
    try:
        db = get_database()
        
        employee_id_upper = attendance.employee_id.strip().upper()
        employee = await db.employees.find_one({"employee_id": employee_id_upper})
        if not employee:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Employee with ID '{attendance.employee_id}' not found"
            )
        
        attendance_date = attendance.date
        if isinstance(attendance_date, date) and not isinstance(attendance_date, datetime):
            attendance_date = datetime.combine(attendance_date, datetime.min.time())
        
        existing_attendance = await db.attendance.find_one({
            "employee_id": employee_id_upper,
            "date": attendance_date
        })
        
        if existing_attendance:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Attendance for employee '{attendance.employee_id}' on {attendance.date} already exists"
            )
        
        attendance_dict = attendance.dict()
        attendance_dict["employee_id"] = employee_id_upper
        attendance_dict["status"] = attendance_dict["status"].value if hasattr(attendance_dict["status"], "value") else attendance_dict["status"]
        
        if isinstance(attendance_dict["date"], date) and not isinstance(attendance_dict["date"], datetime):
            attendance_dict["date"] = datetime.combine(attendance_dict["date"], datetime.min.time())
        
        attendance_dict["created_at"] = datetime.utcnow()
        attendance_dict["updated_at"] = datetime.utcnow()
        
        result = await db.attendance.insert_one(attendance_dict)
        
        created_attendance = await db.attendance.find_one({"_id": result.inserted_id})
        return attendance_helper(created_attendance, employee["full_name"])
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error marking attendance: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to mark attendance: {str(e)}"
        )

@router.get("/attendance", response_model=List[AttendanceResponse])
async def get_all_attendance(
    employee_id: Optional[str] = Query(None, description="Filter by employee ID"),
    start_date: Optional[date] = Query(None, description="Filter from date"),
    end_date: Optional[date] = Query(None, description="Filter to date"),
    status: Optional[str] = Query(None, description="Filter by status (Present/Absent)")
):
   
    try:
        db = get_database()
        
        query = {}
        
        if employee_id:
            query["employee_id"] = employee_id.upper()
        
        if start_date or end_date:
            date_query = {}
            if start_date:
                start_datetime = datetime.combine(start_date, datetime.min.time())
                date_query["$gte"] = start_datetime
            if end_date:
                end_datetime = datetime.combine(end_date, datetime.max.time())
                date_query["$lte"] = end_datetime
            query["date"] = date_query
        
        if status:
            query["status"] = status
        
        attendance_records = []
        
        async for attendance in db.attendance.find(query).sort("date", -1):
            employee = await db.employees.find_one({"employee_id": attendance["employee_id"]})
            employee_name = employee["full_name"] if employee else None
            
            attendance_records.append(attendance_helper(attendance, employee_name))
        
        return attendance_records
        
    except Exception as e:
        logger.error(f"Error fetching attendance records: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve attendance records"
        )

@router.get("/attendance/{attendance_id}", response_model=AttendanceResponse)
async def get_attendance_by_id(attendance_id: str):
    
    try:
        db = get_database()
        
        if not ObjectId.is_valid(attendance_id):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid attendance ID format"
            )
        
        attendance = await db.attendance.find_one({"_id": ObjectId(attendance_id)})
        
        if not attendance:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Attendance record with ID '{attendance_id}' not found"
            )
        
        employee = await db.employees.find_one({"employee_id": attendance["employee_id"]})
        employee_name = employee["full_name"] if employee else None
        
        return attendance_helper(attendance, employee_name)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching attendance {attendance_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve attendance record"
        )

@router.get("/attendance/employee/{employee_id}", response_model=List[AttendanceResponse])
async def get_employee_attendance(employee_id: str):
    
    try:
        db = get_database()
        
        # Verify employee exists
        employee = await db.employees.find_one({"employee_id": employee_id.upper()})
        if not employee:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Employee with ID '{employee_id}' not found"
            )
        
        # Fetch attendance records
        attendance_records = []
        
        async for attendance in db.attendance.find({"employee_id": employee_id.upper()}).sort("date", -1):
            attendance_records.append(attendance_helper(attendance, employee["full_name"]))
        
        return attendance_records
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching attendance for employee {employee_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve employee attendance records"
        )

@router.put("/attendance/{attendance_id}", response_model=AttendanceResponse)
async def update_attendance(attendance_id: str, attendance_update: AttendanceUpdate):
    
    try:
        db = get_database()
        
        if not ObjectId.is_valid(attendance_id):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid attendance ID format"
            )
        
        existing_attendance = await db.attendance.find_one({"_id": ObjectId(attendance_id)})
        if not existing_attendance:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Attendance record with ID '{attendance_id}' not found"
            )
        
        update_data = {k: v for k, v in attendance_update.dict(exclude_unset=True).items() if v is not None}
        
        if not update_data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No valid fields provided for update"
            )
        
        update_data["updated_at"] = datetime.utcnow()
        
        await db.attendance.update_one(
            {"_id": ObjectId(attendance_id)},
            {"$set": update_data}
        )
        
        updated_attendance = await db.attendance.find_one({"_id": ObjectId(attendance_id)})
        
        employee = await db.employees.find_one({"employee_id": updated_attendance["employee_id"]})
        employee_name = employee["full_name"] if employee else None
        
        return attendance_helper(updated_attendance, employee_name)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating attendance {attendance_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update attendance record"
        )

@router.delete("/attendance/{attendance_id}", response_model=ResponseModel)
async def delete_attendance(attendance_id: str):
   
    try:
        db = get_database()
        
        if not ObjectId.is_valid(attendance_id):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid attendance ID format"
            )
        
        attendance = await db.attendance.find_one({"_id": ObjectId(attendance_id)})
        if not attendance:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Attendance record with ID '{attendance_id}' not found"
            )
        
        await db.attendance.delete_one({"_id": ObjectId(attendance_id)})
        
        return ResponseModel(
            success=True,
            message="Attendance record deleted successfully"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting attendance {attendance_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete attendance record"
        )

@router.get("/attendance/summary/{employee_id}", response_model=AttendanceSummary)
async def get_attendance_summary(employee_id: str):
   
    try:
        db = get_database()
        
        employee = await db.employees.find_one({"employee_id": employee_id.upper()})
        if not employee:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Employee with ID '{employee_id}' not found"
            )
        
        total_days = await db.attendance.count_documents({"employee_id": employee_id.upper()})
        present_days = await db.attendance.count_documents({
            "employee_id": employee_id.upper(),
            "status": "Present"
        })
        absent_days = await db.attendance.count_documents({
            "employee_id": employee_id.upper(),
            "status": "Absent"
        })
        
        attendance_percentage = (present_days / total_days * 100) if total_days > 0 else 0.0
        
        return AttendanceSummary(
            employee_id=employee_id.upper(),
            employee_name=employee["full_name"],
            total_days=total_days,
            present_days=present_days,
            absent_days=absent_days,
            attendance_percentage=round(attendance_percentage, 2)
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching attendance summary for {employee_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve attendance summary"
        )
