# Mergington High School Activities

A modern web application for managing extracurricular activities at Mergington High School. This FastAPI-based application provides a comprehensive system for students to browse activities and for teachers to manage registrations.

## Features

### Student Features
- **Browse Activities**: View all available extracurricular activities with detailed information
- **Search & Filter**: Find activities by name, category, day of the week, or time range
- **Activity Details**: See schedules, descriptions, participant limits, and current enrollment
- **Responsive Design**: Clean, modern interface that works on all devices

### Teacher Features  
- **Secure Authentication**: Login system for teachers to manage student registrations
- **Student Registration**: Sign up students for activities with authentication
- **Student Unregistration**: Remove students from activities when needed
- **Session Management**: Secure session handling for teacher accounts

### System Features
- **MongoDB Integration**: Persistent data storage for activities, participants, and teacher accounts
- **RESTful API**: Well-documented API endpoints with automatic OpenAPI documentation
- **Real-time Updates**: Activity participant counts update dynamically
- **Data Validation**: Comprehensive input validation and error handling

## Technical Architecture

- **Backend**: FastAPI web framework with Python
- **Database**: MongoDB for data persistence
- **Frontend**: HTML, CSS, and vanilla JavaScript
- **Authentication**: Secure password hashing with SHA-256
- **API Documentation**: Auto-generated OpenAPI/Swagger documentation

## API Endpoints

### Activities
- `GET /activities/` - Get all activities with optional filtering by day, start_time, end_time
- `GET /activities/days` - Get list of all days that have activities scheduled
- `POST /activities/{activity_name}/signup` - Sign up a student for an activity (requires teacher authentication)
- `POST /activities/{activity_name}/unregister` - Remove a student from an activity (requires teacher authentication)

### Authentication
- `POST /auth/login` - Teacher login with username and password
- `GET /auth/check-session` - Verify teacher session status

## Development Guide

For detailed setup and development instructions, please refer to our [Development Guide](../docs/how-to-develop.md).

### Quick Start

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Ensure MongoDB is running locally on port 27017

3. Run the application:
   ```bash
   uvicorn app:app --reload
   ```

4. Access the application:
   - Website: http://localhost:8000
   - API Documentation: http://localhost:8000/docs
   - Alternative API Docs: http://localhost:8000/redoc

## Sample Activities

The system comes pre-loaded with sample activities including:
- Chess Club (Mondays & Fridays, 3:15-4:45 PM)
- Programming Class (Tuesdays & Thursdays, 7:00-8:00 AM)
- Morning Fitness (Monday/Wednesday/Friday, 6:30-7:45 AM)
- Soccer Team (Tuesdays & Thursdays, 3:30-5:30 PM)
- Basketball Team (Wednesdays & Fridays, 3:15-5:00 PM)
- Drama Club (Mondays & Wednesdays, 3:30-5:30 PM)
- Art Club (Thursdays, 3:15-5:00 PM)
- Math Club (Tuesdays, 7:15-8:00 AM)
- Debate Team (Fridays, 3:30-5:30 PM)
- Weekend Robotics Workshop (Saturdays, 10:00 AM-2:00 PM)
- Science Olympiad (Various schedules)

## Database Schema

The application uses two main collections:
- **activities**: Stores activity information, schedules, and participant lists
- **teachers**: Stores teacher accounts with hashed passwords for authentication
