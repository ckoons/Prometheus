"""
Retrospective Models

This module defines the domain models for retrospectives in the Prometheus/Epimethius Planning System.
"""

from datetime import datetime
from typing import Dict, List, Any, Optional, Set
import uuid


class RetroItem:
    """Model for an item in a retrospective."""

    def __init__(
        self,
        item_id: str,
        content: str,
        category: str,  # e.g., "what_went_well", "what_didnt_go_well", "action_item"
        votes: int = 0,
        author: Optional[str] = None,
        related_task_ids: List[str] = None,
        metadata: Dict[str, Any] = None
    ):
        self.item_id = item_id
        self.content = content
        self.category = category
        self.votes = votes
        self.author = author
        self.related_task_ids = related_task_ids or []
        self.metadata = metadata or {}
        self.created_at = datetime.now().timestamp()
        self.updated_at = self.created_at

    def to_dict(self) -> Dict[str, Any]:
        """Convert the retrospective item to a dictionary."""
        return {
            "item_id": self.item_id,
            "content": self.content,
            "category": self.category,
            "votes": self.votes,
            "author": self.author,
            "related_task_ids": self.related_task_ids,
            "metadata": self.metadata,
            "created_at": self.created_at,
            "updated_at": self.updated_at
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'RetroItem':
        """Create a retrospective item from a dictionary."""
        item = cls(
            item_id=data["item_id"],
            content=data["content"],
            category=data["category"],
            votes=data.get("votes", 0),
            author=data.get("author"),
            related_task_ids=data.get("related_task_ids", []),
            metadata=data.get("metadata", {})
        )
        
        # Set timestamps if provided
        if "created_at" in data:
            item.created_at = data["created_at"]
        if "updated_at" in data:
            item.updated_at = data["updated_at"]
            
        return item

    def add_vote(self):
        """Add a vote for this item."""
        self.votes += 1
        self.updated_at = datetime.now().timestamp()

    def remove_vote(self) -> bool:
        """Remove a vote from this item."""
        if self.votes > 0:
            self.votes -= 1
            self.updated_at = datetime.now().timestamp()
            return True
        return False

    def update_content(self, content: str):
        """Update the content of the item."""
        self.content = content
        self.updated_at = datetime.now().timestamp()

    def update_category(self, category: str):
        """Update the category of the item."""
        self.category = category
        self.updated_at = datetime.now().timestamp()

    @staticmethod
    def create_new(
        content: str,
        category: str,
        author: Optional[str] = None,
        related_task_ids: List[str] = None,
        metadata: Dict[str, Any] = None
    ) -> 'RetroItem':
        """
        Create a new retrospective item with a generated ID.
        
        Args:
            content: Content of the item
            category: Category of the item
            author: Optional author identifier
            related_task_ids: Optional list of related task IDs
            metadata: Optional metadata
            
        Returns:
            A new RetroItem instance
        """
        item_id = f"retro-item-{uuid.uuid4()}"
        return RetroItem(
            item_id=item_id,
            content=content,
            category=category,
            author=author,
            related_task_ids=related_task_ids,
            metadata=metadata
        )


class ActionItem:
    """Model for an action item from a retrospective."""

    def __init__(
        self,
        action_id: str,
        title: str,
        description: str,
        assignees: List[str] = None,
        due_date: Optional[datetime] = None,
        status: str = "open",  # "open", "in_progress", "completed", "cancelled"
        priority: str = "medium",  # "low", "medium", "high", "critical"
        related_retro_items: List[str] = None,
        metadata: Dict[str, Any] = None
    ):
        self.action_id = action_id
        self.title = title
        self.description = description
        self.assignees = assignees or []
        self.due_date = due_date
        self.status = status
        self.priority = priority
        self.related_retro_items = related_retro_items or []
        self.metadata = metadata or {}
        self.created_at = datetime.now().timestamp()
        self.updated_at = self.created_at
        self.completed_at = None
        self.status_history = [{
            "status": status,
            "timestamp": self.created_at
        }]

    def to_dict(self) -> Dict[str, Any]:
        """Convert the action item to a dictionary."""
        return {
            "action_id": self.action_id,
            "title": self.title,
            "description": self.description,
            "assignees": self.assignees,
            "due_date": self.due_date.isoformat() if self.due_date else None,
            "status": self.status,
            "priority": self.priority,
            "related_retro_items": self.related_retro_items,
            "metadata": self.metadata,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "completed_at": self.completed_at,
            "status_history": self.status_history
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ActionItem':
        """Create an action item from a dictionary."""
        # Convert date strings to datetime objects
        due_date = datetime.fromisoformat(data["due_date"]) if data.get("due_date") else None
        
        # Create the action item
        action = cls(
            action_id=data["action_id"],
            title=data["title"],
            description=data["description"],
            assignees=data.get("assignees", []),
            due_date=due_date,
            status=data.get("status", "open"),
            priority=data.get("priority", "medium"),
            related_retro_items=data.get("related_retro_items", []),
            metadata=data.get("metadata", {})
        )
        
        # Set timestamps and history if provided
        if "created_at" in data:
            action.created_at = data["created_at"]
        if "updated_at" in data:
            action.updated_at = data["updated_at"]
        if "completed_at" in data and data["completed_at"]:
            action.completed_at = data["completed_at"]
        if "status_history" in data:
            action.status_history = data["status_history"]
            
        return action

    def update_status(self, status: str, comment: Optional[str] = None):
        """Update the status of the action item."""
        self.status = status
        self.updated_at = datetime.now().timestamp()
        
        # Set completed_at if status is "completed"
        if status == "completed" and not self.completed_at:
            self.completed_at = self.updated_at
        elif status != "completed":
            self.completed_at = None
        
        # Add to status history
        self.status_history.append({
            "status": status,
            "timestamp": self.updated_at,
            "comment": comment
        })

    def assign_to(self, assignee: str):
        """Assign the action item to a person."""
        if assignee not in self.assignees:
            self.assignees.append(assignee)
            self.updated_at = datetime.now().timestamp()

    def unassign_from(self, assignee: str) -> bool:
        """Unassign the action item from a person."""
        if assignee in self.assignees:
            self.assignees.remove(assignee)
            self.updated_at = datetime.now().timestamp()
            return True
        return False

    def update_due_date(self, due_date: datetime):
        """Update the due date of the action item."""
        self.due_date = due_date
        self.updated_at = datetime.now().timestamp()

    def update_priority(self, priority: str):
        """Update the priority of the action item."""
        self.priority = priority
        self.updated_at = datetime.now().timestamp()

    def is_overdue(self) -> bool:
        """Check if the action item is overdue."""
        if not self.due_date or self.status == "completed" or self.status == "cancelled":
            return False
        return datetime.now() > self.due_date

    @staticmethod
    def create_new(
        title: str,
        description: str,
        assignees: List[str] = None,
        due_date: Optional[datetime] = None,
        priority: str = "medium",
        related_retro_items: List[str] = None,
        metadata: Dict[str, Any] = None
    ) -> 'ActionItem':
        """
        Create a new action item with a generated ID.
        
        Args:
            title: Title of the action item
            description: Description of the action item
            assignees: Optional list of assignees
            due_date: Optional due date
            priority: Optional priority
            related_retro_items: Optional list of related retrospective item IDs
            metadata: Optional metadata
            
        Returns:
            A new ActionItem instance
        """
        action_id = f"action-{uuid.uuid4()}"
        return ActionItem(
            action_id=action_id,
            title=title,
            description=description,
            assignees=assignees,
            due_date=due_date,
            priority=priority,
            related_retro_items=related_retro_items,
            metadata=metadata
        )


class Retrospective:
    """Model for a project retrospective."""

    def __init__(
        self,
        retro_id: str,
        plan_id: str,
        name: str,
        date: datetime,
        format: str,  # "start_stop_continue", "4_ls", "mad_sad_glad", etc.
        facilitator: str,
        participants: List[str] = None,
        items: List[RetroItem] = None,
        action_items: List[ActionItem] = None,
        status: str = "draft",  # "draft", "in_progress", "completed"
        metadata: Dict[str, Any] = None
    ):
        self.retro_id = retro_id
        self.plan_id = plan_id
        self.name = name
        self.date = date
        self.format = format
        self.facilitator = facilitator
        self.participants = participants or []
        self.items = items or []
        self.action_items = action_items or []
        self.status = status
        self.metadata = metadata or {}
        self.created_at = datetime.now().timestamp()
        self.updated_at = self.created_at

    def to_dict(self) -> Dict[str, Any]:
        """Convert the retrospective to a dictionary."""
        return {
            "retro_id": self.retro_id,
            "plan_id": self.plan_id,
            "name": self.name,
            "date": self.date.isoformat() if self.date else None,
            "format": self.format,
            "facilitator": self.facilitator,
            "participants": self.participants,
            "items": [item.to_dict() for item in self.items],
            "action_items": [action.to_dict() for action in self.action_items],
            "status": self.status,
            "metadata": self.metadata,
            "created_at": self.created_at,
            "updated_at": self.updated_at
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Retrospective':
        """Create a retrospective from a dictionary."""
        # Convert date strings to datetime objects
        date = datetime.fromisoformat(data["date"]) if data.get("date") else None
        
        # Convert items to RetroItem objects
        items = []
        for item_data in data.get("items", []):
            items.append(RetroItem.from_dict(item_data))
        
        # Convert action items to ActionItem objects
        action_items = []
        for action_data in data.get("action_items", []):
            action_items.append(ActionItem.from_dict(action_data))
        
        # Create the retrospective
        retro = cls(
            retro_id=data["retro_id"],
            plan_id=data["plan_id"],
            name=data["name"],
            date=date,
            format=data["format"],
            facilitator=data["facilitator"],
            participants=data.get("participants", []),
            items=items,
            action_items=action_items,
            status=data.get("status", "draft"),
            metadata=data.get("metadata", {})
        )
        
        # Set timestamps if provided
        if "created_at" in data:
            retro.created_at = data["created_at"]
        if "updated_at" in data:
            retro.updated_at = data["updated_at"]
            
        return retro

    def add_item(self, item: RetroItem) -> None:
        """Add a retrospective item."""
        self.items.append(item)
        self.updated_at = datetime.now().timestamp()

    def remove_item(self, item_id: str) -> bool:
        """Remove a retrospective item."""
        for i, item in enumerate(self.items):
            if item.item_id == item_id:
                del self.items[i]
                self.updated_at = datetime.now().timestamp()
                return True
        return False

    def get_item(self, item_id: str) -> Optional[RetroItem]:
        """Get a retrospective item by ID."""
        for item in self.items:
            if item.item_id == item_id:
                return item
        return None

    def add_action_item(self, action_item: ActionItem) -> None:
        """Add an action item."""
        self.action_items.append(action_item)
        self.updated_at = datetime.now().timestamp()

    def remove_action_item(self, action_id: str) -> bool:
        """Remove an action item."""
        for i, action in enumerate(self.action_items):
            if action.action_id == action_id:
                del self.action_items[i]
                self.updated_at = datetime.now().timestamp()
                return True
        return False

    def get_action_item(self, action_id: str) -> Optional[ActionItem]:
        """Get an action item by ID."""
        for action in self.action_items:
            if action.action_id == action_id:
                return action
        return None

    def update_status(self, status: str):
        """Update the status of the retrospective."""
        self.status = status
        self.updated_at = datetime.now().timestamp()

    def start(self):
        """Start the retrospective."""
        if self.status == "draft":
            self.status = "in_progress"
            self.updated_at = datetime.now().timestamp()

    def finalize(self) -> None:
        """Finalize the retrospective."""
        self.status = "completed"
        self.updated_at = datetime.now().timestamp()

    def get_items_by_category(self, category: str) -> List[RetroItem]:
        """Get retrospective items by category."""
        return [item for item in self.items if item.category == category]

    def get_top_voted_items(self, limit: int = 5) -> List[RetroItem]:
        """Get the top voted retrospective items."""
        sorted_items = sorted(self.items, key=lambda x: x.votes, reverse=True)
        return sorted_items[:limit]

    def get_incomplete_action_items(self) -> List[ActionItem]:
        """Get incomplete action items."""
        return [action for action in self.action_items 
                if action.status != "completed" and action.status != "cancelled"]

    def get_action_items_by_priority(self, priority: str) -> List[ActionItem]:
        """Get action items by priority."""
        return [action for action in self.action_items if action.priority == priority]

    @staticmethod
    def create_new(
        plan_id: str,
        name: str,
        format: str,
        facilitator: str,
        date: Optional[datetime] = None,
        participants: List[str] = None,
        metadata: Dict[str, Any] = None
    ) -> 'Retrospective':
        """
        Create a new retrospective with a generated ID.
        
        Args:
            plan_id: ID of the plan
            name: Name of the retrospective
            format: Format of the retrospective
            facilitator: Facilitator of the retrospective
            date: Optional date of the retrospective (defaults to now)
            participants: Optional list of participants
            metadata: Optional metadata
            
        Returns:
            A new Retrospective instance
        """
        retro_id = f"retro-{uuid.uuid4()}"
        return Retrospective(
            retro_id=retro_id,
            plan_id=plan_id,
            name=name,
            date=date or datetime.now(),
            format=format,
            facilitator=facilitator,
            participants=participants,
            metadata=metadata
        )