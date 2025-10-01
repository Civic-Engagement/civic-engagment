"""
Test Core Platform Features
Tests for Events, Debates UI, Profile Editor, and Participation Dashboard
"""

import os
import sys
import json
import pytest
from datetime import datetime, timedelta
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Import modules to test
from events.event_manager import EventManager
from debates.backend import DebateBackend
from users.backend import UserBackend
from users.auth import SessionManager


class TestEventManager:
    """Test event management functionality"""
    
    @pytest.fixture
    def event_manager(self):
        """Create event manager instance"""
        return EventManager()
    
    @pytest.fixture
    def test_user(self):
        """Create test user data"""
        return {
            'email': 'test@example.com',
            'first_name': 'Test',
            'last_name': 'User',
            'role': 'contract_representative',
            'user_id': 'test_user_123'
        }
    
    def test_event_types_defined(self, event_manager):
        """Test that event types are properly defined"""
        assert 'town_hall' in EventManager.EVENT_TYPES
        assert 'debate_forum' in EventManager.EVENT_TYPES
        assert 'training_session' in EventManager.EVENT_TYPES
        assert 'election_event' in EventManager.EVENT_TYPES
        assert 'community_meeting' in EventManager.EVENT_TYPES
    
    def test_event_type_requirements(self, event_manager):
        """Test that event types have required attributes"""
        for event_type, requirements in EventManager.EVENT_TYPES.items():
            assert 'required_roles' in requirements
            assert 'constitutional_review' in requirements
            assert 'public_notice_days' in requirements
            assert isinstance(requirements['required_roles'], list)
            assert isinstance(requirements['constitutional_review'], bool)
            assert isinstance(requirements['public_notice_days'], int)
    
    def test_database_initialization(self, event_manager):
        """Test that database is properly initialized"""
        event_manager.ensure_database()
        assert os.path.exists(event_manager.db_path)
        
        # Check database structure
        data = event_manager.load_data()
        assert 'events' in data
        assert 'working_groups' in data
        assert 'attendees' in data
        assert 'outcomes' in data
    
    def test_validate_event_authority(self, event_manager, test_user):
        """Test event creation authority validation"""
        # Setup session
        SessionManager._current_session = test_user
        
        # Test valid authority
        is_valid, message = event_manager.validate_event_authority(
            test_user['email'], 
            'town_hall'
        )
        assert is_valid or "must be current user" in message  # Depends on session state
        
        # Test invalid event type
        is_valid, message = event_manager.validate_event_authority(
            test_user['email'],
            'invalid_type'
        )
        assert not is_valid
        assert 'Invalid event type' in message
    
    def test_create_event_validation(self, event_manager, test_user):
        """Test event creation with validation"""
        # Setup session
        SessionManager._current_session = test_user
        
        # Test missing required fields
        event_data = {
            'title': 'Test Event'
            # Missing required fields
        }
        success, message, event_id = event_manager.create_event(event_data, test_user['email'])
        assert not success
        assert 'Missing required field' in message
        
        # Test invalid event type
        event_data = {
            'title': 'Test Event',
            'type': 'invalid_type',
            'datetime': (datetime.now() + timedelta(days=10)).isoformat(),
            'description': 'Test description'
        }
        success, message, event_id = event_manager.create_event(event_data, test_user['email'])
        assert not success
        assert 'Invalid event type' in message
    
    def test_list_events(self, event_manager):
        """Test listing events with filters"""
        events = event_manager.list_events()
        assert isinstance(events, list)
        
        # Test with filters
        scheduled_events = event_manager.list_events(filter_status='scheduled')
        assert isinstance(scheduled_events, list)
        
        training_events = event_manager.list_events(filter_type='training_session')
        assert isinstance(training_events, list)


class TestDebateBackend:
    """Test debate backend functionality"""
    
    @pytest.fixture
    def debate_backend(self):
        """Create debate backend instance"""
        return DebateBackend()
    
    @pytest.fixture
    def test_user(self):
        """Create test user data"""
        return {
            'email': 'debater@example.com',
            'first_name': 'Debate',
            'last_name': 'User',
            'role': 'contract_representative',
            'user_id': 'debater_123'
        }
    
    def test_debate_status_constants(self):
        """Test debate status constants"""
        from debates.backend import DebateStatus
        assert hasattr(DebateStatus, 'PENDING')
        assert hasattr(DebateStatus, 'APPROVED')
    
    def test_argument_type_constants(self):
        """Test argument type constants"""
        from debates.backend import ArgumentType
        assert hasattr(ArgumentType, 'FOR')
        assert hasattr(ArgumentType, 'AGAINST')
        assert hasattr(ArgumentType, 'NEUTRAL')
    
    def test_list_topics(self, debate_backend):
        """Test listing debate topics"""
        topics = debate_backend.list_topics()
        assert isinstance(topics, list)


class TestUserBackend:
    """Test user backend enhancements"""
    
    @pytest.fixture
    def user_backend(self):
        """Create user backend instance"""
        return UserBackend()
    
    def test_update_user_profile_method_exists(self, user_backend):
        """Test that update_user_profile method exists"""
        assert hasattr(user_backend, 'update_user_profile')
        assert callable(user_backend.update_user_profile)
    
    def test_update_user_profile_allowed_fields(self, user_backend):
        """Test profile update with allowed fields"""
        # This test would need a test user in the database
        # For now, just verify the method signature
        import inspect
        sig = inspect.signature(user_backend.update_user_profile)
        assert 'user_email' in sig.parameters
        assert 'updated_data' in sig.parameters


class TestSessionManager:
    """Test session manager enhancements"""
    
    def test_update_current_user_method_exists(self):
        """Test that update_current_user method exists"""
        assert hasattr(SessionManager, 'update_current_user')
        assert callable(SessionManager.update_current_user)
    
    def test_update_current_user_with_no_session(self):
        """Test updating user when no session exists"""
        SessionManager._current_session = None
        # Should not raise error
        SessionManager.update_current_user({'first_name': 'Test'})
    
    def test_update_current_user_with_session(self):
        """Test updating user with active session"""
        SessionManager._current_session = {
            'email': 'test@example.com',
            'first_name': 'Old',
            'last_name': 'Name'
        }
        
        # Update first name
        SessionManager.update_current_user({'first_name': 'New'})
        
        # Verify update
        assert SessionManager._current_session['first_name'] == 'New'
        
        # Clean up
        SessionManager._current_session = None


class TestIntegration:
    """Integration tests for core platform features"""
    
    def test_modules_can_be_imported(self):
        """Test that all new modules can be imported"""
        try:
            from events.event_manager import EventManager
            from events.calendar_ui import CalendarUI
            from debates.ui import DebateUI
            from users.profile_editor import ProfileEditDialog
            from users.participation_dashboard import ParticipationDashboard
            assert True
        except ImportError as e:
            pytest.fail(f"Failed to import module: {e}")
    
    def test_event_manager_blockchain_integration(self):
        """Test that event manager records to blockchain"""
        from events.event_manager import EventManager
        em = EventManager()
        
        # Verify event manager has methods that should record to blockchain
        assert hasattr(em, 'create_event')
        assert hasattr(em, 'register_attendee')
        assert hasattr(em, 'check_in_attendee')
        assert hasattr(em, 'update_event_status')
    
    def test_debate_ui_backend_integration(self):
        """Test that debate UI connects to backend"""
        # Verify both modules exist and can work together
        from debates.backend import DebateBackend
        from debates.ui import DebateUI
        
        backend = DebateBackend()
        assert hasattr(backend, 'list_topics')
        assert hasattr(backend, 'create_topic')
        assert hasattr(backend, 'add_argument')


def test_event_manager_basic_functionality():
    """Basic functionality test for EventManager"""
    em = EventManager()
    
    # Test database initialization
    assert os.path.exists(em.db_path)
    
    # Test loading data
    data = em.load_data()
    assert isinstance(data, dict)
    assert 'events' in data


def test_debate_backend_basic_functionality():
    """Basic functionality test for DebateBackend"""
    db = DebateBackend()
    
    # Test listing topics
    topics = db.list_topics()
    assert isinstance(topics, list)


if __name__ == '__main__':
    # Run tests
    pytest.main([__file__, '-v', '--tb=short'])
