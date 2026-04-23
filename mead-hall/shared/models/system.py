"""Data model for clustering systems.

This module provides the ClusteringSystem class with validation
and serialization capabilities.
"""

import json
from datetime import datetime


VALID_STATUSES = {'active', 'inactive', 'maintenance', 'error'}


class ClusteringSystem:
    """Represents a clustering system with nodes.

    Attributes:
        id: Unique identifier for the system.
        name: Name of the clustering system.
        status: Current status (active, inactive, maintenance, error).
        nodes: List of node identifiers or node dictionaries.
    """

    def __init__(self, id, name, status, nodes=None):
        self.id = id
        self.name = name
        self.status = status
        self.nodes = nodes or []

    def to_dict(self):
        """Convert the system to a dictionary representation."""
        return {
            'id': self.id,
            'name': self.name,
            'status': self.status,
            'nodes': self.nodes,
        }

    @classmethod
    def from_dict(cls, data):
        """Create a ClusteringSystem from a dictionary.

        Args:
            data: Dictionary with id, name, status, and optional nodes.

        Returns:
            A new ClusteringSystem instance.
        """
        return cls(
            id=data['id'],
            name=data['name'],
            status=data['status'],
            nodes=data.get('nodes', []),
        )

    @classmethod
    def create(cls, name, status='active', nodes=None):
        """Create a new ClusteringSystem with validation.

        Args:
            name: Name of the system (required).
            status: Status of the system (default: 'active').
            nodes: Optional list of nodes.

        Returns:
            A tuple (ClusteringSystem, error) where error is None on success.

        Raises:
            ValueError: If validation fails.
        """
        errors = []

        if not name or not isinstance(name, str) or not name.strip():
            errors.append("'name' is required and must be a non-empty string")

        if status not in VALID_STATUSES:
            errors.append(f"'status' must be one of: {', '.join(sorted(VALID_STATUSES))}")

        if errors:
            raise ValueError('; '.join(errors))

        system = cls(
            id=None,  # Will be assigned by database
            name=name.strip(),
            status=status,
            nodes=nodes or [],
        )
        return system

    def validate_update(self, data):
        """Validate update data for this system.

        Args:
            data: Dictionary of fields to update.

        Returns:
            A tuple (validated_data, error) where error is None on success.
        """
        errors = []

        if 'name' in data:
            name = data['name']
            if not isinstance(name, str):
                errors.append("'name' must be a string")
            elif not name.strip():
                errors.append("'name' cannot be empty")
            elif len(name) > 255:
                errors.append("'name' must be less than 255 characters")

        if 'status' in data:
            status = data['status']
            if status not in VALID_STATUSES:
                errors.append(f"'status' must be one of: {', '.join(sorted(VALID_STATUSES))}")

        if 'nodes' in data:
            nodes = data['nodes']
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

    def __repr__(self):
        return f"ClusteringSystem(id={self.id}, name={self.name!r}, status={self.status!r})"

    def __eq__(self, other):
        if not isinstance(other, ClusteringSystem):
            return False
        return self.id == other.id

    def __hash__(self):
        return hash(self.id)