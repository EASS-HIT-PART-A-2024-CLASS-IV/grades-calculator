# Grades Calculator App

 [![image](https://github.com/EASS-HIT-PART-A-2024-CLASS-IV/grades-calculator/assets/131989545/c214de5f-f324-4313-99dd-a0301a6e06e4)
](https://github.com/EASS-HIT-PART-A-2024-CLASS-IV/grades-calculator/blob/main/frontend/LOGO-CALCULATOR2.png)


This project is a Grades Calculator application built with:

- Docker Compose
- FastAPI
- Streamlit 

The application allows users to:

- Create a course
- View a course:  * Update a course data
                  * Delete a course
- Calculate the average by: * Total courses
                            * Selected courses
                            * Semestr-year wide
- Grades simulator

  
as well as view all tasks in a list. The backend is built with FastAPI and connected to Redis for data storage. The frontend is built with Streamlit and communicates with the backend to retrieve and manipulate data.

# Prerequisites
You will need to have Docker and Docker Compose installed on your machine in order to run the application.

# Getting Started
These instructions will get you a copy of the project up and running on your local machine for development and testing purposes

In console make new direction:
```
mkdir grades-calculator
```

Change direction: 
```
cd grades-calculator
```

Clone the repository, write in console: 
```
git clone [[https://github.com/EASS-HIT-PART-A-2022-CLASS-II/Elad_Mor_Project.git](https://github.com/EASS-HIT-PART-A-2024-CLASS-IV/grades-calculator.git)](https://github.com/EASS-HIT-PART-A-2024-CLASS-IV/grades-calculator.git)
```

## Running the Application
Clone the repository to your local machine. Then, navigate to the root of the project in the terminal and run:

```docker-compose up```

This will build the Docker images and start the containers. Once the containers are running, you can access the frontend in your web browser at
http://localhost:8502.

# How to use
Use the App
This Grades Calculator App have four main sections, which can be accessed via the menu in the sidebar:

### Create
This section allows you to create a new course.
  * You can enter the course name
  * You can slide your course grade
  * You can select the course Year
  * You can select the course semester
Once you have filled in the fields, click on the Add button to add the course to the DB.

### View/ Update/ Delete
This section displays a table of all the coursed you have created.
You can choose one course from all of the courses by choosing in the selectbox.
You can see the data of this course and also have the options to update the data or delete the course by clicking on the buttons.

### Calculate Average
This section allows you to calculate the weighted averages to the DB that you have entered.
Select the methode option that you want to calculate from the dropdown menu:
  * All courses
  * By semester & year
  * According to selected courses
All of these options contains the needed summery, visualizations and tables.

### Grades simulator 
This section allows you to simulate the averages by changing a course grade.
You can see the influence to the total average, year average and the semester average.

# Built With
- Docker Compose - A tool for defining and running multi-container Docker applications.
- FastAPI - A modern, fast (high-performance) web framework for building APIs with Python 3.7+ based on standard Python type hints.
- Streamlit - An open-source app framework for Machine Learning and Data Science teams.
- Redis - An open source, in-memory data structure store, used as a database, cache, and message broker.
