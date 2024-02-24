import json
from fastapi.testclient import TestClient
from main import app
from pydantic import BaseModel
from unittest.mock import patch

client = TestClient(app)

class Course(BaseModel):
    course_name: str
    course_grade: int
    course_credit: float
    course_year: int
    course_semester: str

class CourseInResponse(BaseModel):
    course_name: str
    course_grade: int
    course_credit: float
    course_year: int
    course_semester: str

class CourseInDB(BaseModel):
    id: str
    course_name: str
    course_grade: int
    course_credit: float
    course_year: int
    course_semester: str

@patch("main.r")
def test_create_course(mock_redis):
    mock_redis.set.return_value = True
    sample_course = {
        "course_name": "EASS",
        "course_grade": 95,
        "course_credit": 3.5,
        "course_year": 2024,
        "course_semester": "Semester A"
    }
    response = client.post("/courses/", json=sample_course)
    assert response.status_code == 200
    assert response.json()["course_name"] == sample_course["course_name"]
    # Add more assertions for other fields if needed

@patch("main.r")
def test_get_course(mock_redis):
    sample_course = {
        "course_name": "EASS",
        "course_grade": 95,
        "course_credit": 3.5,
        "course_year": 2024,
        "course_semester": "Semester A"
    }
    mock_redis.get.return_value = json.dumps(sample_course)
    response = client.get("/courses/1")
    assert response.status_code == 200
    # Ignore the 'id' key before comparison
    assert {k: v for k, v in response.json()['course'].items() if k != 'id'} == sample_course

@patch("main.r")
def test_update_course(mock_redis):
    sample_course = {
        "course_name": "EASS - Updated",
        "course_grade": 100,
        "course_credit": 4.0,
        "course_year": 2023,
        "course_semester": "Semester B"
    }
    mock_redis.set.return_value = True
    response = client.put("/courses/1", json=sample_course)
    assert response.status_code == 200

@patch("main.r")
def test_delete_course(mock_redis):
    mock_redis.delete.return_value = True
    response = client.delete("/courses/1")
    assert response.status_code == 200

@patch("main.r")
def test_get_all_courses(mock_redis):
    sample_courses = [
        {
            "course_name": "Deep Learning",
            "course_grade": 85,
            "course_credit": 3.5,
            "course_year": 2022,
            "course_semester": "Semester A"
        },
        {
            "course_name": "Data Science",
            "course_grade": 93,
            "course_credit": 4.0,
            "course_year": 2023,
            "course_semester": "Semester B"
        }
    ]
    mock_redis.keys.return_value = ["course_id_1", "course_id_2"]
    mock_redis.get.side_effect = [json.dumps(course) for course in sample_courses]
    response = client.get("/courses")
    assert response.status_code == 200
    sorted_response = sorted(response.json(), key=lambda x: x['course_year'])
    sorted_sample_courses = sorted(sample_courses, key=lambda x: x['course_year'])
    for course in sorted_response:
        course.pop('id', None)
    assert sorted_response == sorted_sample_courses

@patch("main.r")
def test_get_average_year(mock_redis):
    mock_redis.keys.return_value = ["course_id_1", "course_id_2"]

    sample_courses = [
        {
            "course_name": "Deep Learning",
            "course_grade": 85,
            "course_credit": 3.5,
            "course_year": 2022,
            "course_semester": "Semester A"
        },
        {
            "course_name": "Data Science",
            "course_grade": 93,
            "course_credit": 4.0,
            "course_year": 2023,
            "course_semester": "Semester B"
        }
    ]

    for i, course_id in enumerate(mock_redis.keys.return_value):
        mock_redis.get.return_value = json.dumps(sample_courses[i])

    response = client.get("/average/2022")
    assert response.status_code == 404
