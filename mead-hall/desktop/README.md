# Mead Hall - Desktop GUI

Tkinter-based desktop application for managing clustering systems.

## Features

- **GUI interface** for system management
- **API client integration** for all state management
- **Authentication** with login/logout support
- **Real-time refresh** of system data from the server

## Dependencies

```bash
pip install requests
```

## Running

```bash
python main.py
```

## Usage

1. The application attempts to auto-login on startup
2. If authentication fails, a login dialog appears
3. Default credentials:
   - **Admin**: username=`admin`, password=`admin123`
   - **User**: username=`user`, password=`user123`
4. Once logged in, you can:
   - **Add System** - create a new clustering system
   - **Update System** - modify the selected system
   - **Delete System** - remove the selected system
   - **Logout** - clear the current session

## Architecture

The desktop app uses the `APIClient` from the `shared` module for all API communication:

- State is managed server-side via the Flask backend
- The GUI is a thin presentation layer over the API
- Authentication tokens are stored in the API client instance

## Project Structure

```
desktop/
├── main.py          # Main Tkinter application
└── README.md        # This file
```
