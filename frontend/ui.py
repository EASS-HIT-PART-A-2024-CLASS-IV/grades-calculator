import json
import streamlit as st
import requests
from requests.exceptions import RequestException
import time
from datetime import datetime
import pandas as pd
import matplotlib
import matplotlib.pyplot as plt
import redis
import base64
from collections import defaultdict



# Backend URL
BACKEND_URL = "http://localhost:8080"

current_year = datetime.now().year

r = redis.Redis(host="redis", port=6379, db=0)



# MENU FUNCTIONS:

def create_course():
    st.subheader("Add A New Course")
    # Input fields for course details
    course_name = st.text_input("Course Name")
    course_grade = st.slider("Course Grade", min_value=0, max_value=100, step=1, value=85)
    course_credit = st.number_input("Course Credit", min_value=0.0, step=0.5, value=2.5)
    course_year = st.number_input("Course Academic Year", step=1, value=current_year)
    course_semester = st.radio("Semester", ["Semester A", "Semester B", "Semester C"])

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
        }

        try:
            response = requests.post(f"{BACKEND_URL}/courses/", json=data)
            response.raise_for_status()  # Raise an exception for HTTP errors
            st.success(f"Successfully added course: {course_name}")
        except requests.exceptions.RequestException as e:
            st.error(f"Failed to add course. Error: {e}")

def view_course():
    st.header("View Course")
    courses = get_all_courses()

    if not courses:
        st.write("No courses available.")
        return

    # Display data table with all courses
    df = pd.DataFrame(courses)
    st.dataframe(df)

    selected_course_name = st.selectbox("Select Course", [""] + [course["course_name"] for course in courses])

    if selected_course_name:
        # Call print_course() function to display the details of the selected course
        print_course(courses, selected_course_name)

        selected_course_data = next((course for course in courses if course["course_name"] == selected_course_name), None)

        if selected_course_data:
            # Add buttons for update and delete actions
            col1, col2 = st.columns(2)
            with col1:
                if st.button("Update", key=f"update_{selected_course_data['id']}"):
                    update_course(courses, selected_course_name)
            with col2:
                if st.button("Delete", key=f"delete_{selected_course_data['id']}"):
                    delete_course(courses, selected_course_name)





def calculate_average():
    st.header("Calculate Average")
    st.write("Choose the option to calculate the weighted average:")
    # Add options to calculate average
    average_options = ["All courses", "By semester & year", "According to selected courses"]
    selected_average_option = st.selectbox("Select Average Option", average_options)

    if selected_average_option == "All courses":
        calculate_weighted_average_for_all_courses()
    elif selected_average_option == "By semester & year":
        calculate_weighted_average_by_year_semester()
        plot_average_grade_by_semester()
    elif selected_average_option == "According to selected courses":
        calculate_weighted_average_for_selected_courses()

def simulate_grade_change():
    st.header("Simulate Grade Change")
    courses = get_all_courses()

    if not courses:
        st.write("No courses available.")
        return

    selected_course_name = st.selectbox("Select Course", [""] + [course["course_name"] for course in courses])

    if selected_course_name:
        selected_course_data = next((course for course in courses if course["course_name"] == selected_course_name), None)

        if selected_course_data:
            st.subheader("Selected Course Details:")
            st.markdown(f"**Course Name:** {selected_course_data['course_name']}")
            st.markdown(f"**Current Course Grade:** {selected_course_data['course_grade']}")
            st.markdown(f"**Course Credit:** {selected_course_data['course_credit']}")
            st.markdown(f"**Course Year:** {selected_course_data['course_year']}")
            st.markdown(f"**Course Semester:** {selected_course_data['course_semester']}")

            new_grade = st.slider("New Course Grade", min_value=0, max_value=100, step=1, value=selected_course_data["course_grade"])

            if st.button("Simulate Grade Change"):
                try:
                    # Store the previous grade
                    prev_grade = selected_course_data["course_grade"]

                    # Calculate the previous averages
                    prev_avg_all_courses, prev_avg_by_semester, prev_avg_by_year = calculate_previous_averages(courses)

                    # Update the grade to the new grade
                    selected_course_data["course_grade"] = new_grade

                    # Recalculate the averages with the new grade
                    updated_avg_all_courses, updated_avg_by_semester, updated_avg_by_year = calculate_updated_averages(courses)

                    # Calculate the differences
                    diff_avg_all_courses = updated_avg_all_courses - prev_avg_all_courses
                    diff_avg_by_semester = {key: updated_avg_by_semester[key] - prev_avg_by_semester[key] for key in prev_avg_by_semester}
                    diff_avg_by_year = {key: updated_avg_by_year[key] - prev_avg_by_year[key] for key in prev_avg_by_year}

                    # Create a DataFrame for the results
                    data = {
                        "Aspect": ["Total Average", selected_course_data['course_year'], selected_course_data['course_semester']],
                        "Previous Average": [prev_avg_all_courses, prev_avg_by_year[selected_course_data['course_year']], prev_avg_by_semester[selected_course_data['course_semester']]],
                        "New Average": [updated_avg_all_courses, updated_avg_by_year[selected_course_data['course_year']], updated_avg_by_semester[selected_course_data['course_semester']]],
                        "Difference": [diff_avg_all_courses, diff_avg_by_year[selected_course_data['course_year']], diff_avg_by_semester[selected_course_data['course_semester']]]
                    }
                    df = pd.DataFrame(data)
                    
                    # Remove rows where the difference is 0
                    df = df[df['Difference'] != 0]
                    
                    # Apply color to the difference column based on the sign of the difference
                    def color_negative_red(val):
                        color = 'red' if val < 0 else 'green'
                        return f'color: {color}'

                    # Display the table
                    st.subheader("Grade Change Summary")
                    st.table(df.style.applymap(color_negative_red, subset=['Difference']))
                    
                    # Reset the grade back to its original value
                    selected_course_data["course_grade"] = prev_grade
                    
                except Exception as e:
                    st.error(f"Failed to simulate grade change. Error: {e}")
        else:
            st.error("No course selected.")



# VIEW FUNCTION

def print_course(courses, selected_course_name):
    st.header("View Course")

    if not courses:
        st.write("No courses available.")
        return

    selected_course_data = next((course for course in courses if course["course_name"] == selected_course_name), None)

    if selected_course_data:
        st.subheader("Selected Course Details:")
        st.markdown(f"**Course Name:** {selected_course_data['course_name']}")
        st.markdown(f"**Course Grade:** {selected_course_data['course_grade']}")
        st.markdown(f"**Course Credit:** {selected_course_data.get('course_credit', 'Information not available')}")
        st.markdown(f"**Course Year:** {selected_course_data['course_year']}")
        st.markdown(f"**Course Semester:** {selected_course_data['course_semester']}")
        st.markdown(f"**Course ID:** {selected_course_data['id']}")
    else:
        st.error("No course selected.")

def update_course(courses, selected_course_name):
    st.header("Update Course")

    if not courses:
        st.write("No courses available.")
        return

    # Find the selected course
    selected_course = next((course for course in courses if course["course_name"] == selected_course_name), None)
    if selected_course:
        
        new_course_name = st.text_input("New Course Name", value=selected_course["course_name"])
        new_grade = st.slider("New Course Grade", min_value=0, max_value=100, step=1, value=selected_course["course_grade"])
        new_credit = st.number_input("New Course Credit", min_value=0.0, step=0.5, value=selected_course["course_credit"])
        new_year = st.number_input("New Course Year", step=1, value=selected_course["course_year"])
        new_semester = st.radio("New Semester", ["Semester A", "Semester B", "Semester C"], index=["Semester A", "Semester B", "Semester C"].index(selected_course["course_semester"]))
            
        if st.button("Update Course"):
            try:
                data = {
                    "course_name": new_course_name,
                    "course_grade": new_grade,
                    "course_credit": new_credit,
                    "course_year": new_year,
                    "course_semester": new_semester
                }
                response = requests.put(f"{BACKEND_URL}/courses/{selected_course['id']}", json=data)
                response.raise_for_status()  # Raise an exception for HTTP errors
                st.success("Course updated successfully!")
            except requests.exceptions.RequestException as e:
                st.error(f"Failed to update course. Error: {e}")
    else:
        st.error("No course selected.")

def delete_course(courses, selected_course_name):
            # Find the selected course
            selected_course = next((course for course in courses if course["course_name"] == selected_course_name), None)
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

def update_course2():
    st.header("Update Course")
    courses = get_all_courses()

    if not courses:
        st.write("No courses available.")
        return

    selected_course_name = st.selectbox("Select Course to Update", [""] + [course["course_name"] for course in courses])

    if selected_course_name:
        selected_course_data = next((course for course in courses if course["course_name"] == selected_course_name), None)

        if selected_course_data:
            st.subheader("Selected Course Details:")
            st.markdown(f"**Course Name:** {selected_course_data['course_name']}")
            st.markdown(f"**Current Course Grade:** {selected_course_data['course_grade']}")
            st.markdown(f"**Course Credit:** {selected_course_data['course_credit']}")
            st.markdown(f"**Course Year:** {selected_course_data['course_year']}")
            st.markdown(f"**Course Semester:** {selected_course_data['course_semester']}")

            new_course_name = st.text_input("New Course Name", value=selected_course_data["course_name"])
            new_grade = st.slider("New Course Grade", min_value=0, max_value=100, step=1, value=selected_course_data["course_grade"])
            new_credit = st.number_input("New Course Credit", min_value=0.0, step=0.5, value=selected_course_data["course_credit"])
            new_year = st.number_input("New Course Year", step=1, value=selected_course_data["course_year"])
            new_semester = st.radio("New Semester", ["Semester A", "Semester B", "Semester C"], index=["Semester A", "Semester B", "Semester C"].index(selected_course_data["course_semester"]))

            if st.button("Update Course"):
                try:
                    data = {
                        "course_name": new_course_name,
                        "course_grade": new_grade,
                        "course_credit": new_credit,
                        "course_year": new_year,
                        "course_semester": new_semester
                    }
                    response = requests.put(f"{BACKEND_URL}/courses/{selected_course_data['id']}", json=data)
                    response.raise_for_status()  # Raise an exception for HTTP errors
                    st.success("Course updated successfully!")
                except requests.exceptions.RequestException as e:
                    st.error(f"Failed to update course. Error: {e}")
        else:
            st.error("No course selected.")


# AVERAGE CALCULATOR FUNCTIONS:

def calculate_weighted_average_for_all_courses():
    # Get all courses from the backend
    courses = get_all_courses()
    # Check if courses exist
    if courses:
        # Convert courses data to DataFrame
        df = pd.DataFrame(courses)
        # Check if course_credit column exists
        if 'course_credit' in df.columns:
            # Display table
            st.write("All Course Details:")
            st.write(df)
            
            # Calculate weighted average and total credits
            total_weighted_score = (df['course_grade'] * df['course_credit']).sum()
            total_credits = df['course_credit'].sum()
            weighted_average = total_weighted_score / total_credits if total_credits > 0 else 0
            
            # Display weighted average and total credits
            st.write(f"Your weighted average is: {weighted_average:.2f}")
            st.write(f"Your total credits is: {total_credits:.2f}")
        else:
            st.write("No course credit information available for any course.")
    else:
        st.write("No courses available.")

def calculate_weighted_average_by_semester():
    # Get all courses from the backend
    courses = get_all_courses()
    # Check if courses exist
    if courses:
        # Convert courses data to DataFrame
        df = pd.DataFrame(courses)
        # Check if course_credit column exists
        if 'course_credit' in df.columns:
            # Group courses by year
            year_groups = df.groupby('course_year')
            for year, year_df in year_groups:
                st.subheader(f"Year: {year}")
                year_semester_groups = year_df.groupby('course_semester')
                for semester, semester_df in year_semester_groups:
                    st.subheader(f"Semester: {semester}")
                    st.write(semester_df)
                    total_weighted_score = (semester_df['course_grade'] * semester_df['course_credit']).sum()
                    total_credits = semester_df['course_credit'].sum()
                    weighted_average = total_weighted_score / total_credits if total_credits > 0 else 0
                    st.write(f"Weighted average for {semester}: {weighted_average:.2f}")

                # Calculate and display the yearly summary
                st.subheader(f"Yearly Summary for {year}")
                total_year_weighted_score = (year_df['course_grade'] * year_df['course_credit']).sum()
                total_year_credits = year_df['course_credit'].sum()
                year_weighted_average = total_year_weighted_score / total_year_credits if total_year_credits > 0 else 0
                st.write(f"Total weighted average for {year}: {year_weighted_average:.2f}")
                st.write(f"Total credits for {year}: {total_year_credits:.2f}")
                
                # Plot average grade by semester for the current year
                plot_average_grade_by_semester(year, year_df)

        else:
            st.write("No course credit information available for any course.")
    else:
        st.write("No courses available.")
    
def calculate_weighted_average_by_year_semester():
    # Get all courses from the backend
    courses = get_all_courses()
    # Check if courses exist
    if courses:
        # Convert courses data to DataFrame
        df = pd.DataFrame(courses)
        # Check if course_credit column exists
        if 'course_credit' in df.columns:
            # Group courses by year
            year_groups = df.groupby('course_year')
            for year, year_df in year_groups:
                # Display year header
                st.subheader(f"Year: {year}")

                # Group courses by semester within the year
                semester_groups = year_df.groupby('course_semester')
                semester_averages = {}  # Store semester averages for plotting
                for semester, semester_df in semester_groups:
                    # Display semester subheader
                    st.subheader(f"{semester} - {year}")

                    # Display courses for this semester
                    st.write(semester_df)

                    # Calculate weighted average and total credits for this semester
                    total_weighted_score = (semester_df['course_grade'] * semester_df['course_credit']).sum()
                    total_credits = semester_df['course_credit'].sum()
                    weighted_average = total_weighted_score / total_credits if total_credits > 0 else 0

                    # Display semester summary
                    st.write(f"Weighted average for {semester}: {weighted_average:.2f}")
                    st.write(f"Total credits: {total_credits:.2f}")

                    # Store semester average for plotting
                    semester_averages[semester] = weighted_average

                # Yearly summary
                yearly_total_weighted_score = (year_df['course_grade'] * year_df['course_credit']).sum()
                yearly_total_credits = year_df['course_credit'].sum()
                yearly_weighted_average = yearly_total_weighted_score / yearly_total_credits if yearly_total_credits > 0 else 0
                st.subheader(f"Year {year} Summary")
                st.write(f"Yearly weighted average: {yearly_weighted_average:.2f}")
                st.write(f"Total credits: {yearly_total_credits:.2f}")


        else:
            st.write("No course credit information available for any course.")
    else:
        st.write("No courses available.")

def calculate_weighted_average_for_selected_courses():
    # Get all courses from the backend
    courses = get_all_courses()
    # Check if courses exist
    if courses:
        # Convert courses data to DataFrame
        df = pd.DataFrame(courses)
        # Display a selection box to choose courses
        selected_courses = st.multiselect("Select courses", df['course_name'].unique())
        if selected_courses:
            # Filter DataFrame to include only selected courses
            selected_df = df[df['course_name'].isin(selected_courses)]
            if 'course_credit' in selected_df.columns:
                # Display table of selected courses
                st.write("Selected Courses:")
                st.write(selected_df)
                # Calculate weighted average and total credits for selected courses
                total_weighted_score = (selected_df['course_grade'] * selected_df['course_credit']).sum()
                total_credits = selected_df['course_credit'].sum()
                weighted_average = total_weighted_score / total_credits if total_credits > 0 else 0
                st.write(f"Weighted average for selected courses: {weighted_average:.2f}")
            else:
                st.write("No course credit information available for any selected course.")
        else:
            st.write("No courses selected.")
    else:
        st.write("No courses available.")

def calculate_weighted_average_by_year():
    courses = r.keys()
    year_grades_credits = {}
    
    for key in courses:
        course_data = json.loads(r.get(key))
        year = course_data["course_year"]
        grade = course_data["course_grade"]
        credit = course_data["course_credit"]
        
        if year not in year_grades_credits:
            year_grades_credits[year] = {"total_grade_credit": 0, "total_credits": 0}
            
        year_grades_credits[year]["total_grade_credit"] += grade * credit
        year_grades_credits[year]["total_credits"] += credit
    
    average_grades_by_year = {}
    
    for year, data in year_grades_credits.items():
        if data["total_credits"] > 0:
            average_grade = data["total_grade_credit"] / data["total_credits"]
            average_grades_by_year[year] = average_grade
            
    return average_grades_by_year


# SIMULATOR FUNCTIONS:

def calculate_previous_averages(courses):
    # Convert courses data to DataFrame
    df = pd.DataFrame(courses)
    
    # Calculate previous average for all courses
    total_weighted_score_all = (df['course_grade'] * df['course_credit']).sum()
    total_credits_all = df['course_credit'].sum()
    prev_avg_all_courses = total_weighted_score_all / total_credits_all if total_credits_all > 0 else 0
    
    # Group courses by semester
    semester_groups = df.groupby('course_semester')
    prev_avg_by_semester = {}
    for semester, semester_df in semester_groups:
        total_weighted_score = (semester_df['course_grade'] * semester_df['course_credit']).sum()
        total_credits = semester_df['course_credit'].sum()
        prev_avg_by_semester[semester] = total_weighted_score / total_credits if total_credits > 0 else 0
    
    # Group courses by year
    year_groups = df.groupby('course_year')
    prev_avg_by_year = {}
    for year, year_df in year_groups:
        total_weighted_score = (year_df['course_grade'] * year_df['course_credit']).sum()
        total_credits = year_df['course_credit'].sum()
        prev_avg_by_year[year] = total_weighted_score / total_credits if total_credits > 0 else 0
    
    return prev_avg_all_courses, prev_avg_by_semester, prev_avg_by_year

def calculate_updated_averages(courses):
    # Convert courses data to DataFrame
    df = pd.DataFrame(courses)
    
    # Calculate updated average for all courses
    total_weighted_score_all = (df['course_grade'] * df['course_credit']).sum()
    total_credits_all = df['course_credit'].sum()
    updated_avg_all_courses = total_weighted_score_all / total_credits_all if total_credits_all > 0 else 0
    
    # Group courses by semester
    semester_groups = df.groupby('course_semester')
    updated_avg_by_semester = {}
    for semester, semester_df in semester_groups:
        total_weighted_score = (semester_df['course_grade'] * semester_df['course_credit']).sum()
        total_credits = semester_df['course_credit'].sum()
        updated_avg_by_semester[semester] = total_weighted_score / total_credits if total_credits > 0 else 0
    
    # Group courses by year
    year_groups = df.groupby('course_year')
    updated_avg_by_year = {}
    for year, year_df in year_groups:
        total_weighted_score = (year_df['course_grade'] * year_df['course_credit']).sum()
        total_credits = year_df['course_credit'].sum()
        updated_avg_by_year[year] = total_weighted_score / total_credits if total_credits > 0 else 0
    
    return updated_avg_all_courses, updated_avg_by_semester, updated_avg_by_year



# GENERAL FUNCTIONS

def get_all_courses():
    try:
        response = requests.get(f"{BACKEND_URL}/courses")
        response.raise_for_status()
        return response.json()
    except RequestException as e:
        st.error(f"Failed to fetch courses: {e}")
        return []

def plot_average_grade_by_semester():
    # Get all courses from the backend
    courses = get_all_courses()
    # Check if courses exist
    if courses:
        # Convert courses data to DataFrame
        df = pd.DataFrame(courses)
        # Check if course_credit column exists
        if 'course_credit' in df.columns:
            # Create a new column combining year and semester
            df['year_semester'] = df['course_year'].astype(str) + '_' + df['course_semester']

            # Group courses by year and semester and calculate weighted average
            year_semester_groups = df.groupby('year_semester')
            averages = {}  # Store averages for each year and semester pair
            for year_semester, year_semester_df in year_semester_groups:
                total_weighted_score = (year_semester_df['course_grade'] * year_semester_df['course_credit']).sum()
                total_credits = year_semester_df['course_credit'].sum()
                weighted_average = total_weighted_score / total_credits if total_credits > 0 else 0
                averages[year_semester] = weighted_average

            # Sort the keys of the averages dictionary by year and then by semester
            sorted_keys = sorted(averages.keys(), key=lambda x: (int(x.split('_')[0]), x.split('_')[1]))
            sorted_averages = {key: averages[key] for key in sorted_keys}

            # Plotting the line graph
            if sorted_averages:  # Check if there are any averages to plot
                plt.figure(figsize=(10, 6))
                plt.plot(list(sorted_averages.keys()), list(sorted_averages.values()), marker='o', linestyle='-')
                plt.title('Weighted Average by Year and Semester')
                plt.xlabel('Year-Semester')
                plt.ylabel('Weighted Average')
                plt.xticks(rotation=45)  # Rotate x-axis labels for better visibility
                plt.tight_layout()
                st.pyplot(plt)  # Display the plot in Streamlit
            else:
                st.write("No data available to plot.")
        else:
            st.write("No course credit information available for any course.")
    else:
        st.write("No courses available.")

def home():
    # Add logo and title for the home page
    st.image(r"/home/im159/grades-calculator/grades-calculator/frontend/LOGO-CALCULATOR2.png", width=450)
    st.title("Welcome to the Grades Calculator App!")
    st.write("This app allows you to view, add, and calculate averages for courses.")




def main():


    st.sidebar.image(r"/home/im159/grades-calculator/grades-calculator/frontend/LOGO-CALCULATOR2.png", width=250)

    menu = ["Home", "Create", "View/ Update/ Delete", "Update Course", "Calculate Average", "Simulate Grade Change"]
    choice = st.sidebar.selectbox("Menu", menu)

    if choice == "Home":
        home()
    elif choice == "Create":
        create_course()
    elif choice == "View/ Update/ Delete":
        view_course()
    elif choice == "Calculate Average":
        calculate_average()
    elif choice == "Simulate Grade Change":
        simulate_grade_change()
    elif choice == "Update Course":
        update_course2()  # Call the new function here


if __name__ == "__main__":
    main()
