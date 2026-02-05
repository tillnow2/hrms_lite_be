from fastapi import APIRouter, HTTPException, status
from app.config.database import get_database
from datetime import datetime, date
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

@router.get("/dashboard/stats")
async def get_dashboard_stats():
  
  
    try:
        db = get_database()
        

        total_employees = await db.employees.count_documents({})
        

        today = date.today()
        today_start = datetime.combine(today, datetime.min.time())
        today_end = datetime.combine(today, datetime.max.time())
        

        today_present = await db.attendance.count_documents({
            "date": {"$gte": today_start, "$lte": today_end},
            "status": "Present"
        })
        
        today_absent = await db.attendance.count_documents({
            "date": {"$gte": today_start, "$lte": today_end},
            "status": "Absent"
        })
        

        total_attendance_records = await db.attendance.count_documents({})
        

        total_present = await db.attendance.count_documents({"status": "Present"})
        total_absent = await db.attendance.count_documents({"status": "Absent"})
        
        overall_attendance_percentage = (
            (total_present / total_attendance_records * 100) 
            if total_attendance_records > 0 else 0.0
        )
        

        departments = []
        async for dept in db.employees.aggregate([
            {"$group": {"_id": "$department", "count": {"$sum": 1}}},
            {"$sort": {"count": -1}}
        ]):
            departments.append({
                "department": dept["_id"],
                "count": dept["count"]
            })
        

        recent_attendance = []
        async for record in db.attendance.find().sort("date", -1).limit(10):

            employee = await db.employees.find_one({"employee_id": record["employee_id"]})
            employee_name = employee["full_name"] if employee else "Unknown"
            
            recent_attendance.append({
                "employee_id": record["employee_id"],
                "employee_name": employee_name,
                "date": record["date"].isoformat(),
                "status": record["status"]
            })
        

        today_total = today_present + today_absent
        today_attendance_percentage = (
            (today_present / today_total * 100) 
            if today_total > 0 else 0.0
        )
        
        return {
            "success": True,
            "data": {
                "summary": {
                    "total_employees": total_employees,
                    "total_attendance_records": total_attendance_records,
                    "today_present": today_present,
                    "today_absent": today_absent,
                    "today_total": today_total,
                    "today_attendance_percentage": round(today_attendance_percentage, 2),
                    "overall_attendance_percentage": round(overall_attendance_percentage, 2)
                },
                "departments": departments,
                "recent_attendance": recent_attendance,
                "today_date": today.isoformat()
            }
        }
        
    except Exception as e:
        logger.error(f"Error fetching dashboard stats: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve dashboard statistics"
        )
