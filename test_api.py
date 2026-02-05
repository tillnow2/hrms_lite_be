#!/usr/bin/env python3

import asyncio
import sys
from datetime import date

async def test_api():
    try:
        from httpx import AsyncClient
        
        BASE_URL = "http://localhost:8000"
        
        print("Testing HRMS Lite API\n")
        print(f"Base URL: {BASE_URL}\n")
        
        async with AsyncClient() as client:
            print("Testing health endpoint...")
            response = await client.get(f"{BASE_URL}/health")
            assert response.status_code == 200
            print(f"Health check passed: {response.json()}\n")
            
            print("Testing GET /api/employees (empty)...")
            response = await client.get(f"{BASE_URL}/api/employees")
            assert response.status_code == 200
            print(f"Get employees passed: {len(response.json())} employees\n")
            
            print("Testing POST /api/employees...")
            employee_data = {
                "employee_id": "EMP001",
                "full_name": "John Doe",
                "email": "john.doe@example.com",
                "department": "Engineering"
            }
            response = await client.post(f"{BASE_URL}/api/employees", json=employee_data)
            assert response.status_code == 201
            created_employee = response.json()
            print(f"Employee created: {created_employee['employee_id']} - {created_employee['full_name']}\n")
            
            print("Testing GET /api/employees/EMP001...")
            response = await client.get(f"{BASE_URL}/api/employees/EMP001")
            assert response.status_code == 200
            employee = response.json()
            print(f"Employee retrieved: {employee['full_name']}\n")
            
            print("Testing duplicate employee creation...")
            response = await client.post(f"{BASE_URL}/api/employees", json=employee_data)
            assert response.status_code == 409
            print(f"Duplicate validation passed: {response.json()['message']}\n")
            
            print("Testing POST /api/attendance...")
            attendance_data = {
                "employee_id": "EMP001",
                "date": str(date.today()),
                "status": "Present",
                "remarks": "On time"
            }
            response = await client.post(f"{BASE_URL}/api/attendance", json=attendance_data)
            assert response.status_code == 201
            attendance = response.json()
            print(f"Attendance marked: {attendance['status']} on {attendance['date']}\n")
            
            print("Testing GET /api/attendance...")
            response = await client.get(f"{BASE_URL}/api/attendance")
            assert response.status_code == 200
            print(f"Attendance records retrieved: {len(response.json())} records\n")
            
            print("Testing GET /api/attendance/summary/EMP001...")
            response = await client.get(f"{BASE_URL}/api/attendance/summary/EMP001")
            assert response.status_code == 200
            summary = response.json()
            print(f"Attendance summary: {summary['present_days']}/{summary['total_days']} present\n")
            
            print("Testing invalid email validation...")
            invalid_employee = {
                "employee_id": "EMP002",
                "full_name": "Jane Doe",
                "email": "invalid-email",
                "department": "HR"
            }
            response = await client.post(f"{BASE_URL}/api/employees", json=invalid_employee)
            assert response.status_code == 422
            print(f"Email validation passed: Request rejected\n")
            
            print("Testing DELETE /api/employees/EMP001...")
            response = await client.delete(f"{BASE_URL}/api/employees/EMP001")
            assert response.status_code == 200
            print(f"Employee deleted successfully\n")
            
            print("=" * 50)
            print("All tests passed successfully!")
            print("=" * 50)
            
    except ImportError:
        print("Error: httpx not installed")
        print("Install it with: pip install httpx")
        sys.exit(1)
    except AssertionError as e:
        print(f"Test failed: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    print("\n" + "=" * 50)
    print("HRMS Lite API Test Suite")
    print("=" * 50 + "\n")
    
    print("Make sure the API is running on http://localhost:8000")
    print("Run: uvicorn main:app --reload\n")
    
    asyncio.run(test_api())
