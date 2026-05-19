from fastapi import FastAPI, HTTPException
from db import engine
from tables import students, create_tables
from sqlalchemy import insert, select, update, delete
from pydantic import BaseModel

app = FastAPI(title="Student Management API")

# Pydantic models for request/response
class StudentCreate(BaseModel):
    name: str
    age: int
    city: str

class StudentResponse(BaseModel):
    id: int
    name: str
    age: int
    city: str

# Initialize database on startup
@app.on_event("startup")
def startup_event():
    create_tables()

# ===== CREATE =====
@app.post("/students", response_model=StudentResponse)
def create_student(student: StudentCreate):
    """Create a new student"""
    try:
        with engine.connect() as conn:
            query = insert(students).values(
                name=student.name,
                age=student.age,
                city=student.city
            )
            result = conn.execute(query)
            conn.commit()

            # Get the created student
            student_id = result.lastrowid
            return StudentResponse(
                id=student_id,
                name=student.name,
                age=student.age,
                city=student.city
            )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# ===== READ/FETCH =====
@app.get("/students", response_model=list[StudentResponse])
def get_all_students():
    """Get all students"""
    with engine.connect() as conn:
        query = select(students)
        result = conn.execute(query)
        students_list = []
        for row in result:
            students_list.append(StudentResponse(
                id=row.id,
                name=row.name,
                age=row.age,
                city=row.city
            ))
        return students_list

@app.get("/students/{student_id}", response_model=StudentResponse)
def get_student(student_id: int):
    """Get a specific student by ID"""
    with engine.connect() as conn:
        query = select(students).where(students.c.id == student_id)
        result = conn.execute(query)
        row = result.fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="Student not found")
        return StudentResponse(
            id=row.id,
            name=row.name,
            age=row.age,
            city=row.city
        )

# ===== UPDATE =====
@app.put("/students/{student_id}", response_model=StudentResponse)
def update_student(student_id: int, student: StudentCreate):
    """Update a student"""
    with engine.connect() as conn:
        # Check if student exists
        query = select(students).where(students.c.id == student_id)
        result = conn.execute(query)
        if not result.fetchone():
            raise HTTPException(status_code=404, detail="Student not found")

        # Update the student
        update_query = update(students).where(students.c.id == student_id).values(
            name=student.name,
            age=student.age,
            city=student.city
        )
        conn.execute(update_query)
        conn.commit()

        return StudentResponse(
            id=student_id,
            name=student.name,
            age=student.age,
            city=student.city
        )

# ===== DELETE =====
@app.delete("/students/{student_id}")
def delete_student(student_id: int):
    """Delete a student"""
    with engine.connect() as conn:
        # Check if student exists
        query = select(students).where(students.c.id == student_id)
        result = conn.execute(query)
        if not result.fetchone():
            raise HTTPException(status_code=404, detail="Student not found")

        # Delete the student
        delete_query = delete(students).where(students.c.id == student_id)
        conn.execute(delete_query)
        conn.commit()

        return {"message": f"Student {student_id} deleted successfully"}

# Additional endpoints
@app.put("/students/update-city")
def update_city_by_name(name: str, new_city: str):
    """Update city of a student by name"""
    with engine.connect() as conn:
        query = update(students).where(students.c.name == name).values(city=new_city)
        result = conn.execute(query)
        conn.commit()
        if result.rowcount == 0:
            raise HTTPException(status_code=404, detail="Student not found")
        return {"message": f"Updated {name}'s city to {new_city}"}

@app.delete("/students/delete-by-age")
def delete_students_by_age(age_limit: int):
    """Delete students younger than age_limit"""
    with engine.connect() as conn:
        query = delete(students).where(students.c.age < age_limit)
        result = conn.execute(query)
        conn.commit()
        return {"message": f"Deleted {result.rowcount} students with age < {age_limit}"}


# Legacy functions (for backward compatibility)
def create_user(input_name: str, input_age: int, input_city: str):
    """Insert a new student into the database"""
    with engine.connect() as conn:
        query = insert(students).values(name=input_name, age=input_age, city=input_city)
        conn.execute(query)
        conn.commit()
        print(f"✓ Created student: {input_name}")


def fetch_all_students():
    """Fetch and display all students from the database"""
    with engine.connect() as conn:
        query = select(students)
        result = conn.execute(query)

        print("\n--- All Students ---")
        for row in result:
            print(f"ID: {row.id}, Name: {row.name}, Age: {row.age}, City: {row.city}")


def update_city_by_name(name: str, new_city: str):
    """Update the city of a student by their name"""
    with engine.connect() as conn:
        query = update(students).where(students.c.name == name).values(city=new_city)
        conn.execute(query)
        conn.commit()
        print(f"✓ Updated {name}'s city to {new_city}")


def delete_students_by_age(age_limit: int):
    """Delete all students whose age is less than the age_limit"""
    with engine.connect() as conn:
        query = delete(students).where(students.c.age < age_limit)
        conn.execute(query)
        conn.commit()
        print(f"✓ Deleted students with age < {age_limit}")


# Test the functions (only runs when executed directly)
if __name__ == "__main__":
    # Create tables first
    create_tables()

    # Create some students (age must be > 18 due to CHECK constraint)
    create_user("Rahul", 22, "Mumbai")
    create_user("Pradeep", 25, "Delhi")
    create_user("Sreshta", 19, "Pune")
    create_user("Aviva", 23, "Bangalore")

    # Fetch all students
    fetch_all_students()

    # Update Rahul's city
    update_city_by_name("Rahul", "Chennai")

    # Delete students younger than 20
    delete_students_by_age(20)

    # Fetch remaining students
    fetch_all_students()
