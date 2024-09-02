# Ward Profiles Web Application

Welcome to the Ward Profiles Web Application! This project is designed to provide an interactive platform for visualizing ward-level data, including demographics, employment statistics, and more. The application is built using Flask, with various APIs and Python packages to enhance its functionality.

## Table of Contents
- [Features](#features)
- [Installation](#installation)
- [Running the Application](#running-the-application)
- [Usage](#usage)
- [Contributing](#contributing)
- [License](#license)

## Features
- Interactive maps using Folium
- Data visualization with Plotly
- Integration with NOMIS API for real-time data
- Flask-based backend with SQLAlchemy for database management
- Accessible and responsive front-end design

## Installation

### Prerequisites
Before you begin, ensure you have Python 3.8+ installed on your system.

### Setting Up the Flask Environment

1. **Clone the Repository**
   ```bash
   git clone https://github.com/yourusername/wardprofiles.git
   cd wardprofiles

2. **Create a Virtual Environment Set up a virtual environment to manage your project dependencies**
   ```bash
   python3 -m venv venv

3. **Activate the Virtual Environment (on windows)**
   ```bash
   venv\Scripts\activate

4. **Install the Flask libraries bellow**
   
![image](https://github.com/user-attachments/assets/f74b71db-8eac-4c4b-b6fd-e38d8b6f2508)

6. **Install all the other python packages required**
   ![image](https://github.com/user-attachments/assets/5a8ce81c-e865-4a4c-bfb5-8cc487fceb50)

## Running Flask locally:

1. **Setting up environment variables:**
   ```bash
   FLASK_APP=run.py
   FLASK_ENV=development
   DATABASE_URL=your-database-url

2. **Initialising the database:**
   ```bash
   flask db upgrade

3. **Running the flask application:**
   ```bash
    flask run

### Key Points:
- The `README.md` file provides clear instructions for setting up the environment, installing necessary packages, and running the Flask application.
- It mentions essential Flask extensions and additional Python packages used in the project.
- The file is structured with sections like Features, Installation, and Usage to make it easy to follow.

