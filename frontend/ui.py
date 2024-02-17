from datetime import datetime
import streamlit as st
import requests
import time
import pandas as pd
import plotly.express as px

# Backend URL
BACKEND_URL = "http://localhost:8080"

current_year = datetime.now().year

def create_course():
    st.subheader("Add A New Course")
    # Input fields for course details
    course_name = st.text_area("Course Name")
    course_grade = st.slider("Course Grade", min_value=0, max_value=100, step=1, value=75)
    course_credit = st.number_input("Course Credit", min_value=0.0, step=0.5)
    course_year = st.number_input("Course Academic Year", min_value=0, step=1, value=current_year)
    course_semester = st.radio("Semester", ["Semester A", "Semester B", "Semester C"])
    course_points = st.number_input("Course Points", min_value=0.0, step=0.1)  # Add course points field

    if st.button("Add New Course"):
        # Check if the user has selected an option other than the blank one
        if course_semester == "":
            st.warning("Please select a semester.")
            return

        data = {
            "course_name": course_name,
            "course_grade": course_grade,
            "course_credit": course_credit,
            "course_year": course_year,
            "course_semester": course_semester,
            "course_points": course_points  # Include course points in the data
        }

        max_retries = 3
        retries = 0
        while retries < max_retries:
            try:
                response = requests.post(f"{BACKEND_URL}/courses/", json=data)
                response.raise_for_status()  # Raise an exception for HTTP errors
                st.success(f"Successfully added course: {course_name}")
                break  # Exit loop if successful
            except requests.exceptions.RequestException as e:
                retries += 1
                if retries == max_retries:
                    st.error(f"Failed to add course after {max_retries} attempts. Please try again later.")
                    st.error(f"Error message: {e}")
                    break
                else:
                    st.warning(f"Failed to connect to backend. Retrying in 3 seconds...")
                    time.sleep(3)

def read_course():
    st.subheader("Read Course")
    
    # Fetch all courses to populate the dropdown
    all_courses_response = requests.get(f"{BACKEND_URL}/courses")
    if all_courses_response.status_code == 200:
        all_courses = all_courses_response.json()
        course_names = [course["course_name"] for course in all_courses]
        
        # Dropdown to select the course name
        selected_course_name = st.selectbox("Select Course Name", course_names)
        
        if st.button("Search"):
            # Find the course with the selected name
            selected_course = next((course for course in all_courses if course["course_name"] == selected_course_name), None)
            if selected_course:
                # Display course details
                st.write(selected_course)
                if st.button("Update Course"):
                    # Redirect to update course page
                    update_course(selected_course)
            else:
                st.error("Course not found.")
    else:
        st.error(f"Failed to fetch courses: {all_courses_response.text}")

def update_course(course):
    st.subheader("Update Course")
    # Input fields for course details
    new_course_name = st.text_input("New Course Name", value=course["course_name"])
    new_course_grade = st.slider("New Course Grade", min_value=0, max_value=100, step=1, value=course["course_grade"])
    new_course_credit = st.number_input("New Course Credit", min_value=0.0, step=0.5, value=course["course_credit"])
    new_course_year = st.number_input("New Course Academic Year", min_value=0, step=1, value=course["course_year"])
    new_course_semester = st.radio("New Semester", ["Semester A", "Semester B", "Semester C"], index=["Semester A", "Semester B", "Semester C"].index(course["course_semester"]))
    
    if st.button("Update"):
        # Check if the user has selected an option other than the blank one
        if new_course_semester == "":
            st.warning("Please select a semester.")
            return

        data = {
            "course_name": new_course_name,
            "course_grade": new_course_grade,
            "course_credit": new_course_credit,
            "course_year": new_course_year,
            "course_semester": new_course_semester,
            "course_points": course["course_points"]  # Include course points in the data
        }

        max_retries = 3
        retries = 0
        while retries < max_retries:
            try:
                response = requests.put(f"{BACKEND_URL}/courses/{course['id']}", json=data)
                response.raise_for_status()  # Raise an exception for HTTP errors
                st.success("Successfully updated course.")
                break  # Exit loop if successful
            except requests.exceptions.RequestException as e:
                retries += 1
                if retries == max_retries:
                    st.error(f"Failed to update course after {max_retries} attempts. Please try again later.")
                    st.error(f"Error message: {e}")
                    break
                else:
                    st.warning(f"Failed to connect to backend. Retrying in 3 seconds...")
                    time.sleep(3)

def delete_course():
    st.subheader("Delete Course")
    # Input field for course name
    course_to_delete = st.text_input("Course To Delete")
    if st.button("Delete Course"):
        # Check if the user has entered a course name
        if not course_to_delete:
            st.warning("Please enter a course name.")
            return

        # Fetch all courses
        all_courses_response = requests.get(f"{BACKEND_URL}/courses")
        if all_courses_response.status_code == 200:
            all_courses = all_courses_response.json()
            # Find the course with the selected name
            selected_course = next((course for course in all_courses if course["course_name"] == course_to_delete), None)
            if selected_course:
                # Delete the course
                try:
                    response = requests.delete(f"{BACKEND_URL}/courses/{selected_course['id']}")
                    response.raise_for_status()  # Raise an exception for HTTP errors
                    st.success("Successfully deleted course.")
                except requests.exceptions.RequestException as e:
                    st.error(f"Failed to delete course. Error: {e}")
            else:
                st.error("Course not found.")
        else:
            st.error(f"Failed to fetch courses: {all_courses_response.text}")

def calculate_average():
    st.subheader("Calculate Average")
    st.write("Choose the option to calculate the weighted average:")

    average_options = ["For all courses studied", "According to semester", "By year", "According to courses I can choose"]
    selected_average_option = st.selectbox("Select Average Option", average_options)

    if selected_average_option == "For all courses studied":
        # Calculate weighted average for all courses studied
        all_courses_response = requests.get(f"{BACKEND_URL}/courses")
        if all_courses_response.status_code == 200:
            all_courses = all_courses_response.json()
            all_grades = [course["course_grade"] for course in all_courses]
            all_credits = [course["course_credit"] for course in all_courses]
            total_weighted_average = sum(grade * credit for grade, credit in zip(all_grades, all_credits)) / sum(all_credits)
            st.write(f"Weighted Average for All Courses Studied: {total_weighted_average:.2f}")
        else:
            st.error(f"Failed to fetch courses: {all_courses_response.text}")

def main():

<<<<<<< HEAD
<<<<<<< HEAD
    # Add background photo with URL
=======
    # Add background photo URL
>>>>>>> origin/main
=======
    # Add background photo URL
=======
    # Add background photo with URL
>>>>>>> 6ebdb68 (update)
>>>>>>> d92ebe0 (update)
    background_image_url = "https://png.pngtree.com/background/20210717/original/pngtree-chic-mathematics-subject-for-high-school-9th-grade-geometry-picture-image_1443162.jpg"

    # Add CSS for background photo
    st.markdown(
    f"""
    <style>
        .reportview-container {{
            background: url("{background_image_url}") no-repeat center center fixed;
            background-size: cover;
        }}
    </style>
    """,
    unsafe_allow_html=True
)

    st.title("Grades Calculator")
    menu = ["Add", "Read", "Delete", "Calculate Average"]
    choice = st.sidebar.selectbox("Menu", menu)

    if choice == "Add":
        create_course()
    elif choice == "Read":
        read_course()
    elif choice == "Delete":
        delete_course()
    elif choice == "Calculate Average":
        calculate_average()


if __name__ == '__main__':
    main()
<<<<<<< HEAD

=======
>>>>>>> origin/main
