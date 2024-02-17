import json
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi import HTTPException
import uuid
import redis
from dataclasses import dataclass, asdict
from typing import List

app = FastAPI()
r = redis.Redis(host="redis", port=6379, db=0)

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@dataclass
class Course:
    course_name: str
    course_grade: int
    course_credit: float
    course_year: int
    course_semester: str

    def to_dict(self):
        return asdict(self)

@app.post("/courses/")
def create_course(course: Course):
    new_course = json.dumps(course.to_dict())
    item_id = str(uuid.uuid4())

    # Log the received data
    print("Received data for new course:")
    print(new_course)

    try:
        # Attempt to add the course to Redis
        r.set(item_id, new_course)
        return {"id": item_id}
    except Exception as e:
        # Log any errors
        print(f"Error occurred while adding course: {e}")
        raise HTTPException(status_code=500, detail=f"Error occurred while adding course: {e}")
    
    
@app.put("/courses/{item_id}")
async def update_course(item_id: str, course: Course):
    try:
        print("Received item_id:", item_id)
        print("Received course data:", course)

        # Convert the received course object to a dictionary
        course_dict = course.to_dict()

        # Check if the course with the given item_id exists
        if r.exists(item_id):
            # Update the course in Redis with the new data
            r.set(item_id, json.dumps(course_dict))
            return {"update": "success"}
        else:
            # If the course does not exist, raise a 404 error
            raise HTTPException(status_code=404, detail="Course not found")
    except Exception as e:
        print("An error occurred during course update:", e)
        return {"update": "failed", "error": str(e)}



@app.delete("/courses/{item_id}")
async def delete_course(item_id: str):
    try:
        print("Attempting to delete course with item_id:", item_id)

        # Check if the course exists
        if r.exists(item_id):
            print("Course found. Deleting...")
            r.delete(item_id)
            print("Course deleted successfully.")
            return {"message": "Course deleted successfully"}
        else:
            print("Course not found.")
            raise HTTPException(status_code=404, detail="Course not found")
    except Exception as e:
        error_message = f"Failed to delete course: {str(e)}"
        print(error_message)
        raise HTTPException(status_code=500, detail=error_message)
    


@app.get("/courses/{item_id}")
async def get_course(item_id: str):
    course = r.get(item_id)
    return {"course": json.loads(course)}

@app.get("/courses")
async def get_all_courses():
    courses = r.keys()
    res = []
    for key in courses:
        course_data = json.loads(r.get(key))
        course_data["id"] = key
        res.append(course_data)
    return res

@app.get("/courses/average-year")
async def get_average_year():
    courses = r.keys()
    year_semester_grades = {}
    for key in courses:
        course_data = json.loads(r.get(key))
        year = course_data["course_year"]
        semester = course_data["course_semester"]
        grade = course_data["course_grade"]
        year_semester = f"{year}_{semester}"
        if year_semester not in year_semester_grades:
            year_semester_grades[year_semester] = {"grades": [], "count": 0}
        year_semester_grades[year_semester]["grades"].append(grade)
        year_semester_grades[year_semester]["count"] += 1

    average_grades = {}
    for year_semester, data in year_semester_grades.items():
        average_grade = sum(data["grades"]) / data["count"]
        average_grades[year_semester] = average_grade
    return average_grades

