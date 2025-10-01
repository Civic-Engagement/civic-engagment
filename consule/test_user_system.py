#!/usr/bin/env python3
"""
USER SYSTEM TEST
Test script to verify user management functionality
"""

from user_manager import UserManager, UserValidator
from organization_manager import OrganizationManager
from blockchain_user_system import BlockchainUserSystem

def test_user_validation():
    """Test user validation functions"""
    print("🧪 Testing User Validation...")
    
    # Test email validation
    assert UserValidator.validate_email("test@example.com") == True
    assert UserValidator.validate_email("invalid-email") == False
    assert UserValidator.validate_email("user@domain.co.uk") == True
    
    # Test phone validation
    assert UserValidator.validate_phone("555-123-4567") == True
    assert UserValidator.validate_phone("15551234567") == True
    assert UserValidator.validate_phone("123") == False  # Too short
    
    # Test date of birth validation
    assert UserValidator.validate_date_of_birth("1990-05-15") == True
    assert UserValidator.validate_date_of_birth("invalid-date") == False
    assert UserValidator.validate_date_of_birth("2020-01-01") == False  # Too young
    
    # Test username validation
    assert UserValidator.validate_username("john_doe") == True
    assert UserValidator.validate_username("jd") == False  # Too short
    assert UserValidator.validate_username("john@doe") == False  # Invalid characters
    
    # Test name validation
    assert UserValidator.validate_name("John") == True
    assert UserValidator.validate_name("Mary-Jane") == True
    assert UserValidator.validate_name("O'Connor") == True
    assert UserValidator.validate_name("123") == False  # Numbers not allowed
    
    print("✅ User validation tests passed!")

def test_user_registration():
    """Test user registration"""
    print("\n🧪 Testing User Registration...")
    
    user_manager = UserManager("test_users.json")
    
    # Test registration data
    registration_data = {
        "username": "test_user_001",
        "password": "secure_password123",
        "legal_first_name": "John",
        "legal_middle_name": "Michael",
        "legal_last_name": "Doe",
        "date_of_birth": "1990-05-15",
        "email_addresses": [
            {"email": "john@example.com", "is_primary": True},
            {"email": "john.doe@work.com", "is_primary": False}
        ],
        "phone_numbers": [
            {"number": "555-123-4567", "type": "mobile", "is_primary": True},
            {"number": "555-987-6543", "type": "home", "is_primary": False}
        ],
        "addresses": [
            {
                "type": "residence",
                "street_address": "123 Main St",
                "city": "Springfield",
                "state_province": "IL",
                "postal_code": "62701",
                "country": "USA",
                "is_primary": True
            }
        ],
        "countries_of_citizenship": ["USA"]
    }
    
    # Test registration
    result = user_manager.register_user(registration_data)
    assert result["success"] == True
    user_id = result["user_id"]
    
    print(f"✅ User registered with ID: {user_id}")
    
    # Test authentication
    user = user_manager.authenticate_user("test_user_001", "secure_password123")
    assert user is not None
    assert user.username == "test_user_001"
    assert user.legal_first_name == "John"
    
    print("✅ User authentication successful!")
    
    # Test duplicate registration
    duplicate_result = user_manager.register_user(registration_data)
    assert duplicate_result["success"] == False
    assert "already exists" in str(duplicate_result["errors"])
    
    print("✅ Duplicate registration properly rejected!")
    
    return user_manager, user

def test_organization_management():
    """Test organization management"""
    print("\n🧪 Testing Organization Management...")
    
    org_manager = OrganizationManager("test_organizations.json")
    
    # Test organization creation
    org_data = {
        "name": "test_civic_org",
        "display_name": "Test Civic Organization",
        "description": "A test organization for civic engagement",
        "organization_type": "community",
        "website": "https://testcivic.org",
        "contact_email": "info@testcivic.org",
        "city": "Springfield",
        "state_province": "IL",
        "country": "USA",
        "is_public": True,
        "requires_approval": True
    }
    
    result = org_manager.create_organization("creator_user_id", org_data)
    assert result["success"] == True
    org_id = result["organization_id"]
    
    print(f"✅ Organization created with ID: {org_id}")
    
    # Test membership request
    membership_result = org_manager.request_membership(
        org_id,
        "test_user_id",
        "test_user",
        "Test User",
        "I want to contribute to civic engagement"
    )
    assert membership_result["success"] == True
    
    print("✅ Membership request successful!")
    
    # Test listing organizations
    public_orgs = org_manager.list_public_organizations()
    assert len(public_orgs) >= 1
    assert any(org["name"] == "test_civic_org" for org in public_orgs)
    
    print("✅ Organization listing working!")
    
    return org_manager

def test_blockchain_integration():
    """Test blockchain user integration"""
    print("\n🧪 Testing Blockchain Integration...")
    
    # Create integrated system
    system = BlockchainUserSystem(blockchain_port=8999)  # Use different port for testing
    
    # Start blockchain node
    node = system.start_blockchain_node("test-node")
    assert node is not None
    
    print("✅ Blockchain node started for testing!")
    
    # Test registration with blockchain logging
    registration_data = {
        "username": "blockchain_user",
        "password": "test_password",
        "legal_first_name": "Blockchain",
        "legal_last_name": "User",
        "date_of_birth": "1985-12-25",
        "email_addresses": [
            {"email": "blockchain@example.com", "is_primary": True}
        ]
    }
    
    result = system.register_user_with_blockchain(registration_data)
    assert result["success"] == True
    
    print("✅ User registration with blockchain logging successful!")
    
    # Test login with blockchain logging
    user = system.login_user_with_blockchain("blockchain_user", "test_password")
    assert user is not None
    
    print("✅ User login with blockchain logging successful!")
    
    # Check blockchain contains user actions
    history = system.get_blockchain_user_history(user.user_id)
    assert len(history) >= 2  # Should have registration and login
    
    print(f"✅ Blockchain history contains {len(history)} user actions!")
    
    # Stop blockchain node
    system.blockchain_node.stop()
    
    return system

def cleanup_test_files():
    """Clean up test files"""
    print("\n🧹 Cleaning up test files...")
    
    import os
    test_files = ["test_users.json", "test_organizations.json"]
    
    for file in test_files:
        if os.path.exists(file):
            os.remove(file)
            print(f"✅ Removed {file}")

def main():
    """Run all tests"""
    print("🔗 BLOCKCHAIN USER SYSTEM TESTS")
    print("=" * 50)
    
    try:
        # Run all tests
        test_user_validation()
        user_manager, user = test_user_registration()
        org_manager = test_organization_management()
        system = test_blockchain_integration()
        
        print("\n" + "=" * 50)
        print("🎉 ALL TESTS PASSED!")
        print("=" * 50)
        print("✅ User validation system working")
        print("✅ User registration system working")
        print("✅ Organization management working")
        print("✅ Blockchain integration working")
        print("\n🚀 User management system is ready for production!")
        
    except AssertionError as e:
        print(f"\n❌ TEST FAILED: {e}")
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
    finally:
        cleanup_test_files()

if __name__ == "__main__":
    main()