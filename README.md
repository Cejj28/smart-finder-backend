# Smart Finder Backend

This is the backend for the Smart Finder system (web and mobile UI) developed for Laboratory Activity No. 8. It provides a RESTful API using Django REST Framework (DRF) to support the frontend application features, including authentication, reporting, and item tracking.

## Features
- **Authentication**: Token-based user authentication.
- **REST APIs**: Endpoints to submit and retrieve Lost and Found Item reports.
- **Image Upload Support**: Backend handles image uploads necessary for item reporting.

## Setup
```bash
python -m venv venv
source venv/bin/activate  # On Windows: .\venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```
