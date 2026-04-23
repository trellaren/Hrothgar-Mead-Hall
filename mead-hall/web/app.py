# Main Flask application for clustering systems management
import os
import json
import secrets
from datetime import datetime, timedelta
from functools import wraps

from flask import Flask, jsonify, request, g
from flask_cors import CORS
from flask_bcrypt import Bcrypt
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user

from database import init_db, get_db_session, System as DbSystem

# Initialize Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', secrets.token_hex(32))

CORS(app)
bcrypt = Bcrypt(app)

# Flask-Login setup
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# In-memory storage for backward compatibility (will be replaced by database)
systems = []

# ==================== User Model for Flask-Login ====================

class User(UserMixin):
    """Simple user model for authentication."""
    def __init__(self, id, username, role='user'):
        self.id = id
        self.username = username
        self.role = role

    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'role': self.role,
        }


# In-memory user store (in production, this would be a database)
USERS_DB = {
    'admin': bcrypt.generate_password_hash('admin123').decode('utf-8'),
    'user': bcrypt.generate_password_hash('user123').decode('utf-8'),
}
ROLES = {
    'admin': 'admin',
    'user': 'user',
}


@login_manager.user_loader
def load_user(user_id):
    """Load user by ID for Flask-Login."""
    for username, role in ROLES.items():
        if str(list(ROLES.keys()).index(username) + 1) == str(user_id):
            return User(int(user_id), username, role)
    return None


# ==================== Authentication Routes ====================

@app.route('/api/auth/login', methods=['POST'])
def login():
    """Authenticate a user and return a token."""
    data = request.get_json()
    if not data:
        return jsonify({'error': 'No data provided'}), 400

    username = data.get('username', '')
    password = data.get('password', '')

    if not username or not password:
        return jsonify({'error': 'Username and password are required'}), 400

    # Check credentials against in-memory store
    if username in USERS_DB and bcrypt.check_password_hash(USERS_DB[username], password):
        role = ROLES.get(username, 'user')
        user = User(list(ROLES.keys()).index(username) + 1, username, role)
        login_user(user)

        # Generate a simple session token (in production, use JWT)
        token = secrets.token_hex(32)
        # Store token temporarily (in production, use proper session management)
        if not hasattr(app, 'active_tokens'):
            app.active_tokens = {}
        app.active_tokens[token] = {
            'user_id': user.id,
            'expires': datetime.utcnow() + timedelta(hours=24),
        }

        return jsonify({
            'message': 'Login successful',
            'token': token,
            'user': user.to_dict(),
        }), 200

    return jsonify({'error': 'Invalid username or password'}), 401


@app.route('/api/auth/register', methods=['POST'])
def register():
    """Register a new user."""
    data = request.get_json()
    if not data:
        return jsonify({'error': 'No data provided'}), 400

    username = data.get('username', '')
    password = data.get('password', '')

    if not username or not password:
        return jsonify({'error': 'Username and password are required'}), 400

    if len(password) < 8:
        return jsonify({'error': 'Password must be at least 8 characters long'}), 400

    # Check if user already exists
    if username in USERS_DB:
        return jsonify({'error': 'Username already exists'}), 409

    # Create new user
    new_user_id = len(ROLES) + 1
    USERS_DB[username] = bcrypt.generate_password_hash(password).decode('utf-8')
    ROLES[username] = 'user'

    return jsonify({
        'message': 'User registered successfully',
        'user': {'id': new_user_id, 'username': username, 'role': 'user'},
    }), 201


@app.route('/api/auth/logout', methods=['POST'])
@login_required
def logout():
    """Logout the current user."""
    logout_user()
    return jsonify({'message': 'Logged out successfully'}), 200


@app.route('/api/auth/me', methods=['GET'])
@login_required
def get_current_user():
    """Get current user info."""
    return jsonify({'user': current_user.to_dict()}), 200


# ==================== Authentication Decorator ====================

def token_required(f):
    """Decorator to require token authentication."""
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None

        # Check for token in Authorization header
        auth_header = request.headers.get('Authorization')
        if auth_header:
            if auth_header.startswith('Bearer '):
                token = auth_header[7:]
            else:
                token = auth_header

        if not token:
            return jsonify({'error': 'Authentication token is required'}), 401

        # Validate token (in production, use JWT validation)
        active_tokens = getattr(app, 'active_tokens', {})
        if token not in active_tokens:
            return jsonify({'error': 'Invalid or expired token'}), 401

        # Check expiration
        token_data = active_tokens[token]
        if datetime.utcnow() > token_data['expires']:
            del active_tokens[token]
            return jsonify({'error': 'Token has expired'}), 401

        # Set current token in globals for access in the decorated function
        g.current_token = token
        g.current_user_id = token_data['user_id']

        return f(*args, **kwargs)
    return decorated


def admin_required(f):
    """Decorator to require admin role."""
    @wraps(f)
    @token_required
    def decorated(*args, **kwargs):
        # For now, all authenticated users are admin
        # In production, check current_user.role == 'admin'
        return f(*args, **kwargs)
    return decorated


# ==================== Model Enforcement ====================

VALID_STATUSES = {'active', 'inactive', 'maintenance', 'error'}
REQUIRED_SYSTEM_FIELDS = {'name', 'status'}


def validate_system_data(data, is_update=False):
    """
    Validate system data on creation/update.
    Returns (validated_data, error) tuple.
    """
    if not data:
        return None, {'error': 'No data provided'}

    errors = []

    # Check required fields (only for creation, not update)
    if not is_update:
        for field in REQUIRED_SYSTEM_FIELDS:
            if field not in data:
                errors.append(f"'{field}' is required")

    if errors:
        return None, {'error': '; '.join(errors)}

    # Validate name
    name = data.get('name')
    if name:
        if not isinstance(name, str):
            errors.append("'name' must be a string")
        elif len(name.strip()) == 0:
            errors.append("'name' cannot be empty")
        elif len(name) > 255:
            errors.append("'name' must be less than 255 characters")

    # Validate status
    status = data.get('status')
    if status:
        if status not in VALID_STATUSES:
            errors.append(f"'status' must be one of: {', '.join(sorted(VALID_STATUSES))}")

    # Validate nodes if provided
    nodes = data.get('nodes')
    if nodes is not None:
        if not isinstance(nodes, list):
            errors.append("'nodes' must be an array")
        else:
            for i, node in enumerate(nodes):
                if isinstance(node, dict):
                    if 'id' not in node and 'address' not in node:
                        errors.append(f"Node at index {i} must have 'id' or 'address'")
                elif not isinstance(node, str):
                    errors.append(f"Node at index {i} must be a string or object")

    if errors:
        return None, {'error': '; '.join(errors)}

    return data, None


def enforce_model(data, is_update=False):
    """
    Enforce the ClusteringSystem model schema.
    Returns (enforced_data, error) tuple.
    Ensures all fields are present and properly typed.
    """
    validated, err = validate_system_data(data, is_update)
    if err:
        return None, err

    # Build enforced data with proper defaults
    enforced = {}

    # Name: must be present and sanitized
    name = validated.get('name', '').strip()
    enforced['name'] = name if name else ('New System' if not is_update else None)
    if not is_update and not name:
        return None, {'error': "'name' is required and cannot be empty"}

    # Status: must be valid, default to 'active' on creation
    status = validated.get('status', 'active')
    enforced['status'] = status

    # Nodes: must be a list, default to empty list
    nodes = validated.get('nodes', [])
    enforced['nodes'] = nodes

    # Add timestamps for creation
    if not is_update:
        enforced['created_at'] = datetime.utcnow().isoformat()
        enforced['updated_at'] = enforced['created_at']

    return enforced, None


# ==================== System CRUD Endpoints ====================

@app.route('/api/systems', methods=['GET'])
@token_required
def get_systems():
    """Get all clustering systems."""
    # Use database if available, fall back to in-memory
    db_session = get_db_session()
    try:
        db_systems = db_session.query(DbSystem).all()
        if db_systems:
            return jsonify([s.to_dict() for s in db_systems])
    finally:
        db_session.close()

    # Fallback to in-memory storage
    return jsonify(systems)


@app.route('/api/systems/<int:system_id>', methods=['GET'])
@token_required
def get_system(system_id):
    """Get a specific clustering system by ID."""
    # Check database first
    db_session = get_db_session()
    try:
        db_system = db_session.query(DbSystem).get(system_id)
        if db_system:
            return jsonify(db_system.to_dict())
    finally:
        db_session.close()

    # Fallback to in-memory storage
    system = next((s for s in systems if s['id'] == system_id), None)
    if system:
        return jsonify(system)
    return jsonify({'error': 'System not found'}), 404


@app.route('/api/systems', methods=['POST'])
@token_required
def create_system():
    """Create a new clustering system with model enforcement and validation."""
    # Validate and enforce model
    enforced_data, error = enforce_model(request.get_json(), is_update=False)
    if error:
        return jsonify(error), 400

    # Use database
    db_session = get_db_session()
    try:
        db_system = DbSystem.from_create_dict(enforced_data)
        db_session.add(db_system)
        db_session.commit()
        db_session.refresh(db_system)
        return jsonify(db_system.to_dict()), 201
    except Exception as e:
        db_session.rollback()
        return jsonify({'error': f'Database error: {str(e)}'}), 500
    finally:
        db_session.close()


@app.route('/api/systems/<int:system_id>', methods=['PUT'])
@token_required
def update_system(system_id):
    """Update a clustering system with validation."""
    # Check database first
    db_session = get_db_session()
    try:
        db_system = db_session.query(DbSystem).get(system_id)
        if not db_system:
            return jsonify({'error': 'System not found'}), 404

        # Validate and enforce model for update
        data = request.get_json()
        enforced_data, error = enforce_model(data, is_update=True)
        if error:
            return jsonify(error), 400

        # Apply updates
        if 'name' in enforced_data:
            db_system.name = enforced_data['name']
        if 'status' in enforced_data:
            db_system.status = enforced_data['status']
        if 'nodes' in enforced_data:
            import json
            db_system.nodes = json.dumps(enforced_data['nodes'])
        db_system.updated_at = datetime.utcnow()

        db_session.commit()
        return jsonify(db_system.to_dict())
    except Exception as e:
        db_session.rollback()
        return jsonify({'error': f'Database error: {str(e)}'}), 500
    finally:
        db_session.close()


@app.route('/api/systems/<int:system_id>', methods=['DELETE'])
@token_required
def delete_system(system_id):
    """Delete a clustering system."""
    # Check database
    db_session = get_db_session()
    try:
        db_system = db_session.query(DbSystem).get(system_id)
        if not db_system:
            return jsonify({'error': 'System not found'}), 404

        db_session.delete(db_system)
        db_session.commit()
        return jsonify({'message': 'System deleted'})
    except Exception as e:
        db_session.rollback()
        return jsonify({'error': f'Database error: {str(e)}'}), 500
    finally:
        db_session.close()


# ==================== Health Check ====================

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.utcnow().isoformat(),
    })


# ==================== Initialization ====================

with app.app_context():
    init_db()


if __name__ == '__main__':
    app.run(debug=True, port=5000)