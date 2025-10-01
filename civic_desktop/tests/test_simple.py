"""
Simple Test Script for Core Platform Features
Tests basic functionality without requiring pytest
"""

import os
import sys
from pathlib import Path
from datetime import datetime, timedelta

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

print("=" * 60)
print("Testing Core Platform Features")
print("=" * 60)

def test_imports():
    """Test that all modules can be imported"""
    print("\n1. Testing module imports...")
    
    try:
        from events.event_manager import EventManager
        print("   ✓ EventManager imported successfully")
    except Exception as e:
        print(f"   ✗ Failed to import EventManager: {e}")
        return False
    
    try:
        from debates.backend import DebateBackend
        print("   ✓ DebateBackend imported successfully")
    except Exception as e:
        print(f"   ✗ Failed to import DebateBackend: {e}")
        return False
    
    try:
        from users.backend import UserBackend
        print("   ✓ UserBackend imported successfully")
    except Exception as e:
        print(f"   ✗ Failed to import UserBackend: {e}")
        return False
    
    try:
        from users.auth import SessionManager
        print("   ✓ SessionManager imported successfully")
    except Exception as e:
        print(f"   ✗ Failed to import SessionManager: {e}")
        return False
    
    return True

def test_event_manager():
    """Test EventManager functionality"""
    print("\n2. Testing EventManager...")
    
    try:
        from events.event_manager import EventManager
        
        # Test initialization
        em = EventManager()
        print("   ✓ EventManager initialized")
        
        # Test event types defined
        assert 'town_hall' in EventManager.EVENT_TYPES
        assert 'debate_forum' in EventManager.EVENT_TYPES
        print("   ✓ Event types properly defined")
        
        # Test database initialization
        em.ensure_database()
        assert os.path.exists(em.db_path)
        print("   ✓ Event database initialized")
        
        # Test loading data
        data = em.load_data()
        assert 'events' in data
        assert 'working_groups' in data
        print("   ✓ Event data loaded successfully")
        
        # Test listing events
        events = em.list_events()
        assert isinstance(events, list)
        print(f"   ✓ Event listing works (found {len(events)} events)")
        
        return True
        
    except Exception as e:
        print(f"   ✗ EventManager test failed: {e}")
        return False

def test_debate_backend():
    """Test DebateBackend functionality"""
    print("\n3. Testing DebateBackend...")
    
    try:
        from debates.backend import DebateBackend, DebateStatus, ArgumentType
        
        # Test initialization
        db = DebateBackend()
        print("   ✓ DebateBackend initialized")
        
        # Test constants
        assert hasattr(DebateStatus, 'PENDING')
        assert hasattr(DebateStatus, 'APPROVED')
        assert hasattr(ArgumentType, 'FOR')
        assert hasattr(ArgumentType, 'AGAINST')
        print("   ✓ Debate constants defined")
        
        # Test listing topics
        topics = db.list_topics()
        assert isinstance(topics, list)
        print(f"   ✓ Topic listing works (found {len(topics)} topics)")
        
        return True
        
    except Exception as e:
        print(f"   ✗ DebateBackend test failed: {e}")
        return False

def test_user_backend_enhancements():
    """Test UserBackend enhancements"""
    print("\n4. Testing UserBackend enhancements...")
    
    try:
        from users.backend import UserBackend
        
        # Test initialization
        ub = UserBackend()
        print("   ✓ UserBackend initialized")
        
        # Test update_user_profile method exists
        assert hasattr(ub, 'update_user_profile')
        assert callable(ub.update_user_profile)
        print("   ✓ update_user_profile method exists")
        
        return True
        
    except Exception as e:
        print(f"   ✗ UserBackend enhancement test failed: {e}")
        return False

def test_session_manager_enhancements():
    """Test SessionManager enhancements"""
    print("\n5. Testing SessionManager enhancements...")
    
    try:
        from users.auth import SessionManager
        
        # Test update_current_user method exists
        assert hasattr(SessionManager, 'update_current_user')
        assert callable(SessionManager.update_current_user)
        print("   ✓ update_current_user method exists")
        
        # Test with no session (should not error)
        SessionManager._current_session = None
        SessionManager.update_current_user({'first_name': 'Test'})
        print("   ✓ update_current_user handles no session gracefully")
        
        return True
        
    except Exception as e:
        print(f"   ✗ SessionManager enhancement test failed: {e}")
        return False

def test_ui_modules():
    """Test UI module imports"""
    print("\n6. Testing UI module imports...")
    
    ui_imports_success = True
    
    try:
        from events.calendar_ui import CalendarUI
        print("   ✓ CalendarUI imported successfully")
    except Exception as e:
        print(f"   ⚠ CalendarUI import warning: {e}")
        # UI imports may fail if PyQt5 not available, which is okay
    
    try:
        from debates.ui import DebateUI
        print("   ✓ DebateUI imported successfully")
    except Exception as e:
        print(f"   ⚠ DebateUI import warning: {e}")
    
    try:
        from users.profile_editor import ProfileEditDialog
        print("   ✓ ProfileEditDialog imported successfully")
    except Exception as e:
        print(f"   ⚠ ProfileEditDialog import warning: {e}")
    
    try:
        from users.participation_dashboard import ParticipationDashboard
        print("   ✓ ParticipationDashboard imported successfully")
    except Exception as e:
        print(f"   ⚠ ParticipationDashboard import warning: {e}")
    
    return True  # UI imports are optional if PyQt5 not available

def main():
    """Run all tests"""
    results = []
    
    results.append(("Module Imports", test_imports()))
    results.append(("EventManager", test_event_manager()))
    results.append(("DebateBackend", test_debate_backend()))
    results.append(("UserBackend Enhancements", test_user_backend_enhancements()))
    results.append(("SessionManager Enhancements", test_session_manager_enhancements()))
    results.append(("UI Modules", test_ui_modules()))
    
    print("\n" + "=" * 60)
    print("Test Results Summary")
    print("=" * 60)
    
    passed = 0
    failed = 0
    
    for test_name, result in results:
        status = "✓ PASSED" if result else "✗ FAILED"
        print(f"{test_name:.<40} {status}")
        if result:
            passed += 1
        else:
            failed += 1
    
    print("=" * 60)
    print(f"Total: {passed} passed, {failed} failed out of {len(results)} tests")
    print("=" * 60)
    
    return failed == 0

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
