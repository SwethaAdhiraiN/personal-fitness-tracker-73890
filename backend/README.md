# Backend (Django API Server)

This is the main API server for the Personal Fitness Tracker. It provides endpoints for user authentication, workout plans, daily schedules, body fat estimation, and progress analytics.

## Overview

- **Framework:** Django + Django REST Framework + CORS headers + drf-yasg (OpenAPI docs)
- **DB:** SQLite (path configured via environment variable)
- **Features:**
  - User registration/login/logout using session/cookie auth
  - CRUD for users, workout plans, daily workouts
  - Progress tracking APIs (progressive overload)
  - Body fat estimation endpoint
  - API documentation at `/docs/` and `/redoc/`

## Required Environment Variables

All are typically set via a `.env` file or directly in your container/host OS. Minimal setup needed:

| Variable    | Required | Purpose                                | Example/Notes                  |
|-------------|----------|----------------------------------------|--------------------------------|
| `SQLITE_DB` | Yes      | Path to SQLite database file            | `/path/to/myapp.db`            |
| `DJANGO_SECRET_KEY` | Optional (for prod) | Django secret key (default defined in code) |                              |

- The SQLite DB path must point to a file initialized via the workout_database container.

## Bootstrapping & Setup

Run all commands from this directory (`backend`).

### 1. Install Python Dependencies

```sh
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 2. Configure Environment

Set path to the SQLite DB file to match the initialized DB from workout_database, e.g.:

```sh
export SQLITE_DB="/path/to/myapp.db"
# [Or add this line to a .env file used by your process manager]
```

### 3. Run Database Migrations

```sh
python manage.py makemigrations
python manage.py migrate
```

### 4. Create Superuser (Optional, to use Django admin)

```sh
python manage.py createsuperuser
```

### 5. Start the Development Server

```sh
python manage.py runserver 0.0.0.0:8000
```
Server will listen on port **8000** by default.

## Known Ports

- Django API: **8000**
- Docs: `/docs/` for Swagger UI, `/redoc/` for ReDoc UI

## API Endpoints (Summary)

All endpoints are prefixed with `/api/`. (Full OpenAPI docs available at `/docs/` in running server.)

- `POST   /api/register/` — Register new user
- `POST   /api/login/` — User login
- `POST   /api/logout/` — User logout
- `GET    /api/me/` — Current user info
- `GET    /api/my-weekly-workout/` — Authenticated user's active workout plans
- `GET    /api/daily-checklist/?date=YYYY-MM-DD` — Daily schedule
- `POST   /api/daily-checklist/` — Mark checklist
- `POST   /api/estimate-body-fat/` — Body fat estimation
- `GET    /api/progress-chart/` — Progress aggregation
- RESTful endpoints for:
  - `/api/workout-plans/`
  - `/api/daily-workouts/`
  - `/api/body-compositions/`
  - `/api/progress/`
- Health: `GET /api/health/`

## Cross-Container Integration

- **Database:** Must have access to a _shared_ SQLite file (see `SQLITE_DB`).  
  - The file should be bootstrapped by running the `init_db.py` script in the workout_database container.
  - For local dev, use an absolute path to the file or a shared/mounted volume.

- **Frontend:** Will make requests to this backend at port **8000** (ensure CORS is configured, which is the default).

- **.env Usage:** Either create a `.env` file and use [`django-environ`](https://github.com/joke2k/django-environ) or just export `SQLITE_DB` before starting the server.

Example `.env`:
```
SQLITE_DB=/abs/path/to/personal-fitness-tracker-73888/workout_database/myapp.db
```

## Development & Testing Notes

- Test the API using Curl, Postman, or by running the frontend.
- API authentication uses session/cookie-based auth out of the box.
- All schema/model changes require `python manage.py makemigrations && python manage.py migrate`.
- Manage users and data via Django admin (at `/admin/`) after creating a superuser.

## Troubleshooting

- If database access fails, ensure `SQLITE_DB` points to the correct file and is readable/writable by the server.
- CORS/CSRF issues: check allowed origins in `backend/config/settings.py`.
- For schema introspection, see [docs endpoints](http://localhost:8000/docs/).

## Contact & Help

For advanced configuration or extension, see the code in `api/`, especially:
- `models.py`, `views.py`, `serializers.py`, `urls.py` for API details.
