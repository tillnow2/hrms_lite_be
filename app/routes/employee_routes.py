from fastapi import APIRouter, HTTPException, status
from typing import List
from app.models.employee import EmployeeCreate, EmployeeResponse, EmployeeUpdate
from app.schemas.response import ResponseModel, ErrorResponse
from app.config.database import get_database
from datetime import datetime
from bson import ObjectId
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

def employee_helper(employee) -> dict:
    return {
        "_id": str(employee["_id"]),
        "employee_id": employee["employee_id"],
        "full_name": employee["full_name"],
        "email": employee["email"],
        "department": employee["department"],
        "created_at": employee["created_at"],
        "updated_at": employee["updated_at"]
    }

@router.get("/employees", response_model=List[EmployeeResponse])
async def get_all_employees():
    
    try:
        db = get_database()
        employees = []
        
        async for employee in db.employees.find().sort("created_at", -1):
            employees.append(employee_helper(employee))
        
        return employees
    except Exception as e:
        logger.error(f"Error fetching employees: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve employees"
        )

@router.get("/employees/{employee_id}", response_model=EmployeeResponse)
async def get_employee_by_id(employee_id: str):
    
    try:
        db = get_database()
        employee = await db.employees.find_one({"employee_id": employee_id.upper()})
        
        if not employee:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Employee with ID '{employee_id}' not found"
            )
        
        return employee_helper(employee)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching employee {employee_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve employee"
        )

@router.post("/employees", response_model=EmployeeResponse, status_code=status.HTTP_201_CREATED)
async def create_employee(employee: EmployeeCreate):
    
    try:
        db = get_database()
        
        employee_id_upper = employee.employee_id.strip().upper()
        existing_employee = await db.employees.find_one({"employee_id": employee_id_upper})
        if existing_employee:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Employee with ID '{employee.employee_id}' already exists"
            )
        
        existing_email = await db.employees.find_one({"email": employee.email})
        if existing_email:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Employee with email '{employee.email}' already exists"
            )
        
        employee_dict = employee.dict()
        employee_dict["employee_id"] = employee_id_upper
        employee_dict["created_at"] = datetime.utcnow()
        employee_dict["updated_at"] = datetime.utcnow()
        
        result = await db.employees.insert_one(employee_dict)
        
        created_employee = await db.employees.find_one({"_id": result.inserted_id})
        return employee_helper(created_employee)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating employee: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create employee: {str(e)}"
        )

@router.delete("/employees/{employee_id}", response_model=ResponseModel)
async def delete_employee(employee_id: str):
    
    try:
        db = get_database()
        
        employee = await db.employees.find_one({"employee_id": employee_id.upper()})
        if not employee:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Employee with ID '{employee_id}' not found"
            )
        
        await db.employees.delete_one({"employee_id": employee_id.upper()})
        
        await db.attendance.delete_many({"employee_id": employee_id.upper()})
        
        return ResponseModel(
            success=True,
            message=f"Employee '{employee_id}' and associated records deleted successfully"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting employee {employee_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete employee"
        )
