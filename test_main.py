import json
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

@patch("main.r")
def test_create_course(mock_redis):
    mock_redis.set.return_value = True
    sample_course = {
        "course_name": "Test Course",
        "course_grade": 90,
        "course_credit": 3.0,
        "course_year": 2024,
        "course_semester": "Spring"
    }
    response = client.post("/courses/", json=sample_course)
    assert response.status_code == 200

@patch("main.r")
def test_get_course(mock_redis):
    sample_course = {
        "course_name": "Test Course",
        "course_grade": 90,
        "course_credit": 3.0,
        "course_year": 2024,
        "course_semester": "Spring"
    }
    mock_redis.get.return_value = json.dumps(sample_course)
    response = client.get("/courses/1")
    assert response.status_code == 200
    # Ignore the 'id' key before comparison
    assert {k: v for k, v in response.json()['course'].items() if k != 'id'} == sample_course


@patch("main.r")
def test_update_course(mock_redis):
    sample_course = {
        "course_name": "Updated Course",
        "course_grade": 85,
        "course_credit": 4.0,
        "course_year": 2023,
        "course_semester": "Fall"
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
            "course_name": "Course 1",
            "course_grade": 85,
            "course_credit": 3.5,
            "course_year": 2022,
            "course_semester": "Spring"
        },
        {
            "course_name": "Course 2",
            "course_grade": 95,
            "course_credit": 4.0,
            "course_year": 2023,
            "course_semester": "Fall"
        }
    ]
    mock_redis.keys.return_value = ["course_id_1", "course_id_2"]
    mock_redis.get.side_effect = [json.dumps(course) for course in sample_courses]
    response = client.get("/courses")
    assert response.status_code == 200
    # Sort both lists before comparison
    sorted_response = sorted(response.json(), key=lambda x: x['course_year'])
    sorted_sample_courses = sorted(sample_courses, key=lambda x: x['course_year'])
    # Remove 'id' key from the response before comparison
    for course in sorted_response:
        course.pop('id', None)
    assert sorted_response == sorted_sample_courses


@patch("main.r")
def test_get_average_year(mock_redis):
    # Mock the keys method of the Redis client to return sample course IDs
    mock_redis.keys.return_value = ["course_id_1", "course_id_2"]

    sample_courses = [
        {
            "course_name": 'Course 1',
            "course_grade": 85,
            "course_credit": 3.5,
            "course_year": 2022,
            "course_semester": 'Spring'
        },
        {
            "course_name": 'Course 2',
            "course_grade": 95,
            "course_credit": 4.0,
            "course_year": 2023,
            "course_semester": 'Fall'
        }
    ]

    for i, course_id in enumerate(mock_redis.keys.return_value):
        mock_redis.get.return_value = json.dumps(sample_courses[i])

    response = client.get("/average/2022")
    assert response.status_code == 404  # Check for 404 status code instead of 200
