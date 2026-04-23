# Mead Hall - Shared Module

Shared code between the web backend and desktop GUI.

## Modules

### `api_client.py`

API client for communicating with the Flask backend.

```python
from api_client import APIClient, AuthenticationError

client = APIClient("http://localhost:5000")

# Login
client.login("admin", "admin123")

# CRUD operations
systems = client.get_systems()
system = client.get_system(1)
created = client.create_system({"name": "My System", "status": "active"})
updated = client.update_system(1, {"name": "Updated System"})
client.delete_system(1)

# Logout
client.logout()
```

### `models/system.py`

Data model for clustering systems with validation.

```python
from models.system import ClusteringSystem, VALID_STATUSES

# Create with validation
system = ClusteringSystem.create(name="My System", status="active")

# Convert to/from dict
data = system.to_dict()
system = ClusteringSystem.from_dict(data)

# Validate updates
errors = system.validate_update({"name": "New Name"})
```

## Project Structure

```
shared/
├── api_client.py      # API client for backend communication
├── README.md          # This file
└── models/
    ├── system.py      # ClusteringSystem model with validation
    └── __init__.py
```
