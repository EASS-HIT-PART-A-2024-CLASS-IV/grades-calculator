import streamlit as st
import requests
from requests.exceptions import RequestException
import time
from datetime import datetime
import pandas as pd
import matplotlib
import matplotlib.pyplot as plt


# Backend URL
BACKEND_URL = "http://localhost:8080"

current_year = datetime.now().year




def create_course():
    st.subheader("Add A New Course")
    # Input fields for course details
    course_name = st.text_area("Course Name")
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

    selected_course_name = st.selectbox("Select Course", [""] + [course["course_name"] for course in courses])

    if selected_course_name:
        selected_course_data = next((course for course in courses if course["course_name"] == selected_course_name), None)

        if selected_course_data:
            st.subheader("Selected Course Details:")
            st.markdown(f"**Course Name:** {selected_course_data['course_name']}")
            st.markdown(f"**Course Grade:** {selected_course_data['course_grade']}")
            if 'course_credit' in selected_course_data:
                st.markdown(f"**Course Credit:** {selected_course_data['course_credit']}")
            else:
                st.markdown("**Course Credit:** information not available")
            st.markdown(f"**Course Year:** {selected_course_data['course_year']}")
            st.markdown(f"**Course Semester:** {selected_course_data['course_semester']}")

            
            # Add buttons for update and delete actions
            col1, col2 = st.columns(2)
            with col1:
                if st.button("Update", key=f"update_{selected_course_data['id']}"):
                    update_course(selected_course_data)
            with col2:
                if st.button("Delete", key=f"delete_{selected_course_data['id']}"):
                    delete_course(selected_course_data)
        else:
            st.write("No course selected.")




def get_all_courses():
    try:
        response = requests.get(f"{BACKEND_URL}/courses")
        response.raise_for_status()
        return response.json()
    except RequestException as e:
        st.error(f"Failed to fetch courses: {e}")
        return []
    



def delete_course(course):
    st.subheader("Delete Course")
    confirmation = st.checkbox(f"Confirm deletion of course: {course['course_name']}")

    if confirmation:
        try:
            response = requests.delete(f"{BACKEND_URL}/courses/{course['id']}")
            if response.status_code == 200:
                st.success(f"Successfully deleted course: {course['course_name']}")
            else:
                st.error(f"Failed to delete course: {response.text}")
        except requests.exceptions.RequestException as e:
            st.error(f"Error occurred while deleting course: {e}")





def calculate_average():
    st.header("Calculate Average")
    st.write("Choose the option to calculate the weighted average:")
    # Add options to calculate average
    average_options = ["For all courses studied", "According to semester", "By year", "According to selected courses"]
    selected_average_option = st.selectbox("Select Average Option", average_options)

    if selected_average_option == "For all courses studied":
        calculate_weighted_average_for_all_courses()
    elif selected_average_option == "According to semester":
        calculate_weighted_average_by_semester()
    elif selected_average_option == "By year":
        calculate_weighted_average_by_year()
    elif selected_average_option == "According to selected courses":
        calculate_weighted_average_for_selected_courses()




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
            # Create a new column combining year and semester
            df['year_semester'] = df['course_year'].astype(str) + '_' + df['course_semester']

            # Group courses by year and semester and calculate weighted average
            year_semester_groups = df.groupby('year_semester')
            averages = {}  # Store averages for each year and semester pair
            for year_semester, year_semester_df in year_semester_groups:
                st.write(f"Year-Semester: {year_semester}")
                st.write(year_semester_df)
                total_weighted_score = (year_semester_df['course_grade'] * year_semester_df['course_credit']).sum()
                total_credits = year_semester_df['course_credit'].sum()
                weighted_average = total_weighted_score / total_credits if total_credits > 0 else 0
                st.write(f"Weighted average for {year_semester}: {weighted_average:.2f}")
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



def calculate_weighted_average_by_year():
    # Get all courses from the backend
    courses = get_all_courses()
    # Check if courses exist
    if courses:
        # Convert courses data to DataFrame
        df = pd.DataFrame(courses)
        # Check if course_credit column exists
        if 'course_credit' in df.columns:
            # Group courses by year and calculate weighted average for each year
            year_groups = df.groupby('course_year')
            for year, year_df in year_groups:
                st.write(f"Year: {year}")
                st.write(year_df)
                total_weighted_score = (year_df['course_grade'] * year_df['course_credit']).sum()
                total_credits = year_df['course_credit'].sum()
                weighted_average = total_weighted_score / total_credits if total_credits > 0 else 0
                st.write(f"Weighted average for {year}: {weighted_average:.2f}")
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




def update_course(course_data):
    st.subheader("Update Course")
    
    new_course_name = st.text_input("New Course Name", value=course_data["course_name"])
    new_course_grade = st.slider("New Course Grade", min_value=0, max_value=100, step=1, value=course_data["course_grade"])
    new_course_credit = st.number_input("New Course Credit", min_value=0.0, step=0.5, value=course_data.get("course_credit", 0.0))
    new_course_year = st.number_input("New Course Academic Year", min_value=0, step=1, value=course_data["course_year"])
    new_course_semester = st.radio("New Semester", ["Semester A", "Semester B", "Semester C"], index=["Semester A", "Semester B", "Semester C"].index(course_data["course_semester"]))

    if st.button("Update"):
        updated_course_data = {
            "course_name": new_course_name,
            "course_grade": new_course_grade,
            "course_credit": new_course_credit,
            "course_year": new_course_year,
            "course_semester": new_course_semester
        }
        
        try:
            response = requests.put(f"{BACKEND_URL}/courses/{course_data['id']}", json=updated_course_data)
            if response.status_code == 200:
                st.success("Successfully updated course.")
            else:
                st.error(f"Failed to update course. Status code: {response.status_code}")
        except requests.exceptions.RequestException as e:
            st.error(f"Failed to update course. Error: {e}")



def main():
    menu = ["Create", "View", "Average Calculator"]
    choice = st.sidebar.selectbox("Menu", menu)

    if choice == "View":
        view_course()
    elif choice == "Create":
        create_course()
    elif choice == "Average Calculator":
        calculate_average()


if __name__ == "__main__":
    main()
