"""
Pytest configuration and fixtures for Civic Engagement Platform tests
Provides shared fixtures, test utilities, and configuration
"""

import pytest
import os
import sys
import json
import tempfile
import shutil
from pathlib import Path
from datetime import datetime
from typing import Dict, Any

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

# Test configuration
TEST_CONFIG = {
    'environment': 'test',
    'debug': True,
    'blockchain_auto_rollup': False,
    'db_paths': {
        'users_db_path': 'test_users_db.json',
        'blockchain_db_path': 'test_blockchain_db.json',
        'debates_db_path': 'test_debates_db.json',
        'moderation_db_path': 'test_moderation_db.json',
        'crypto_db_path': 'test_crypto_db.json',
    }
}


@pytest.fixture(scope='function')
def temp_dir():
    """Create a temporary directory for test files"""
    temp_path = tempfile.mkdtemp(prefix='civic_test_')
    yield temp_path
    # Cleanup
    if os.path.exists(temp_path):
        shutil.rmtree(temp_path)


@pytest.fixture(scope='function')
def test_user_data():
    """Provide sample user data for testing"""
    return {
        'email': 'test@civic.platform',
        'first_name': 'Test',
        'last_name': 'User',
        'city': 'Test City',
        'state': 'Test State',
        'country': 'Test Country',
        'password': 'TestPassword123!',
        'id_document_path': '/tmp/test_id.jpg'
    }


@pytest.fixture(scope='function')
def test_founder_data():
    """Provide sample founder data for testing"""
    return {
        'email': 'founder@civic.platform',
        'first_name': 'Founder',
        'last_name': 'User',
        'city': 'Founder City',
        'state': 'Founder State',
        'country': 'USA',
        'password': 'FounderPassword123!',
        'founder_key': 'test-founder-key-12345'
    }


@pytest.fixture(scope='function')
def test_debate_data():
    """Provide sample debate topic data for testing"""
    return {
        'title': 'Test Debate Topic',
        'description': 'This is a test debate topic for unit testing',
        'jurisdiction': 'local',
        'location': 'Test City',
        'category': 'policy'
    }


@pytest.fixture(scope='function')
def test_blockchain_page():
    """Provide sample blockchain page data"""
    return {
        'action_type': 'test_action',
        'user_email': 'test@civic.platform',
        'data': {
            'test_field': 'test_value',
            'timestamp': datetime.now().isoformat()
        }
    }


@pytest.fixture(scope='function')
def mock_user_backend(temp_dir, monkeypatch):
    """Create a mock UserBackend with temporary database"""
    from users.backend import UserBackend
    
    # Set up temporary database path
    test_db_path = os.path.join(temp_dir, 'test_users_db.json')
    
    # Create empty database
    with open(test_db_path, 'w') as f:
        json.dump({'users': []}, f)
    
    # Create UserBackend instance
    backend = UserBackend()
    backend.db_path = test_db_path
    
    yield backend
    
    # Cleanup is handled by temp_dir fixture


@pytest.fixture(scope='function')
def mock_blockchain(temp_dir, monkeypatch):
    """Create a mock Blockchain with temporary database"""
    from blockchain.blockchain import Blockchain
    
    test_db_path = os.path.join(temp_dir, 'test_blockchain_db.json')
    
    # Create empty blockchain
    initial_chain = {
        'pages': [],
        'chapters': [],
        'books': [],
        'parts': [],
        'series': []
    }
    
    with open(test_db_path, 'w') as f:
        json.dump(initial_chain, f)
    
    # Patch the database path
    original_load = Blockchain.load_chain
    
    def mock_load_chain():
        with open(test_db_path, 'r') as f:
            return json.load(f)
    
    monkeypatch.setattr(Blockchain, 'load_chain', mock_load_chain)
    
    yield Blockchain
    
    # Cleanup is handled by temp_dir fixture


@pytest.fixture(scope='function')
def crypto_test_wallet():
    """Provide sample crypto wallet data for testing"""
    return {
        'wallet_address': 'test_wallet_addr_12345',
        'balance': 100.0,
        'public_key': 'test_public_key',
        'created_at': datetime.now().isoformat()
    }


@pytest.fixture(scope='session')
def test_config():
    """Provide test configuration for all tests"""
    return TEST_CONFIG


# Pytest hooks for custom test behavior
def pytest_configure(config):
    """Configure pytest with custom settings"""
    config.addinivalue_line(
        "markers", "unit: mark test as a unit test"
    )
    config.addinivalue_line(
        "markers", "integration: mark test as an integration test"
    )


def pytest_collection_modifyitems(config, items):
    """Modify test collection to add markers automatically"""
    for item in items:
        # Auto-add markers based on test location
        if "integration" in str(item.fspath):
            item.add_marker(pytest.mark.integration)
        elif "unit" in str(item.fspath):
            item.add_marker(pytest.mark.unit)
        
        # Add module-specific markers
        if "blockchain" in str(item.fspath):
            item.add_marker(pytest.mark.blockchain)
        elif "users" in str(item.fspath):
            item.add_marker(pytest.mark.users)
        elif "debates" in str(item.fspath):
            item.add_marker(pytest.mark.debates)
        elif "crypto" in str(item.fspath):
            item.add_marker(pytest.mark.crypto)
