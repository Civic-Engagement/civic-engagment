"""
Event Manager Backend - Civic Event Management & Community Organizing
Handles event creation, registration, attendance tracking, and community coordination
"""

import os
import json
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple

# Import application components
try:
    from ..blockchain.blockchain import add_user_action
    from ..users.auth import SessionManager, RoleChecker
    from ..utils.validation import DataValidator
except ImportError as e:
    print(f"Warning: Import error in event manager: {e}")


def get_events_db_path() -> str:
    """Get path to events database"""
    try:
        from civic_desktop.main import ENV_CONFIG
        return ENV_CONFIG.get('events_db_path', os.path.join(os.path.dirname(__file__), 'events_db.json'))
    except Exception:
        return os.path.join(os.path.dirname(__file__), 'events_db.json')


class EventManager:
    """Comprehensive civic event management system"""
    
    # Event types with their requirements
    EVENT_TYPES = {
        'town_hall': {
            'required_roles': ['contract_representative', 'contract_senator', 'contract_elder'],
            'constitutional_review': True,
            'public_notice_days': 14,
            'capacity_limits': None,
            'recording_required': True,
            'description': 'Official town hall meeting for community governance'
        },
        'debate_forum': {
            'required_roles': ['contract_member', 'contract_representative'],
            'constitutional_review': True,
            'public_notice_days': 7,
            'capacity_limits': 200,
            'recording_required': True,
            'description': 'Structured debate on civic issues'
        },
        'training_session': {
            'required_roles': ['contract_member'],
            'constitutional_review': False,
            'public_notice_days': 3,
            'capacity_limits': 50,
            'recording_required': False,
            'description': 'Educational session on civic participation'
        },
        'election_event': {
            'required_roles': ['contract_representative', 'contract_senator', 'contract_elder'],
            'constitutional_review': True,
            'public_notice_days': 30,
            'capacity_limits': None,
            'recording_required': True,
            'description': 'Official election or voting event'
        },
        'community_meeting': {
            'required_roles': ['contract_member'],
            'constitutional_review': False,
            'public_notice_days': 3,
            'capacity_limits': 100,
            'recording_required': False,
            'description': 'General community gathering'
        }
    }
    
    def __init__(self):
        """Initialize event manager"""
        self.db_path = get_events_db_path()
        self.ensure_database()
    
    def ensure_database(self):
        """Ensure events database exists with proper structure"""
        if not os.path.exists(self.db_path):
            initial_data = {
                'events': [],
                'working_groups': [],
                'attendees': {},
                'outcomes': {}
            }
            
            os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
            
            with open(self.db_path, 'w') as f:
                json.dump(initial_data, f, indent=2)
    
    def load_data(self) -> Dict:
        """Load events database"""
        try:
            with open(self.db_path, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            self.ensure_database()
            return self.load_data()
        except json.JSONDecodeError:
            self.ensure_database()
            return self.load_data()
    
    def save_data(self, data: Dict):
        """Save events database"""
        try:
            with open(self.db_path, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"Error saving events data: {e}")
    
    def validate_event_authority(self, organizer_email: str, event_type: str) -> Tuple[bool, str]:
        """Validate organizer has authority to create event type"""
        try:
            user = SessionManager.get_current_user()
            if not user or user.get('email') != organizer_email:
                return False, "Invalid organizer - must be current user"
            
            user_role = user.get('role', 'contract_member')
            
            if event_type not in self.EVENT_TYPES:
                return False, f"Invalid event type: {event_type}"
            
            required_roles = self.EVENT_TYPES[event_type]['required_roles']
            
            if user_role not in required_roles:
                return False, f"Role '{user_role}' cannot organize '{event_type}' events"
            
            return True, "Authority validated"
            
        except Exception as e:
            return False, f"Error validating authority: {e}"
    
    def create_event(self, event_data: Dict, organizer_email: str) -> Tuple[bool, str, Optional[str]]:
        """
        Create new civic event with constitutional compliance
        
        Args:
            event_data: Event details (title, type, datetime, venue, etc.)
            organizer_email: Email of event organizer
            
        Returns:
            Tuple of (success, message, event_id)
        """
        try:
            # Validate required fields
            required_fields = ['title', 'type', 'datetime', 'description']
            for field in required_fields:
                if field not in event_data:
                    return False, f"Missing required field: {field}", None
            
            # Validate event type
            event_type = event_data.get('type')
            if event_type not in self.EVENT_TYPES:
                return False, f"Invalid event type: {event_type}", None
            
            # Validate organizer authority
            is_valid, auth_message = self.validate_event_authority(organizer_email, event_type)
            if not is_valid:
                return False, auth_message, None
            
            # Parse and validate datetime
            try:
                event_datetime = datetime.fromisoformat(event_data['datetime'])
                now = datetime.now()
                
                # Check notice period
                notice_days = self.EVENT_TYPES[event_type]['public_notice_days']
                min_date = now + timedelta(days=notice_days)
                
                if event_datetime < min_date:
                    return False, f"Event requires {notice_days} days advance notice", None
                
            except ValueError as e:
                return False, f"Invalid datetime format: {e}", None
            
            # Generate unique event ID
            event_id = str(uuid.uuid4())
            
            # Create event record
            event = {
                'id': event_id,
                'title': event_data['title'],
                'type': event_type,
                'description': event_data.get('description', ''),
                'organizer_email': organizer_email,
                'datetime': event_data['datetime'],
                'venue': event_data.get('venue', {}),
                'capacity': event_data.get('capacity', self.EVENT_TYPES[event_type]['capacity_limits']),
                'status': 'scheduled',
                'attendees': [],
                'registration_required': event_data.get('registration_required', True),
                'constitutional_review': self.EVENT_TYPES[event_type]['constitutional_review'],
                'recording_required': self.EVENT_TYPES[event_type]['recording_required'],
                'created_at': datetime.now().isoformat(),
                'updated_at': datetime.now().isoformat()
            }
            
            # Save to database
            data = self.load_data()
            data['events'].append(event)
            self.save_data(data)
            
            # Record to blockchain
            try:
                add_user_action(
                    action_type='event_created',
                    user_email=organizer_email,
                    data={
                        'event_id': event_id,
                        'title': event['title'],
                        'type': event_type,
                        'datetime': event_data['datetime'],
                        'constitutional_review': event['constitutional_review']
                    }
                )
            except Exception as e:
                print(f"Warning: Failed to record event creation to blockchain: {e}")
            
            return True, "Event created successfully", event_id
            
        except Exception as e:
            return False, f"Error creating event: {e}", None
    
    def get_event(self, event_id: str) -> Optional[Dict]:
        """Get event by ID"""
        data = self.load_data()
        for event in data.get('events', []):
            if event['id'] == event_id:
                return event
        return None
    
    def list_events(self, filter_type: Optional[str] = None, 
                   filter_status: Optional[str] = None,
                   limit: int = 50) -> List[Dict]:
        """
        List events with optional filtering
        
        Args:
            filter_type: Filter by event type
            filter_status: Filter by status (scheduled, in_progress, completed, cancelled)
            limit: Maximum number of events to return
            
        Returns:
            List of event dictionaries
        """
        data = self.load_data()
        events = data.get('events', [])
        
        # Apply filters
        if filter_type:
            events = [e for e in events if e.get('type') == filter_type]
        
        if filter_status:
            events = [e for e in events if e.get('status') == filter_status]
        
        # Sort by datetime (newest first)
        events.sort(key=lambda x: x.get('datetime', ''), reverse=True)
        
        return events[:limit]
    
    def register_attendee(self, event_id: str, user_email: str) -> Tuple[bool, str]:
        """
        Register user for event attendance
        
        Args:
            event_id: Event ID
            user_email: User email to register
            
        Returns:
            Tuple of (success, message)
        """
        try:
            data = self.load_data()
            event = None
            
            for e in data['events']:
                if e['id'] == event_id:
                    event = e
                    break
            
            if not event:
                return False, "Event not found"
            
            # Check if registration required
            if not event.get('registration_required', True):
                return False, "Event does not require registration"
            
            # Check capacity
            capacity = event.get('capacity')
            if capacity and len(event.get('attendees', [])) >= capacity:
                return False, "Event is at full capacity"
            
            # Check if already registered
            if user_email in event.get('attendees', []):
                return False, "Already registered for this event"
            
            # Add attendee
            if 'attendees' not in event:
                event['attendees'] = []
            
            event['attendees'].append(user_email)
            event['updated_at'] = datetime.now().isoformat()
            
            self.save_data(data)
            
            # Record to blockchain
            try:
                add_user_action(
                    action_type='event_registered',
                    user_email=user_email,
                    data={
                        'event_id': event_id,
                        'event_title': event['title'],
                        'event_datetime': event['datetime']
                    }
                )
            except Exception as e:
                print(f"Warning: Failed to record event registration to blockchain: {e}")
            
            return True, "Successfully registered for event"
            
        except Exception as e:
            return False, f"Error registering for event: {e}"
    
    def check_in_attendee(self, event_id: str, user_email: str) -> Tuple[bool, str]:
        """
        Check in attendee at event
        
        Args:
            event_id: Event ID
            user_email: User email to check in
            
        Returns:
            Tuple of (success, message)
        """
        try:
            data = self.load_data()
            
            # Get event
            event = None
            for e in data['events']:
                if e['id'] == event_id:
                    event = e
                    break
            
            if not event:
                return False, "Event not found"
            
            # Check if registered
            if user_email not in event.get('attendees', []):
                return False, "Not registered for this event"
            
            # Store check-in data
            if event_id not in data['attendees']:
                data['attendees'][event_id] = {}
            
            data['attendees'][event_id][user_email] = {
                'checked_in_at': datetime.now().isoformat(),
                'checked_in': True
            }
            
            self.save_data(data)
            
            # Record to blockchain
            try:
                add_user_action(
                    action_type='event_attendance',
                    user_email=user_email,
                    data={
                        'event_id': event_id,
                        'event_title': event['title'],
                        'checked_in_at': datetime.now().isoformat()
                    }
                )
            except Exception as e:
                print(f"Warning: Failed to record event check-in to blockchain: {e}")
            
            return True, "Successfully checked in"
            
        except Exception as e:
            return False, f"Error checking in: {e}"
    
    def update_event_status(self, event_id: str, status: str, organizer_email: str) -> Tuple[bool, str]:
        """
        Update event status (scheduled, in_progress, completed, cancelled)
        
        Args:
            event_id: Event ID
            status: New status
            organizer_email: Email of organizer (for authorization)
            
        Returns:
            Tuple of (success, message)
        """
        try:
            valid_statuses = ['scheduled', 'in_progress', 'completed', 'cancelled']
            if status not in valid_statuses:
                return False, f"Invalid status. Must be one of: {', '.join(valid_statuses)}"
            
            data = self.load_data()
            event = None
            
            for e in data['events']:
                if e['id'] == event_id:
                    event = e
                    break
            
            if not event:
                return False, "Event not found"
            
            # Verify organizer
            if event['organizer_email'] != organizer_email:
                # Check if user has administrative role
                user = SessionManager.get_current_user()
                if not user or user.get('role') not in ['contract_elder', 'contract_founder']:
                    return False, "Only event organizer or administrators can update status"
            
            # Update status
            event['status'] = status
            event['updated_at'] = datetime.now().isoformat()
            
            self.save_data(data)
            
            # Record to blockchain
            try:
                add_user_action(
                    action_type='event_status_updated',
                    user_email=organizer_email,
                    data={
                        'event_id': event_id,
                        'event_title': event['title'],
                        'new_status': status
                    }
                )
            except Exception as e:
                print(f"Warning: Failed to record event status update to blockchain: {e}")
            
            return True, f"Event status updated to {status}"
            
        except Exception as e:
            return False, f"Error updating event status: {e}"


# Export main class
__all__ = ['EventManager']
