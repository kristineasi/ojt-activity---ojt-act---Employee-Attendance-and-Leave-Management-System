# Employee Attendance and Leave Management System

A full-stack Django + Django REST Framework web app for:
- Employee time-in and time-out tracking
- Monthly worked-hours summary
- Leave request filing
- Manager approval/rejection workflow in real time via dashboard refresh

## Tech Stack
- Django 5
- Django REST Framework
- Session + Token authentication
- SQLite (local) / PostgreSQL (production)
- WhiteNoise static file serving
- Gunicorn for production app server

## Local Run
1. Create and activate a virtual environment.
2. Install dependencies:
   - `pip install -r requirements.txt`
3. Run migrations:
   - `python manage.py migrate`
4. Seed demo data (one command):
   - `python manage.py seed_demo_data`
   - Manager login: `manager_demo` / `DemoPass123!`
   - Employee login: `employee_demo` / `DemoPass123!`
5. (Optional) Create admin user:
   - `python manage.py createsuperuser`
6. Start server:
   - `python manage.py runserver`
7. Open:
   - `http://127.0.0.1:8000/`

## Verified Routes
- Web
  - `GET /` login page
  - `GET /dashboard/` dashboard page (auth required)
  - `POST /logout/` logout
  - `GET /admin/` Django admin
- Accounts API
  - `POST /api/accounts/register/`
  - `POST /api/accounts/login/`
  - `POST /api/accounts/logout/`
  - `GET /api/accounts/me/`
- Attendance API
  - `POST /api/attendance/time-in/`
  - `POST /api/attendance/time-out/`
  - `GET /api/attendance/my-records/`
  - `GET /api/attendance/summary/?month=3&year=2026`
- Leave API
  - `GET /api/leaves/requests/`
  - `POST /api/leaves/requests/`
  - `PATCH /api/leaves/requests/<id>/approve/` (manager only)
  - `PATCH /api/leaves/requests/<id>/reject/` (manager only)

## Deploy Online (Render)
This repository is preconfigured for Render with:
- `render.yaml`
- `build.sh`
- `Procfile`

### Steps
1. Push this project to GitHub.
2. In Render, choose **New + > Blueprint** and select your repo.
3. Render reads `render.yaml` and creates:
   - One web service
   - One PostgreSQL database
4. After first deploy, open a Render shell and run:
   - `python manage.py migrate`
   - `python manage.py seed_demo_data`
   - `python manage.py createsuperuser` (optional)
5. Use demo credentials above to access the app immediately.

## Required Environment Variables
Use `.env.example` as reference:
- `DJANGO_SECRET_KEY`
- `DJANGO_DEBUG`
- `DJANGO_ALLOWED_HOSTS`
- `DJANGO_CSRF_TRUSTED_ORIGINS`
- `DATABASE_URL`

## Notes
- Dashboard uses session auth from web login.
- Token auth is available for API clients.
- Attendance summary validates month/year input to avoid server errors.
