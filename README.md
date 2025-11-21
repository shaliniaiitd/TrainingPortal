✅ README: TrainingPortal API Documentation (Django REST Framework)
📌 Overview

This API provides CRUD operations for the Members, Courses, Students, and Users models of the TrainingPortal LMS application.

The backend is powered by Django + Django REST Framework, and includes:

ModelViewSets for full CRUD

Browsable API

Nested serialization for Courses → Members

Automatic API documentation (Swagger & Redoc)

🚀 1. Setup Instructions
Install dependencies
pip install django djangorestframework drf-yasg drf-spectacular

Run migrations
python manage.py migrate

Start the server
python manage.py runserver


API base URL:

http://127.0.0.1:8000/myapp/api/

📘 2. API Documentation (Swagger / ReDoc)
Swagger UI
http://127.0.0.1:8000/myapp/api/docs/swagger/

ReDoc
http://127.0.0.1:8000/myapp/api/docs/redoc/

📚 3. Available Endpoints
Base router:
/myapp/api/

Generated endpoints:
👤 Members API
Method	Endpoint	Description
GET	/members/	List all members
POST	/members/	Create a member
GET	/members/{id}/	Retrieve a member
PUT	/members/{id}/	Update a member
PATCH	/members/{id}/	Partial update
DELETE	/members/{id}/	Delete
Sample POST request
{
  "firstname": "John",
  "lastname": "Doe",
  "designation": "Trainer",
  "image": null
}

📘 Courses API

Courses include a nested facultyname object + a writable facultyname_id.

Method	Endpoint	Description
GET	/courses/	List all courses
POST	/courses/	Create a course
GET	/courses/{id}/	Retrieve
PUT	/courses/{id}/	Update
DELETE	/courses/{id}/	Delete
POST format
{
  "coursename": "Python Basics",
  "facultyname_id": 1,
  "startdate": "2025-01-01T10:00",
  "enddate": "2025-02-01T10:00",
  "category": "P"
}

GET response example
{
  "id": 5,
  "coursename": "Python Basics",
  "facultyname": {
    "id": 1,
    "firstname": "John",
    "lastname": "Doe",
    "designation": "Trainer",
    "image": "/media/images/john.jpg"
  },
  "startdate": "2025-01-01T10:00:00Z",
  "enddate": "2025-02-01T10:00:00Z",
  "category": "P"
}

🎓 Students API
Method	Endpoint
GET	/students/
POST	/students/
GET	/students/{id}/
PUT	/students/{id}/
DELETE	/students/{id}/
Example POST
{
  "firstname": "Alice",
  "lastname": "Smith",
  "doj": "2025-01-01T09:00:00Z",
  "resume": "",
  "course": 5,
  "skills": "Python, HTML",
  "email": "alice@example.com"
}

🧑‍💼 Users API

(Not Django Auth — this is your custom User model.)

Method	Endpoint
GET	/users/
POST	/users/
GET	/users/{id}/
PUT	/users/{id}/
DELETE	/users/{id}/
🔐 4. Authentication

Currently no authentication is enabled (all endpoints open).

(Optional) To enable:

REST_FRAMEWORK = {
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.IsAuthenticated"
    ]
}

🧪 5. Testing the API
Using DRF Browsable API

Visit any endpoint, e.g.:

http://127.0.0.1:8000/myapp/api/members/

Using Playwright (Browser Context Fetch API)

Example:

resp = page.request.post("/myapp/api/members/", data={
    "firstname": "John",
    "lastname": "Doe",
    "designation": "Developer"
})
assert resp.ok()

📦 6. Project Structure (API)
myapp/
├── api_views.py
├── serializers.py
├── models.py
├── urls.py     # includes router
└── views.py    # UI views