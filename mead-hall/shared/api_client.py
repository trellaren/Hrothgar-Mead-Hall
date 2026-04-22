# API client for communicating with the Flask backend

import requests
import json

class APIClient:
    def __init__(self, base_url="http://localhost:5000"):
        self.base_url = base_url
    
    def get_systems(self):
        response = requests.get(f"{self.base_url}/api/systems")
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f"Failed to get systems: {response.status_code}")
    
    def get_system(self, system_id):
        response = requests.get(f"{self.base_url}/api/systems/{system_id}")
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f"Failed to get system: {response.status_code}")
    
    def create_system(self, system_data):
        response = requests.post(f"{self.base_url}/api/systems", json=system_data)
        if response.status_code == 201:
            return response.json()
        else:
            raise Exception(f"Failed to create system: {response.status_code}")
    
    def update_system(self, system_id, system_data):
        response = requests.put(f"{self.base_url}/api/systems/{system_id}", json=system_data)
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f"Failed to update system: {response.status_code}")
    
    def delete_system(self, system_id):
        response = requests.delete(f"{self.base_url}/api/systems/{system_id}")
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f"Failed to delete system: {response.status_code}")

# Example usage
if __name__ == "__main__":
    client = APIClient()
    
    # Create a new system
    new_system = {
        "name": "Test System",
        "status": "active"
    }
    
    try:
        created_system = client.create_system(new_system)
        print("Created system:", created_system)
        
        # Get all systems
        systems = client.get_systems()
        print("All systems:", systems)
        
    except Exception as e:
        print("Error:", e)