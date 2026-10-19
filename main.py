
from fastapi import FastAPI, HTTPException
from sqlalchemy import create_engine, text
from sqlalchemy.exc import IntegrityError
from dotenv import load_dotenv
import os

load_dotenv()

DATABASE_URL = os.getenv("TIDB_DATABASE_URL")

if not DATABASE_URL:
    raise RuntimeError("TIDB_DATABASE_URL is missing from .env")

engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True
)

app = FastAPI()


# GET - Get all employees
@app.get("/employees")
def get_employees():
    with engine.connect() as conn:
        result = conn.execute(
            text("""
                SELECT id, name, department, salary
                FROM employees
            """)
        )
        return [dict(row) for row in result.mappings().all()]


# GET - Get one employee
@app.get("/employees/{employee_id}")
def get_employee(employee_id: int):
    with engine.connect() as conn:
        result = conn.execute(
            text("""
                SELECT id, name, department, salary
                FROM employees
                WHERE id = :employee_id
            """),
            {"employee_id": employee_id}
        )
        employee = result.mappings().first()

    if employee is None:
        raise HTTPException(
            status_code=404,
            detail="Employee not found"
        )

    return dict(employee)


# POST - Create employee
@app.post("/employees", status_code=201)
def create_employee(employee: dict):
    required = {"id", "name", "department", "salary"}

    if not required.issubset(employee):
        raise HTTPException(
            status_code=400,
            detail="id, name, department and salary are required"
        )

    try:
        with engine.begin() as conn:
            conn.execute(
                text("""
                    INSERT INTO employees
                    (id, name, department, salary)
                    VALUES
                    (:id, :name, :department, :salary)
                """),
                {
                    "id": employee["id"],
                    "name": employee["name"],
                    "department": employee["department"],
                    "salary": employee["salary"]
                }
            )
    except IntegrityError:
        raise HTTPException(
            status_code=409,
            detail="Employee ID already exists"
        )

    return {
        "message": "Employee created successfully",
        "employee": employee
    }


# PUT - Replace all employee details
@app.put("/employees/{employee_id}")
def update_employee(employee_id: int, updated_employee: dict):
    required = {"name", "department", "salary"}

    if not required.issubset(updated_employee):
        raise HTTPException(
            status_code=400,
            detail="name, department and salary are required"
        )

    with engine.begin() as conn:
        result = conn.execute(
            text("""
                UPDATE employees
                SET name = :name,
                    department = :department,
                    salary = :salary
                WHERE id = :employee_id
            """),
            {
                "name": updated_employee["name"],
                "department": updated_employee["department"],
                "salary": updated_employee["salary"],
                "employee_id": employee_id
            }
        )

        if result.rowcount == 0:
            raise HTTPException(
                status_code=404,
                detail="Employee not found"
            )

    return {
        "message": "Employee replaced successfully",
        "id": employee_id
    }


# PATCH - Update selected employee details
@app.patch("/employees/{employee_id}")
def patch_employee(employee_id: int, employee_data: dict):
    allowed_fields = {"name", "department", "salary"}

    if not employee_data:
        raise HTTPException(
            status_code=400,
            detail="Provide at least one field to update"
        )

    if not set(employee_data).issubset(allowed_fields):
        raise HTTPException(
            status_code=400,
            detail="Only name, department and salary can be updated"
        )

    set_clause = ", ".join(
        f"{field} = :{field}" for field in employee_data
    )

    params = dict(employee_data)
    params["employee_id"] = employee_id

    with engine.begin() as conn:
        result = conn.execute(
            text(f"""
                UPDATE employees
                SET {set_clause}
                WHERE id = :employee_id
            """),
            params
        )

        if result.rowcount == 0:
            exists = conn.execute(
                text("""
                    SELECT id FROM employees
                    WHERE id = :employee_id
                """),
                {"employee_id": employee_id}
            ).first()

            if exists is None:
                raise HTTPException(
                    status_code=404,
                    detail="Employee not found"
                )

    return {
        "message": "Employee partially updated successfully",
        "id": employee_id
    }


# DELETE - Delete employee
@app.delete("/employees/{employee_id}")
def delete_employee(employee_id: int):
    with engine.begin() as conn:
        result = conn.execute(
            text("""
                DELETE FROM employees
                WHERE id = :employee_id
            """),
            {"employee_id": employee_id}
        )

        if result.rowcount == 0:
            raise HTTPException(
                status_code=404,
                detail="Employee not found"
            )

    return {
        "message": "Employee deleted successfully"
    }
