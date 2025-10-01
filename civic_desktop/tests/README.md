# Civic Engagement Platform - Test Suite

This directory contains all test files organized by module and functionality.

## Directory Structure

### `/tests/unit/`
Comprehensive unit tests for individual modules:
- `test_users_unit.py` - Users module: authentication, registration, roles, security (30+ tests)
- `test_blockchain_unit.py` - Blockchain module: pages, integrity, consensus, security (25+ tests)
- `test_debates_moderation_unit.py` - Debates and Moderation: topics, flagging, review (20+ tests)
- `test_crypto_unit.py` - Crypto module: transactions, wallets, DeFi, security (25+ tests)
- `test_validation_unit.py` - Validation utilities: input validation, security (23+ tests)

### `/tests/integration/`
Cross-module integration tests and complete workflows:
- `test_workflows.py` - Integration tests for user registration, debates, moderation, crypto, elections (20+ tests)

### `/tests/blockchain/`
Legacy blockchain system tests and demonstrations:
- `demo_simple.py` - Basic blockchain functionality demonstration
- `demo_complete_integration.py` - Complete user-blockchain integration demo
- `test_blockchain_demo.py` - Blockchain unit tests
- `test_integration.py` - Blockchain integration tests

### `/tests/users/`
Legacy user management system tests:
- `test_users_demo.py` - User registration, authentication, and key management tests
- `test_integration.py` - User-blockchain integration tests

### Configuration Files
- `conftest.py` - Shared pytest fixtures and test utilities
- `../pytest.ini` - Pytest configuration with markers and settings

## Running Tests

From the `civic_desktop/` directory:

```bash
# Run all tests
python -m pytest tests/ -v

# Run unit tests only
python -m pytest tests/unit/ -v

# Run integration tests only
python -m pytest tests/integration/ -v

# Run specific test file
python -m pytest tests/unit/test_users_unit.py -v

# Run tests with specific marker
python -m pytest -m security -v
python -m pytest -m blockchain -v

# Run with coverage reporting
python -m pytest tests/ --cov=. --cov-report=html

# Run specific test class or method
python -m pytest tests/unit/test_users_unit.py::TestUserBackend -v
python -m pytest tests/unit/test_users_unit.py::TestUserBackend::test_password_hashing -v
```

## Test Coverage

### ✅ Implemented Tests (New Comprehensive Suite)
**Unit Tests:**
- Users module: authentication, registration, roles, session management (30+ tests)
- Blockchain: pages, chapters, integrity, consensus, security (25+ tests)
- Debates & Moderation: topics, arguments, flagging, review workflows (20+ tests)
- Crypto system: CivicCoin, wallets, transactions, DeFi, rewards (25+ tests)
- Validation: input validation, security checks, edge cases (23+ tests)

**Integration Tests:**
- Complete user registration workflow with blockchain and crypto
- Debate participation and moderation workflows
- Cross-module data consistency and security
- Election processes and role assignments (20+ tests)

**Total:** 140+ test methods covering critical functionality

### ✅ Legacy Tests (Existing Demonstrations)
- Blockchain core functionality (Pages → Chapters → Books hierarchy)
- Constitutional governance framework
- User registration with blockchain integration
- Cryptographic signing and validation
- Proof of Authority consensus
- User-blockchain data flow

### 🔧 Future Test Expansion
- Analytics and reporting module tests
- Events and calendar module tests
- Communications module tests
- Surveys and polling module tests
- Petitions module tests
- Documents and transparency module tests
- Collaboration module tests
- Additional end-to-end workflow tests
- Performance and load testing
- UI/UX automated testing

## Test Data

All tests use isolated test data and do not affect production databases. Each test creates temporary data structures for validation.

## Dependencies

Tests require the same dependencies as the main application:
- PyQt5 (for UI components)
- cryptography (for RSA operations)
- bcrypt (for password hashing)
- Additional dependencies as specified in `requirements.txt`