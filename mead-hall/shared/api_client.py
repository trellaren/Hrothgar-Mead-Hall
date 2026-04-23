# API client for communicating with the Flask backend
import json

import requests


class APIClient:
    def __init__(self, base_url="http://localhost:5000"):
        self.base_url = base_url
        self._token = None
        self._username = None

    @property
    def token(self):
        return self._token

    @property
    def username(self):
        return self._username

    def set_auth_token(self, token):
        """Set the authentication token."""
        self._token = token

    def clear_auth(self):
        """Clear authentication."""
        self._token = None
        self._username = None

    def _get_headers(self, include_auth=True):
        """Get request headers with optional auth."""
        headers = {'Content-Type': 'application/json'}
        if include_auth and self._token:
            headers['Authorization'] = f'Bearer {self._token}'
        return headers

    def _handle_response(self, response):
        """Handle API response, raising on errors."""
        if response.status_code in (200, 201):
            return response.json()
        # Handle auth errors specially
        if response.status_code == 401:
            raise AuthenticationError(f'Authentication failed: {response.json().get("error", "Unknown error")}')
        raise Exception(f"API error: {response.status_code} - {response.json().get('error', 'Unknown error')}")

    # ==================== Authentication ====================

    def login(self, username, password):
        """Authenticate and store token."""
        response = requests.post(
            f"{self.base_url}/api/auth/login",
            json={'username': username, 'password': password},
        )
        data = self._handle_response(response)
        self._token = data['token']
        self._username = data['user']['username']
        return data

    def register(self, username, password):
        """Register a new user."""
        response = requests.post(
            f"{self.base_url}/api/auth/register",
            json={'username': username, 'password': password},
        )
        return self._handle_response(response)

    def logout(self):
        """Logout and clear auth."""
        if self._token:
            try:
                response = requests.post(
                    f"{self.base_url}/api/auth/logout",
                    headers=self._get_headers(include_auth=True),
                )
                return response.json()
            except Exception:
                pass
        self.clear_auth()
        return {}

    def get_current_user(self):
        """Get current authenticated user."""
        response = requests.get(
            f"{self.base_url}/api/auth/me",
            headers=self._get_headers(include_auth=True),
        )
        return self._handle_response(response)

    # ==================== Systems CRUD ====================

    def get_systems(self):
        response = requests.get(f"{self.base_url}/api/systems", headers=self._get_headers())
        return self._handle_response(response)

    def get_system(self, system_id):
        response = requests.get(f"{self.base_url}/api/systems/{system_id}", headers=self._get_headers())
        return self._handle_response(response)

    def create_system(self, system_data):
        response = requests.post(
            f"{self.base_url}/api/systems",
            json=system_data,
            headers=self._get_headers(),
        )
        return self._handle_response(response)

    def update_system(self, system_id, system_data):
        response = requests.put(
            f"{self.base_url}/api/systems/{system_id}",
            json=system_data,
            headers=self._get_headers(),
        )
        return self._handle_response(response)

    def delete_system(self, system_id):
        response = requests.delete(
            f"{self.base_url}/api/systems/{system_id}",
            headers=self._get_headers(),
        )
        return self._handle_response(response)

    # ==================== Health ====================

    def health_check(self):
        response = requests.get(f"{self.base_url}/api/health")
        if response.status_code == 200:
            return response.json()
        raise Exception(f"Health check failed: {response.status_code}")


class AuthenticationError(Exception):
    """Raised when authentication fails."""
    pass


# Example usage
if __name__ == "__main__":
    client = APIClient()

    # Login first
    try:
        client.login('admin', 'admin123')
        print(f"Logged in as: {client.username}")

        # Create a new system
        new_system = {
            "name": "Test System",
            "status": "active",
        }

        created_system = client.create_system(new_system)
        print("Created system:", created_system)

        # Get all systems
        systems = client.get_systems()
        print("All systems:", systems)

    except AuthenticationError as e:
        print("Authentication error:", e)
    except Exception as e:
        print("Error:", e)