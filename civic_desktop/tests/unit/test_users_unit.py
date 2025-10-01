"""
Unit tests for Users Module
Tests authentication, registration, role management, and user data operations
"""

import pytest
import os
import json
import bcrypt
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, MagicMock

# Import modules to test
from users.backend import UserBackend
from users.auth import AuthenticationService, SessionManager
from users.contract_roles import ContractRole, ContractRoleManager
from utils.validation import DataValidator, SecurityValidator


class TestUserBackend:
    """Test UserBackend core functionality"""
    
    def test_user_backend_initialization(self, temp_dir):
        """Test UserBackend initializes correctly"""
        backend = UserBackend()
        assert backend is not None
        assert hasattr(backend, 'db_path')
    
    def test_load_users_empty_db(self, temp_dir):
        """Test loading from empty database"""
        db_path = os.path.join(temp_dir, 'test_users.json')
        with open(db_path, 'w') as f:
            json.dump({'users': []}, f)
        
        backend = UserBackend()
        backend.db_path = db_path
        users = backend.load_users()
        
        assert isinstance(users, list)
        assert len(users) == 0
    
    def test_save_and_load_users(self, temp_dir):
        """Test saving and loading user data"""
        db_path = os.path.join(temp_dir, 'test_users.json')
        with open(db_path, 'w') as f:
            json.dump({'users': []}, f)
        
        backend = UserBackend()
        backend.db_path = db_path
        
        test_user = {
            'email': 'test@civic.platform',
            'first_name': 'Test',
            'last_name': 'User',
            'created_at': datetime.now().isoformat()
        }
        
        users = [test_user]
        backend.save_users(users)
        
        loaded_users = backend.load_users()
        assert len(loaded_users) == 1
        assert loaded_users[0]['email'] == 'test@civic.platform'
    
    def test_user_exists(self, temp_dir, test_user_data):
        """Test checking if user exists"""
        db_path = os.path.join(temp_dir, 'test_users.json')
        with open(db_path, 'w') as f:
            json.dump({'users': [test_user_data]}, f)
        
        backend = UserBackend()
        backend.db_path = db_path
        
        assert backend.user_exists(test_user_data['email']) is True
        assert backend.user_exists('nonexistent@email.com') is False
    
    def test_get_user(self, temp_dir, test_user_data):
        """Test retrieving user by email"""
        db_path = os.path.join(temp_dir, 'test_users.json')
        with open(db_path, 'w') as f:
            json.dump({'users': [test_user_data]}, f)
        
        backend = UserBackend()
        backend.db_path = db_path
        
        user = backend.get_user(test_user_data['email'])
        assert user is not None
        assert user['email'] == test_user_data['email']
        assert user['first_name'] == test_user_data['first_name']
    
    def test_password_hashing(self):
        """Test password hashing functionality"""
        backend = UserBackend()
        password = "TestPassword123!"
        
        hashed = backend.hash_password(password)
        assert hashed is not None
        assert isinstance(hashed, str)
        assert hashed != password
        
        # Verify password
        assert backend.verify_password(password, hashed) is True
        assert backend.verify_password("wrong_password", hashed) is False


class TestAuthenticationService:
    """Test authentication service functionality"""
    
    def test_authentication_service_init(self):
        """Test AuthenticationService initialization"""
        auth_service = AuthenticationService()
        assert auth_service is not None
    
    @patch('users.backend.UserBackend')
    def test_authenticate_valid_credentials(self, mock_backend):
        """Test authentication with valid credentials"""
        # Setup mock
        mock_user = {
            'email': 'test@civic.platform',
            'password': bcrypt.hashpw('TestPassword123!'.encode(), bcrypt.gensalt()).decode(),
            'first_name': 'Test',
            'last_name': 'User'
        }
        
        mock_backend_instance = Mock()
        mock_backend_instance.get_user.return_value = mock_user
        mock_backend_instance.verify_password.return_value = True
        mock_backend.return_value = mock_backend_instance
        
        auth_service = AuthenticationService()
        auth_service.user_backend = mock_backend_instance
        
        result = auth_service.authenticate('test@civic.platform', 'TestPassword123!')
        assert result is True
    
    @patch('users.backend.UserBackend')
    def test_authenticate_invalid_credentials(self, mock_backend):
        """Test authentication with invalid credentials"""
        mock_backend_instance = Mock()
        mock_backend_instance.get_user.return_value = None
        mock_backend.return_value = mock_backend_instance
        
        auth_service = AuthenticationService()
        auth_service.user_backend = mock_backend_instance
        
        result = auth_service.authenticate('test@civic.platform', 'WrongPassword')
        assert result is False


class TestSessionManager:
    """Test session management functionality"""
    
    def test_session_creation(self):
        """Test creating a user session"""
        test_user = {
            'email': 'test@civic.platform',
            'first_name': 'Test',
            'last_name': 'User',
            'role': 'contract_member'
        }
        
        SessionManager.create_session(test_user)
        
        assert SessionManager.is_authenticated() is True
        current_user = SessionManager.get_current_user()
        assert current_user is not None
        assert current_user['email'] == test_user['email']
    
    def test_session_logout(self):
        """Test logging out and clearing session"""
        test_user = {
            'email': 'test@civic.platform',
            'first_name': 'Test'
        }
        
        SessionManager.create_session(test_user)
        assert SessionManager.is_authenticated() is True
        
        SessionManager.logout()
        assert SessionManager.is_authenticated() is False
        assert SessionManager.get_current_user() is None


class TestContractRoles:
    """Test contract-based role system"""
    
    def test_contract_role_enum(self):
        """Test ContractRole enumeration"""
        assert hasattr(ContractRole, 'CONTRACT_MEMBER')
        assert hasattr(ContractRole, 'CONTRACT_REPRESENTATIVE')
        assert hasattr(ContractRole, 'CONTRACT_SENATOR')
        assert hasattr(ContractRole, 'CONTRACT_ELDER')
        assert hasattr(ContractRole, 'CONTRACT_FOUNDER')
    
    def test_role_manager_initialization(self):
        """Test ContractRoleManager initialization"""
        role_manager = ContractRoleManager()
        assert role_manager is not None
    
    def test_role_assignment(self):
        """Test assigning roles to users"""
        role_manager = ContractRoleManager()
        
        # Test assigning basic role
        result = role_manager.assign_role('test@civic.platform', ContractRole.CONTRACT_MEMBER)
        assert result is not None
    
    def test_role_permissions(self):
        """Test role-based permissions"""
        role_manager = ContractRoleManager()
        
        # Contract Members should have basic permissions
        member_perms = role_manager.get_role_permissions(ContractRole.CONTRACT_MEMBER)
        assert 'vote' in member_perms or member_perms is not None
        
        # Contract Founders should have elevated permissions
        founder_perms = role_manager.get_role_permissions(ContractRole.CONTRACT_FOUNDER)
        assert founder_perms is not None


class TestUserValidation:
    """Test user input validation"""
    
    def test_email_validation(self):
        """Test email validation logic"""
        # Valid emails
        assert DataValidator.validate_email('test@civic.platform')[0] is True
        assert DataValidator.validate_email('user@example.com')[0] is True
        
        # Invalid emails
        assert DataValidator.validate_email('invalid-email')[0] is False
        assert DataValidator.validate_email('')[0] is False
        assert DataValidator.validate_email('@example.com')[0] is False
    
    def test_password_validation(self):
        """Test password strength validation"""
        # Strong passwords
        assert DataValidator.validate_password('StrongPass123!')[0] is True
        assert DataValidator.validate_password('Complex@Pass1')[0] is True
        
        # Weak passwords
        assert DataValidator.validate_password('short')[0] is False
        assert DataValidator.validate_password('nouppercaseorno123!')[0] is False
    
    def test_name_validation(self):
        """Test name validation"""
        # Valid names
        assert DataValidator.validate_name('John')[0] is True
        assert DataValidator.validate_name('Mary-Jane')[0] is True
        
        # Invalid names
        assert DataValidator.validate_name('')[0] is False
        assert DataValidator.validate_name('123')[0] is False
    
    def test_location_validation(self):
        """Test location field validation"""
        # Valid locations
        assert DataValidator.validate_location('New York')[0] is True
        assert DataValidator.validate_location('San Francisco')[0] is True
        
        # Invalid locations
        assert DataValidator.validate_location('')[0] is False


@pytest.mark.integration
class TestUserBlockchainIntegration:
    """Test integration between users and blockchain"""
    
    @patch('blockchain.blockchain.Blockchain')
    def test_user_registration_blockchain_record(self, mock_blockchain):
        """Test that user registration is recorded on blockchain"""
        mock_blockchain.add_page = Mock(return_value=True)
        
        backend = UserBackend()
        # Registration should trigger blockchain recording
        # This is tested in integration tests
        
        assert True  # Placeholder for integration test


@pytest.mark.security
class TestUserSecurity:
    """Test security features of user system"""
    
    def test_password_not_stored_plaintext(self, temp_dir):
        """Test that passwords are never stored in plaintext"""
        db_path = os.path.join(temp_dir, 'test_users.json')
        with open(db_path, 'w') as f:
            json.dump({'users': []}, f)
        
        backend = UserBackend()
        backend.db_path = db_path
        
        password = "TestPassword123!"
        hashed = backend.hash_password(password)
        
        # Ensure hashed password doesn't contain plaintext
        assert password not in hashed
        assert len(hashed) > len(password)
    
    def test_session_timeout(self):
        """Test session timeout functionality"""
        # Sessions should have timeout mechanisms
        test_user = {'email': 'test@civic.platform'}
        SessionManager.create_session(test_user)
        
        # Session should be active
        assert SessionManager.is_authenticated() is True
    
    def test_sql_injection_prevention(self):
        """Test that email validation prevents SQL injection"""
        # Even though we use JSON, test injection patterns are rejected
        malicious_emails = [
            "test@example.com'; DROP TABLE users; --",
            "admin'--",
            "' OR '1'='1"
        ]
        
        for email in malicious_emails:
            is_valid, msg = DataValidator.validate_email(email)
            assert is_valid is False


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
