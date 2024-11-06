# Facial Recognition-based Classroom Attendance Tracking System

This project is a classroom attendance tracking system that uses facial recognition to automatically mark attendance. The system stores attendance data in a series of databases and provides functionality to manage records via Python.

## Features
- **Facial Recognition**: Automatically recognizes faces and records attendance.
- **Database Management**: Stores attendance data in a series of `.db` files.
- **Modular Code**: Includes separate modules for application logic (`app.py`) and database management (`database.py`).

## Project Structure
- `app.py`: Main script to run the facial recognition and attendance tracking system.
- `database.py`: Contains functions and classes for handling database operations.
- `*.db`: Database files where attendance records are stored for different classes or sessions.

## Prerequisites
- Python 3.x
- Required libraries: Install them using:
  ```bash
  pip install -r requirements.txt
