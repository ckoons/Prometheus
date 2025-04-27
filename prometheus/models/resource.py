"""
Resource Models

This module defines the domain models for resources in the Prometheus/Epimethius Planning System.
"""

from datetime import datetime
from typing import Dict, List, Any, Optional, Set
import uuid


class Resource:
    """Resource model representing a resource that can be assigned to tasks."""

    def __init__(
        self,
        resource_id: str,
        name: str,
        resource_type: str,  # "human", "equipment", "service", etc.
        capacity: float,  # e.g., hours per day or units available
        skills: List[str] = None,
        availability: Dict[str, Any] = None,  # e.g., {"weekdays": [1, 2, 3, 4, 5], "hours": [9, 17]}
        cost_rate: Optional[float] = None,  # Cost per unit (e.g., hourly rate)
        metadata: Dict[str, Any] = None
    ):
        self.resource_id = resource_id
        self.name = name
        self.resource_type = resource_type
        self.capacity = capacity
        self.skills = skills or []
        self.availability = availability or {}
        self.cost_rate = cost_rate
        self.metadata = metadata or {}
        self.created_at = datetime.now().timestamp()
        self.updated_at = self.created_at

    def to_dict(self) -> Dict[str, Any]:
        """Convert the resource to a dictionary."""
        return {
            "resource_id": self.resource_id,
            "name": self.name,
            "resource_type": self.resource_type,
            "capacity": self.capacity,
            "skills": self.skills,
            "availability": self.availability,
            "cost_rate": self.cost_rate,
            "metadata": self.metadata,
            "created_at": self.created_at,
            "updated_at": self.updated_at
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Resource':
        """Create a resource from a dictionary."""
        resource = cls(
            resource_id=data["resource_id"],
            name=data["name"],
            resource_type=data["resource_type"],
            capacity=data["capacity"],
            skills=data.get("skills", []),
            availability=data.get("availability", {}),
            cost_rate=data.get("cost_rate"),
            metadata=data.get("metadata", {})
        )
        
        # Set timestamps if provided
        if "created_at" in data:
            resource.created_at = data["created_at"]
        if "updated_at" in data:
            resource.updated_at = data["updated_at"]
            
        return resource

    def add_skill(self, skill: str):
        """Add a skill to the resource."""
        if skill not in self.skills:
            self.skills.append(skill)
            self.updated_at = datetime.now().timestamp()

    def remove_skill(self, skill: str) -> bool:
        """Remove a skill from the resource."""
        if skill in self.skills:
            self.skills.remove(skill)
            self.updated_at = datetime.now().timestamp()
            return True
        return False

    def update_capacity(self, capacity: float):
        """Update the resource capacity."""
        self.capacity = capacity
        self.updated_at = datetime.now().timestamp()

    def update_availability(self, availability: Dict[str, Any]):
        """Update the resource availability."""
        self.availability = availability
        self.updated_at = datetime.now().timestamp()

    def update_cost_rate(self, cost_rate: float):
        """Update the resource cost rate."""
        self.cost_rate = cost_rate
        self.updated_at = datetime.now().timestamp()

    def has_skill(self, skill: str) -> bool:
        """Check if the resource has a skill."""
        return skill in self.skills

    def calculate_cost(self, hours: float) -> float:
        """
        Calculate the cost for a given number of hours.
        
        Args:
            hours: Number of hours to calculate cost for
            
        Returns:
            Cost for the given hours
        """
        if self.cost_rate is None:
            return 0.0
        return hours * self.cost_rate

    @staticmethod
    def create_new(
        name: str,
        resource_type: str,
        capacity: float,
        skills: List[str] = None,
        availability: Dict[str, Any] = None,
        cost_rate: Optional[float] = None,
        metadata: Dict[str, Any] = None
    ) -> 'Resource':
        """
        Create a new resource with a generated ID.
        
        Args:
            name: Name of the resource
            resource_type: Type of resource
            capacity: Capacity of the resource
            skills: Optional list of skills
            availability: Optional availability dictionary
            cost_rate: Optional cost rate
            metadata: Optional metadata
            
        Returns:
            A new Resource instance
        """
        resource_id = f"resource-{uuid.uuid4()}"
        return Resource(
            resource_id=resource_id,
            name=name,
            resource_type=resource_type,
            capacity=capacity,
            skills=skills,
            availability=availability,
            cost_rate=cost_rate,
            metadata=metadata
        )