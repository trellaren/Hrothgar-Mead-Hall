# Data model for clustering systems

class ClusteringSystem:
    def __init__(self, id, name, status, nodes=None):
        self.id = id
        self.name = name
        self.status = status
        self.nodes = nodes or []
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'status': self.status,
            'nodes': self.nodes
        }
    
    @classmethod
    def from_dict(cls, data):
        return cls(
            id=data['id'],
            name=data['name'],
            status=data['status'],
            nodes=data.get('nodes', [])
        )