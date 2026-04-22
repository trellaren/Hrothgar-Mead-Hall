# Main Flask application for clustering systems management
from flask import Flask, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# In-memory storage for clustering systems (in production, this would be a database)
systems = []

@app.route('/api/systems', methods=['GET'])
def get_systems():
    return jsonify(systems)

@app.route('/api/systems/<int:system_id>', methods=['GET'])
def get_system(system_id):
    system = next((s for s in systems if s['id'] == system_id), None)
    if system:
        return jsonify(system)
    return jsonify({'error': 'System not found'}), 404

@app.route('/api/systems', methods=['POST'])
def create_system():
    # This would normally include validation
    new_system = {
        'id': len(systems) + 1,
        'name': 'New System',
        'status': 'active',
        'nodes': []
    }
    systems.append(new_system)
    return jsonify(new_system), 201

@app.route('/api/systems/<int:system_id>', methods=['PUT'])
def update_system(system_id):
    system = next((s for s in systems if s['id'] == system_id), None)
    if system:
        # This would normally include validation
        system.update({'status': 'updated'})
        return jsonify(system)
    return jsonify({'error': 'System not found'}), 404

@app.route('/api/systems/<int:system_id>', methods=['DELETE'])
def delete_system(system_id):
    global systems
    systems = [s for s in systems if s['id'] != system_id]
    return jsonify({'message': 'System deleted'})

if __name__ == '__main__':
    app.run(debug=True, port=5000)