# Mead Hall - Web Backend

Flask-based REST API for managing clustering systems.

## Features

- **RESTful API** for CRUD operations on clustering systems
- **Authentication** via token-based auth (Bearer tokens)
- **Model enforcement** with data validation on all system endpoints
- **SQLite database** via SQLAlchemy for persistent storage
- **Password hashing** via Flask-Bcrypt

## Installation

```bash
pip install flask flask-cors flask-sqlalchemy flask-login flask-bcrypt
```

## Database

The application uses SQLite with SQLAlchemy ORM. The database is automatically initialized on startup.

- Database file: `mead_hall.db` (created in the web directory)
- Tables: `systems`, `users` (in-memory for now)

## API Endpoints

### Authentication

| Method | Endpoint             | Description                           |
| ------ | -------------------- | ------------------------------------- |
| POST   | `/api/auth/login`    | Login with username/password          |
| POST   | `/api/auth/register` | Register a new user                   |
| POST   | `/api/auth/logout`   | Logout current user (requires auth)   |
| GET    | `/api/auth/me`       | Get current user info (requires auth) |

### Systems

| Method | Endpoint            | Description                           |
| ------ | ------------------- | ------------------------------------- |
| GET    | `/api/systems`      | Get all systems (requires auth)       |
| GET    | `/api/systems/<id>` | Get a specific system (requires auth) |
| POST   | `/api/systems`      | Create a new system (requires auth)   |
| PUT    | `/api/systems/<id>` | Update a system (requires auth)       |
| DELETE | `/api/systems/<id>` | Delete a system (requires auth)       |

### Health

| Method | Endpoint      | Description                     |
| ------ | ------------- | ------------------------------- |
| GET    | `/api/health` | Health check (no auth required) |

## Authentication

All system endpoints require authentication via Bearer token in the Authorization header:

```
Authorization: Bearer <token>
```

### Default Credentials

- **Admin**: username=`admin`, password=`admin123`
- **User**: username=`user`, password=`user123`

## Data Validation

System creation/update endpoints validate:

- `name`: Required on creation, must be string, max 255 characters
- `status`: Must be one of `active`, `inactive`, `maintenance`, `error`
- `nodes`: Must be an array of strings or objects with `id`/`address` fields

## Running

```bash
python app.py
```

The server starts on `http://localhost:5000`.

## Testing

```bash
python -m unittest tests.test_model_enforcement -v
```
