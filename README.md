# Users API

A production-ready user management API built with FastAPI. Covers registration, JWT authentication, email verification, role-based access control, and automated cleanup of unverified accounts.

---

## Tech Stack

- **FastAPI** — async web framework
- **SQLAlchemy** — async ORM
- **PostgreSQL** — primary database
- **Alembic** — database migrations
- **JWT** — access and refresh tokens via `python-jose`
- **Celery + Redis** — background task queue and scheduler
- **aiosmtplib** — async SMTP email sending
- **Docker + Docker Compose** — containerization

---

## Project Architecture

The project follows a **modular monolith** pattern with clear separation of concerns:
```
app/
├── core/           # Config, database, security, email
├── models/         # SQLAlchemy ORM models
├── schemas/        # Pydantic request/response schemas
├── repositories/   # Database access layer (one per model)
├── services/       # Business logic layer
├── api/            # HTTP route handlers (thin layer)
├── tasks/          # Celery background tasks
├── scripts/        # CLI utilities (e.g. create admin)
└── alembic/        # Database migrations
```

Each request goes through:
```
Router → Service → Repository → Database
- **Repositories** handle all SQL queries — no business logic
- **Services** contain all business logic — no HTTP concerns
- **Routers** are thin: validate input, call service, return response
```

---

## Features

- `POST /auth/signup` — register a new user; sends a 6-digit verification code to their email
- `POST /auth/login` — authenticate and receive JWT access + refresh token pair
- `POST /auth/refresh` — exchange a refresh token for a new access token
- `POST /auth/verify` — confirm email with the verification code
- `GET /me` — get the currently authenticated user's profile
- `GET /users` — list all users *(admin only)*
- `GET /users/{id}` — get a user by ID *(admin only)*
- `PATCH /users/{id}` — partially update a user's name; users can only update their own profile, admins can update anyone
- `DELETE /users/{id}` — delete a user *(admin only)*
- `GET /health` — liveness probe

### Security
- Passwords hashed with **bcrypt**
- JWT tokens with separate access (15 min) and refresh (7 days) lifetimes
- Token type validation (access token cannot be used as refresh and vice versa)
- Role-based access control (`user` / `admin`)
- Rate limiting on all auth endpoints (5–20 requests/minute per IP)
- CORS configured per environment

### Automated Cleanup
Unverified users older than 2 days are automatically deleted by a **Celery Beat** scheduled task that runs every hour.

---

## Running with Docker (recommended)

### Prerequisites
- Docker and Docker Compose installed

### 1. Clone the repository

```bash
git clone https://github.com/Miraziz77/Users-API.git
cd Users-API
```

### 2. Configure environment variables

```bash
cp .env.example .env
```

Open `.env` and fill in your values — at minimum set your SMTP credentials and a strong `JWT_SECRET_KEY`.

### 3. Start all services

```bash
docker compose up --build
```

This will automatically:
- Start PostgreSQL and Redis
- Run Alembic migrations
- Start the FastAPI server on port 8000
- Start Celery worker and Celery Beat scheduler

### 4. Create the first admin user

In a separate terminal, while containers are running:

```bash
docker exec -it usersapi-api-1 python -m app.scripts.create_admin admin@example.com StrongPass123
```

If the email already exists as a regular user, the script will promote them to admin.

### 5. Open the API docs
http://localhost:8000/docs

### Stopping

```bash
docker compose down        # stop containers, keep database data
docker compose down -v     # stop containers and delete all data
```

---

## Running Locally (without Docker)

### Prerequisites
- Python 3.12+
- PostgreSQL running locally
- Redis running locally (or via Docker: `docker run -d -p 6379:6379 redis:7-alpine`)

### 1. Clone and set up the environment

```bash
git clone https://github.com/Miraziz77/Users-API.git
cd Users-API
python -m venv .venv
.venv\Scripts\activate  # Windows
# source .venv/bin/activate  # macOS/Linux
pip install -r requirements.txt
```

### 2. Configure environment variables

```bash
cp .env.example .env
# Edit .env with your local database and SMTP credentials
```

### 3. Apply migrations

```bash
alembic upgrade head
```

### 4. Start the application (3 terminals)

**Terminal 1 — API server:**
```bash
uvicorn app.main:app --reload
```

**Terminal 2 — Celery worker:**
```bash
celery -A app.core.celery_app:celery_app worker --loglevel=info --pool=solo
```

**Terminal 3 — Celery Beat scheduler:**
```bash
celery -A app.core.celery_app:celery_app beat --loglevel=info
```

### 5. Create the first admin user

```bash
python -m app.scripts.create_admin admin@example.com StrongPass123
```

---

## Environment Variables

| Variable | Description | Example |
|---|---|---|
| `PROJECT_NAME` | API title shown in Swagger | `Users API` |
| `ENVIRONMENT` | `dev` or `prod` | `dev` |
| `DB_USER` | PostgreSQL username | `users_api` |
| `DB_PASS` | PostgreSQL password | `users_api` |
| `DB_HOST` | PostgreSQL host | `localhost` |
| `DB_PORT` | PostgreSQL port | `5432` |
| `DB_NAME` | PostgreSQL database name | `users` |
| `JWT_SECRET_KEY` | Secret key for signing JWT tokens | `your-secret-key` |
| `JWT_ALGORITHM` | JWT signing algorithm | `HS256` |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Access token lifetime in minutes | `15` |
| `REFRESH_TOKEN_EXPIRE_DAYS` | Refresh token lifetime in days | `7` |
| `VERIFICATION_CODE_EXPIRE_HOURS` | Verification code lifetime in hours | `24` |
| `UNVERIFIED_USER_TTL_DAYS` | Days before unverified users are deleted | `2` |
| `CELERY_BROKER_URL` | Redis URL for Celery broker | `redis://localhost:6379/0` |
| `CELERY_RESULT_BACKEND` | Redis URL for Celery results | `redis://localhost:6379/0` |
| `SMTP_HOST` | SMTP server host | `smtp.gmail.com` |
| `SMTP_PORT` | SMTP server port | `587` |
| `SMTP_USER` | SMTP username / sender email | `you@gmail.com` |
| `SMTP_PASSWORD` | SMTP password or app password | `your-app-password` |
| `SMTP_USE_TLS` | Use STARTTLS | `true` |
| `EMAIL_FROM` | From address in sent emails | `you@gmail.com` |
