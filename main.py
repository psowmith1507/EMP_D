
from fastapi import FastAPI, HTTPException

app = FastAPI()

employees = [
    {
        "id": 1,
        "name": "Rahul",
        "department": "IT",
        "salary": 50000
    },
    {
        "id": 2,
        "name": "Anu",
        "department": "HR",
        "salary": 45000
    }
]


# GET - Get all employees
@app.get("/employees")
def get_employees():
    return employees


# GET - Get one employee
@app.get("/employees/{employee_id}")
def get_employee(employee_id: int):
    for employee in employees:
        if employee["id"] == employee_id:
            return employee

    raise HTTPException(status_code=404, detail="Employee not found")


# POST - Create employee
@app.post("/employees")
def create_employee(employee: dict):
    employees.append(employee)

    return {
        "message": "Employee created successfully",
        "employee": employee
    }


# PUT - Replace all employee details
@app.put("/employees/{employee_id}")
def update_employee(employee_id: int, updated_employee: dict):
    for index, employee in enumerate(employees):
        if employee["id"] == employee_id:

            updated_employee["id"] = employee_id
            employees[index] = updated_employee

            return {
                "message": "Employee replaced successfully",
                "employee": updated_employee
            }

    raise HTTPException(status_code=404, detail="Employee not found")


# PATCH - Update selected employee details
@app.patch("/employees/{employee_id}")
def patch_employee(employee_id: int, employee_data: dict):
    for employee in employees:
        if employee["id"] == employee_id:

            employee.update(employee_data)

            return {
                "message": "Employee partially updated successfully",
                "employee": employee
            }

    raise HTTPException(status_code=404, detail="Employee not found")


# DELETE - Delete employee
@app.delete("/employees/{employee_id}")
def delete_employee(employee_id: int):
    for employee in employees:
        if employee["id"] == employee_id:
            employees.remove(employee)

            return {
                "message": "Employee deleted successfully"
            }

    raise HTTPException(status_code=404, detail="Employee not found")
