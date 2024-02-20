
 [![image](https://github.com/EASS-HIT-PART-A-2024-CLASS-IV/grades-calculator/assets/131989545/c214de5f-f324-4313-99dd-a0301a6e06e4)
](https://github.com/EASS-HIT-PART-A-2024-CLASS-IV/grades-calculator/blob/main/frontend/mylogo.png)


# Welcome to the Grades Calculator App!

This application is designed to help you manage and analyze your courses and grades with ease. Whether you're a student keeping track of your academic progress or an educator managing course data, this app provides a user-friendly interface to view, add, update, and delete courses, calculate weighted averages, and even simulate grade changes.

Enjoy exploring your academic journey with the Grades Calculator App!

# Grades Calculator App

This project is a Grades Calculator application that built with:

- Docker Compose
- FastAPI
- Streamlit 

The application allows users to:

- Create a course
- View a course:  
  * Update a course data
  * Delete a course
- Calculate the average by: 
  * Total courses
  * Selected courses
  * Semester-year wide
- Grades simulator
  

# Prerequisites
You will need to have Docker and Docker Compose installed on your machine in order to run the application.

# Getting Started
These instructions will get you a copy of the project up and running on your local machine for development and testing purposes.

In the console, create a new directory:

```
mkdir grades-calculator
```

Change to the new directory:
```
cd grades-calculator
```

Clone the repository:
```
git clone https://github.com/EASS-HIT-PART-A-2024-CLASS-IV/grades-calculator.git
```


Change to the new directory:
```
cd grades-calculator
```

## Running the Application
Clone the repository to your local machine. Then, navigate to the root of the project in the terminal and run:

```
docker-compose up
```


This will build the Docker images and start the containers. Once the containers are running, you can access the frontend in your web browser at http://localhost:8502.

# How to use
This Grades Calculator App has four main sections, which can be accessed via the menu in the sidebar:

### Create
This section allows you to create a new course.
- You can enter the course name
- You can slide your course grade
- You can select the course Year
- You can select the course semester
  
Once you have filled in the fields, click on the Add button to add the course to the DB.

### View/ Update/ Delete
This section displays a table of all the courses you have created.
- You can choose one course from all of the courses by choosing in the selectbox.
- You can see the data of this course, by clicking on the buttons, you can:
  * Update the data
  * Delete the course
    
### Calculate Average
This section allows you to calculate the weighted averages to the DB that you have entered.
Select the method option that you want to calculate from the dropdown menu:
- All courses
- By semester & year
- According to selected courses

All of these options contain the needed summary, visualizations, and tables.

### Grades simulator 
This section allows you to simulate the averages by changing a course grade.
You can see the influence on the total average, year average, and the semester average.

# Built With
- Docker Compose - A tool for defining and running multi-container Docker applications.
- FastAPI - A modern, fast (high-performance) web framework for building APIs with Python 3.7+ based on standard Python type hints.
- Streamlit - An open-source app framework for Machine Learning and Data Science teams.
- Redis - An open-source, in-memory data structure store, used as a database, cache, and message broker.
