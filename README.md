# Task Manager API

A **multi-user task and project management service** inspired by tools like Todoist. Built with **FastAPI**, **PostgreSQL**, **SQLAlchemy**, and **JWT-based authentication**.

---

## Features

### Authentication
- User registration and login
- Secure authentication using JWT access tokens

### Project Management
- Create, view, update, and delete personal projects
- Each project includes:
  - Name and description
  - Ownership relation to the user
  - A list of associated tasks

### Task Management
- Full CRUD operations for tasks
- Tasks belong to projects and users
- Each task supports:
  - Title & description
  - Completion status
  - Priority (Low, Medium, High)
  - Deadlines

### Utilities
- Filtering and sorting for tasks & projects
- WebSocket-based real-time task/project updates for connected users

---

## Tech Stack

- **FastAPI** for API layer
- **PostgreSQL** as database
- **SQLAlchemy 2.0** ORM
- **Alembic** for migrations
- **Docker + Docker Compose** for deployment
- **Gunicorn with Uvicorn workers** for production server
- **Pytest** for testing
- **WebSocket support** for real-time updates

---

## Deployment (Docker)

### Prerequisites
- Docker & Docker Compose

### Steps

1. Create your `.env` file:
    ```bash
    cp .env.example .env
    ```

2. Build and start the containers:

   ```bash
   docker compose up -d --build
   ```

The API will be available at `http://localhost:8000`.

### API Docs

* Swagger UI: `http://localhost:8000/docs`
* ReDoc: `http://localhost:8000/redoc`

---

## Testing

Run tests with:

```bash
pytest
```

Tests are organized under:

```
tests/
├── unit/
├── integration/
```

---

## Project Structure

```
├── app
│   ├── api                # Routers, endpoints, dependencies, schemas
│   ├── core               # Config, logging, middleware, security
│   ├── db                 # DB connection & models
│   ├── services           # Business logic
│   ├── repositories       # DB queries and persistence
│   └── utils              # Helpers (unit of work, etc.)
├── alembic                # DB migrations
├── tests                  # Unit and integration tests
├── docker-compose.yml     # Container orchestration
├── Dockerfile             # App Dockerfile
└── entrypoint.sh          # Startup script
```

---

## TODO

* [ ] Fix priority levels to behave numerically (not alphabetically)
* [ ] Add team collaboration (many-to-many between users and projects)
* [ ] Enable sharing of tasks/projects with permission levels
* [ ] Assign projects to specific users or user groups
* [ ] WebSocket-based real-time updates with state stored in Redis (pub/sub)
* [ ] Notifications & reminders
* [ ] Labels/tags support
* [ ] File attachments for tasks
* [ ] Subscription and billing support
