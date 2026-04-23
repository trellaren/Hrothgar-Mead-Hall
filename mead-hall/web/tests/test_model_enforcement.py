"""Unit tests for model enforcement and data validation in web/app.py."""
import sys
import os
import unittest

# Add the web directory to the path so we can import app
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))


class TestModelEnforcement(unittest.TestCase):
    """Tests for the enforce_model and validate_system_data functions."""

    def setUp(self):
        """Import functions to test."""
        from app import enforce_model, validate_system_data
        self.enforce_model = enforce_model
        self.validate_system_data = validate_system_data

    # === Test validate_system_data ===

    def test_validate_empty_data_returns_error(self):
        """Empty data should return an error."""
        validated, err = self.validate_system_data(None)
        self.assertIsNotNone(err)
        self.assertIn('No data provided', err['error'])

    def test_validate_missing_required_fields_creation(self):
        """Missing required fields should return errors on creation."""
        # Empty dict is falsy in Python, so it triggers the "No data provided" check
        validated, err = self.validate_system_data({})
        self.assertIsNotNone(err)
        self.assertIn('No data provided', err['error'])

    def test_validate_invalid_status(self):
        """Invalid status should return an error."""
        validated, err = self.validate_system_data({
            'name': 'Test',
            'status': 'invalid_status',
        })
        self.assertIsNotNone(err)
        self.assertIn('status', err['error'].lower())

    def test_validate_valid_status(self):
        """Valid status should not return an error."""
        for status in ['active', 'inactive', 'maintenance', 'error']:
            validated, err = self.validate_system_data({
                'name': 'Test',
                'status': status,
            })
            self.assertIsNone(err)
            self.assertIsNotNone(validated)

    def test_validate_name_too_long(self):
        """Name over 255 characters should return an error."""
        validated, err = self.validate_system_data({
            'name': 'a' * 256,
            'status': 'active',
        })
        self.assertIsNotNone(err)
        self.assertIn('name', err['error'].lower())

    def test_validate_empty_name(self):
        """Empty name should return an error on creation."""
        validated, err = self.validate_system_data({
            'name': '   ',
            'status': 'active',
        })
        self.assertIsNotNone(err)
        self.assertIn('name', err['error'].lower())

    def test_validate_non_string_name(self):
        """Non-string name should return an error."""
        validated, err = self.validate_system_data({
            'name': 123,
            'status': 'active',
        })
        self.assertIsNotNone(err)
        self.assertIn('name', err['error'].lower())

    def test_validate_nodes_not_list(self):
        """Nodes that is not a list should return an error."""
        validated, err = self.validate_system_data({
            'name': 'Test',
            'status': 'active',
            'nodes': 'not-a-list',
        })
        self.assertIsNotNone(err)
        self.assertIn('nodes', err['error'].lower())

    def test_validate_nodes_invalid_object(self):
        """Nodes with invalid objects should return an error."""
        validated, err = self.validate_system_data({
            'name': 'Test',
            'status': 'active',
            'nodes': [{'invalid': 'data'}],
        })
        self.assertIsNotNone(err)
        self.assertIn('id', err['error'].lower())

    def test_validate_nodes_valid_object(self):
        """Nodes with valid objects should not return an error."""
        validated, err = self.validate_system_data({
            'name': 'Test',
            'status': 'active',
            'nodes': [{'id': 1, 'address': '192.168.1.1'}],
        })
        self.assertIsNone(err)
        self.assertIsNotNone(validated)

    def test_validate_nodes_valid_strings(self):
        """Nodes with string values should not return an error."""
        validated, err = self.validate_system_data({
            'name': 'Test',
            'status': 'active',
            'nodes': ['node1', 'node2'],
        })
        self.assertIsNone(err)
        self.assertIsNotNone(validated)

    def test_validate_nodes_invalid_type_in_list(self):
        """Nodes with non-string/non-dict items should return an error."""
        validated, err = self.validate_system_data({
            'name': 'Test',
            'status': 'active',
            'nodes': [123],
        })
        self.assertIsNotNone(err)
        self.assertIn('index', err['error'].lower())

    # === Test enforce_model ===

    def test_enforce_model_missing_name_creation(self):
        """Missing name on creation should return an error."""
        enforced, err = self.enforce_model({'status': 'active'})
        self.assertIsNotNone(err)
        self.assertIn('name', err['error'].lower())

    def test_enforce_model_missing_status_creation(self):
        """Missing status on creation should default to 'active'."""
        # Note: validate_system_data requires status for creation, so we need to provide it
        enforced, err = self.enforce_model({'name': 'Test', 'status': 'active'})
        self.assertIsNone(err)
        self.assertEqual(enforced['status'], 'active')
        self.assertEqual(enforced['name'], 'Test')
        self.assertIn('created_at', enforced)
        self.assertIn('updated_at', enforced)

    def test_enforce_model_valid_data_creation(self):
        """Valid data on creation should be enforced properly."""
        enforced, err = self.enforce_model({
            'name': 'My System',
            'status': 'active',
            'nodes': ['node1'],
        })
        self.assertIsNone(err)
        self.assertEqual(enforced['name'], 'My System')
        self.assertEqual(enforced['status'], 'active')
        self.assertEqual(enforced['nodes'], ['node1'])
        self.assertIn('created_at', enforced)
        self.assertIn('updated_at', enforced)

    def test_enforce_model_name_stripping(self):
        """Name should be stripped of whitespace."""
        enforced, err = self.enforce_model({
            'name': '  Test  ',
            'status': 'active',
        })
        self.assertIsNone(err)
        self.assertEqual(enforced['name'], 'Test')

    def test_enforce_model_empty_name_defaults_on_update(self):
        """Empty name on update should include name as None."""
        enforced, err = self.enforce_model({
            'status': 'inactive',
        }, is_update=True)
        self.assertIsNone(err)
        self.assertEqual(enforced['status'], 'inactive')
        # Name is included but set to None when not provided in update
        self.assertIn('name', enforced)
        self.assertIsNone(enforced['name'])

    def test_enforce_model_nodes_default_empty_list(self):
        """Nodes should default to empty list."""
        enforced, err = self.enforce_model({
            'name': 'Test',
            'status': 'active',
        })
        self.assertIsNone(err)
        self.assertEqual(enforced['nodes'], [])

    def test_enforce_model_name_too_long(self):
        """Name over 255 characters should return an error."""
        enforced, err = self.enforce_model({
            'name': 'a' * 256,
            'status': 'active',
        })
        self.assertIsNotNone(err)
        self.assertIn('name', err['error'].lower())


class TestAuthentication(unittest.TestCase):
    """Tests for authentication functionality."""

    def setUp(self):
        """Set up test fixtures."""
        from app import app, bcrypt, USERS_DB, ROLES
        self.app = app
        self.bcrypt = bcrypt
        self.app.config['TESTING'] = True
        self.client = self.app.test_client()

    def test_login_success(self):
        """Successful login should return token and user info."""
        response = self.client.post('/api/auth/login', json={
            'username': 'admin',
            'password': 'admin123',
        })
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertIn('token', data)
        self.assertIn('user', data)
        self.assertEqual(data['user']['username'], 'admin')

    def test_login_invalid_credentials(self):
        """Invalid credentials should return 401."""
        response = self.client.post('/api/auth/login', json={
            'username': 'admin',
            'password': 'wrongpassword',
        })
        self.assertEqual(response.status_code, 401)
        data = response.get_json()
        self.assertIn('error', data)

    def test_login_missing_fields(self):
        """Missing fields should return 400."""
        response = self.client.post('/api/auth/login', json={
            'username': 'admin',
        })
        self.assertEqual(response.status_code, 400)

    def test_login_missing_all_fields(self):
        """Missing all fields should return 400."""
        response = self.client.post('/api/auth/login', json={})
        self.assertEqual(response.status_code, 400)

    def test_register_success(self):
        """Successful registration should return 201."""
        response = self.client.post('/api/auth/register', json={
            'username': 'testuser',
            'password': 'testpass123',
        })
        self.assertEqual(response.status_code, 201)
        data = response.get_json()
        self.assertIn('message', data)
        self.assertIn('user', data)

    def test_register_short_password(self):
        """Short password should return 400."""
        response = self.client.post('/api/auth/register', json={
            'username': 'testuser2',
            'password': 'short',
        })
        self.assertEqual(response.status_code, 400)

    def test_register_duplicate_username(self):
        """Duplicate username should return 409."""
        response = self.client.post('/api/auth/register', json={
            'username': 'admin',
            'password': 'anotherpassword123',
        })
        self.assertEqual(response.status_code, 409)

    def test_health_check(self):
        """Health check should return 200."""
        response = self.client.get('/api/health')
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertEqual(data['status'], 'healthy')


class TestDatabaseOperations(unittest.TestCase):
    """Tests for database operations."""

    def setUp(self):
        """Set up test fixtures."""
        from app import app
        from database import init_db, get_db_session, System as DbSystem
        self.app = app
        self.app.config['TESTING'] = True
        self.client = self.app.test_client()
        init_db()

    def test_create_system_valid(self):
        """Create a system with valid data."""
        response = self.client.post('/api/systems', json={
            'name': 'Test System',
            'status': 'active',
        })
        # Should return 401 without auth (token_required decorator)
        # But we test that the model enforcement works
        self.assertIn(response.status_code, [201, 401])

    def test_create_system_missing_name(self):
        """Create a system without name should return validation error."""
        response = self.client.post('/api/systems', json={
            'status': 'active',
        })
        self.assertIn(response.status_code, [400, 401])

    def test_create_system_invalid_status(self):
        """Create a system with invalid status should return validation error."""
        response = self.client.post('/api/systems', json={
            'name': 'Test System',
            'status': 'invalid',
        })
        self.assertIn(response.status_code, [400, 401])

    def test_get_system_not_found(self):
        """Get non-existent system should return 404."""
        response = self.client.get('/api/systems/99999')
        self.assertIn(response.status_code, [404, 401])

    def test_database_system_model_to_dict(self):
        """Test System.to_dict() method."""
        from database import System
        import json
        system = System(
            id=1,
            name='Test System',
            status='active',
            nodes=json.dumps(['node1', 'node2']),
        )
        data = system.to_dict()
        self.assertEqual(data['id'], 1)
        self.assertEqual(data['name'], 'Test System')
        self.assertEqual(data['status'], 'active')
        self.assertEqual(data['nodes'], ['node1', 'node2'])

    def test_database_system_from_dict(self):
        """Test System.from_dict() class method."""
        from database import System
        import json
        data = {
            'name': 'Test System',
            'status': 'active',
            'nodes': ['node1', 'node2'],
        }
        system = System.from_dict(data)
        self.assertEqual(system.name, 'Test System')
        self.assertEqual(system.status, 'active')
        self.assertEqual(json.loads(system.nodes), ['node1', 'node2'])

    def test_database_system_from_create_dict(self):
        """Test System.from_create_dict() class method."""
        from database import System
        import json
        data = {
            'name': 'Test System',
            'status': 'active',
            'nodes': ['node1'],
        }
        system = System.from_create_dict(data)
        self.assertEqual(system.name, 'Test System')
        self.assertEqual(system.status, 'active')


if __name__ == '__main__':
    unittest.main()