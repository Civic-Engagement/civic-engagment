#!/usr/bin/env python3
"""
USER MANAGEMENT SYSTEM
Comprehensive user registration and management for blockchain platform
"""

import json
import hashlib
import uuid
import re
import base64
from datetime import datetime, date
from typclass UserManager:
    """Manages user registration, authentication, and profiles"""
    
    def __init__(self, blockchain=None):
        self.blockchain = blockchain
        self.users: Dict[str, User] = {}
        self.username_to_id: Dict[str, str] = {}
        self.email_to_id: Dict[str, str] = {}
        if blockchain:
            self.load_users_from_blockchain()t Dict, List, Optional, Any
from dataclasses import dataclass, asdict, field
from enum import Enum

# Try to import cryptography, use fallback if not available
try:
    from cryptography.hazmat.primitives.asymmetric import rsa
    from cryptography.hazmat.primitives import serialization
    from cryptography.hazmat.backends import default_backend
    CRYPTOGRAPHY_AVAILABLE = True
except ImportError:
    CRYPTOGRAPHY_AVAILABLE = False
    print("⚠️ cryptography library not installed. Using simple key generation fallback.")

class PhoneType(Enum):
    HOME = "home"
    MOBILE = "mobile"
    WORK = "work"
    FAX = "fax"
    OTHER = "other"

class AddressType(Enum):
    RESIDENCE = "residence"
    MAILING = "mailing"
    WORK = "work"
    OTHER = "other"

@dataclass
class Address:
    """Complete address information"""
    address_type: AddressType
    street_address: str
    street_address_2: str = ""
    city: str = ""
    state_province: str = ""
    postal_code: str = ""
    country: str = ""
    is_primary: bool = False
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    
    def to_dict(self) -> Dict:
        result = asdict(self)
        result['address_type'] = self.address_type.value
        return result
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'Address':
        data['address_type'] = AddressType(data['address_type'])
        return cls(**data)

@dataclass
class PhoneNumber:
    """Phone number with type and verification status"""
    number: str
    phone_type: PhoneType
    country_code: str = "+1"
    is_primary: bool = False
    is_verified: bool = False
    verification_code: Optional[str] = None
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    verified_at: Optional[str] = None
    
    def to_dict(self) -> Dict:
        result = asdict(self)
        result['phone_type'] = self.phone_type.value
        return result
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'PhoneNumber':
        data['phone_type'] = PhoneType(data['phone_type'])
        return cls(**data)

@dataclass
class EmailAddress:
    """Email address with verification status"""
    email: str
    is_primary: bool = False
    is_verified: bool = False
    verification_token: Optional[str] = None
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    verified_at: Optional[str] = None
    
    def to_dict(self) -> Dict:
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'EmailAddress':
        return cls(**data)

@dataclass
class OrganizationRequest:
    """Request to join an organization"""
    organization_id: str
    organization_name: str
    request_reason: str
    status: str = "pending"  # pending, approved, denied
    requested_at: str = field(default_factory=lambda: datetime.now().isoformat())
    processed_at: Optional[str] = None
    processed_by: Optional[str] = None
    admin_notes: str = ""
    
    def to_dict(self) -> Dict:
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'OrganizationRequest':
        return cls(**data)

@dataclass
class User:
    """Complete user profile with all required information"""
    # Core Identity
    user_id: str
    username: str
    password_hash: str
    
    # Legal Identity (Required)
    legal_first_name: str
    legal_last_name: str
    date_of_birth: str  # YYYY-MM-DD format
    
    # Legal Identity (Optional)
    legal_middle_name: str = ""
    
    # Cryptographic Keys (Required)
    public_key_pem: str = ""
    private_key_pem: str = ""
    
    # Contact Information (Required - at least one email and phone)
    email_addresses: List[EmailAddress] = field(default_factory=list)
    phone_numbers: List[PhoneNumber] = field(default_factory=list)
    
    # Location Information (Optional but encouraged)
    addresses: List[Address] = field(default_factory=list)
    countries_of_citizenship: List[str] = field(default_factory=list)
    
    # Organization Requests
    organization_requests: List[OrganizationRequest] = field(default_factory=list)
    
    # Account Status
    is_active: bool = True
    is_verified: bool = False
    verification_level: str = "basic"  # basic, identity_verified, fully_verified
    
    # Metadata
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    updated_at: str = field(default_factory=lambda: datetime.now().isoformat())
    last_login: Optional[str] = None
    
    def to_dict(self) -> Dict:
        """Convert user to dictionary for storage"""
        result = asdict(self)
        result['email_addresses'] = [email.to_dict() for email in self.email_addresses]
        result['phone_numbers'] = [phone.to_dict() for phone in self.phone_numbers]
        result['addresses'] = [addr.to_dict() for addr in self.addresses]
        result['organization_requests'] = [req.to_dict() for req in self.organization_requests]
        return result
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'User':
        """Create user from dictionary"""
        # Convert nested objects
        data['email_addresses'] = [EmailAddress.from_dict(email) for email in data.get('email_addresses', [])]
        data['phone_numbers'] = [PhoneNumber.from_dict(phone) for phone in data.get('phone_numbers', [])]
        data['addresses'] = [Address.from_dict(addr) for addr in data.get('addresses', [])]
        data['organization_requests'] = [OrganizationRequest.from_dict(req) for req in data.get('organization_requests', [])]
        
        return cls(**data)
    
    def get_primary_email(self) -> Optional[EmailAddress]:
        """Get primary email address"""
        for email in self.email_addresses:
            if email.is_primary:
                return email
        return self.email_addresses[0] if self.email_addresses else None
    
    def get_primary_phone(self) -> Optional[PhoneNumber]:
        """Get primary phone number"""
        for phone in self.phone_numbers:
            if phone.is_primary:
                return phone
        return self.phone_numbers[0] if self.phone_numbers else None
    
    def get_primary_address(self) -> Optional[Address]:
        """Get primary address"""
        for address in self.addresses:
            if address.is_primary:
                return address
        return self.addresses[0] if self.addresses else None

class UserValidator:
    """Validation utilities for user data"""
    
    @staticmethod
    def validate_email(email: str) -> bool:
        """Validate email format"""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None
    
    @staticmethod
    def validate_phone(phone: str) -> bool:
        """Validate phone number format (basic validation)"""
        # Remove all non-digit characters
        digits_only = re.sub(r'[^\d]', '', phone)
        # Should have 10-15 digits
        return 10 <= len(digits_only) <= 15
    
    @staticmethod
    def validate_date_of_birth(dob: str) -> bool:
        """Validate date of birth format and reasonableness"""
        try:
            birth_date = datetime.strptime(dob, '%Y-%m-%d').date()
            today = date.today()
            age = today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))
            # Must be at least 13 years old and less than 150 years old
            return 13 <= age <= 150
        except ValueError:
            return False
    
    @staticmethod
    def validate_username(username: str) -> bool:
        """Validate username format"""
        # 3-30 characters, alphanumeric and underscores only
        pattern = r'^[a-zA-Z0-9_]{3,30}$'
        return re.match(pattern, username) is not None
    
    @staticmethod
    def validate_name(name: str) -> bool:
        """Validate name format"""
        # 1-50 characters, letters, spaces, hyphens, apostrophes
        pattern = r"^[a-zA-Z\s\-']{1,50}$"
        return re.match(pattern, name) is not None

class UserManager:
    """Manages user registration, authentication, and data"""
    
    def __init__(self, data_file: str = "users.json"):
        self.data_file = data_file
        self.users: Dict[str, User] = {}
        self.username_to_id: Dict[str, str] = {}
        self.email_to_id: Dict[str, str] = {}
        self.load_users()
    
    def load_users_from_blockchain(self):
        """Load users from blockchain blocks"""
        if not self.blockchain:
            return
        
        for block in self.blockchain.chain:
            if block.data.get('type') == 'USER_REGISTRATION':
                user_data = block.data.get('user_data', {})
                if user_data:
                    try:
                        user = User.from_dict(user_data)
                        self.users[user.user_id] = user
                        self.username_to_id[user.username] = user.user_id
                        
                        # Index all email addresses
                        for email in user.email_addresses:
                            self.email_to_id[email.email] = user.user_id
                    except Exception as e:
                        print(f"⚠️ Error loading user from blockchain: {e}")
    
    def save_user_to_blockchain(self, user: User, creator_authority_id: str = "GENESIS_AUTH") -> bool:
        """Save user to blockchain instead of file"""
        if not self.blockchain:
            print("❌ No blockchain available for user storage")
            return False
        
        blockchain_data = {
            "type": "USER_REGISTRATION",
            "user_id": user.user_id,
            "username": user.username,
            "user_data": user.to_dict(),
            "registration_timestamp": datetime.now().isoformat()
        }
        
        return self.blockchain.create_block(blockchain_data, creator_authority_id)
    
    def hash_password(self, password: str) -> str:
        """Hash password securely"""
        return hashlib.sha256(password.encode()).hexdigest()
    
    def generate_key_pair(self) -> tuple[str, str]:
        """Generate RSA public/private key pair"""
        if CRYPTOGRAPHY_AVAILABLE:
            try:
                # Generate private key
                private_key = rsa.generate_private_key(
                    public_exponent=65537,
                    key_size=2048,
                    backend=default_backend()
                )
                
                # Get public key
                public_key = private_key.public_key()
                
                # Serialize private key
                private_pem = private_key.private_bytes(
                    encoding=serialization.Encoding.PEM,
                    format=serialization.PrivateFormat.PKCS8,
                    encryption_algorithm=serialization.NoEncryption()
                ).decode('utf-8')
                
                # Serialize public key
                public_pem = public_key.public_bytes(
                    encoding=serialization.Encoding.PEM,
                    format=serialization.PublicFormat.SubjectPublicKeyInfo
                ).decode('utf-8')
                
                return public_pem, private_pem
            except Exception as e:
                print(f"Error generating RSA keys: {e}")
                return self._generate_fallback_keys()
        else:
            return self._generate_fallback_keys()
    
    def _generate_fallback_keys(self) -> tuple[str, str]:
        """Generate simple fallback keys when cryptography is not available"""
        user_id = str(uuid.uuid4())
        timestamp = str(datetime.now().timestamp())
        
        # Simple key generation using hash
        private_key_data = hashlib.sha256((user_id + timestamp + "private").encode()).hexdigest()
        public_key_data = hashlib.sha256((user_id + timestamp + "public").encode()).hexdigest()
        
        # Format as PEM-like strings
        private_pem = f"-----BEGIN SIMPLE PRIVATE KEY-----\n{private_key_data}\n-----END SIMPLE PRIVATE KEY-----"
        public_pem = f"-----BEGIN SIMPLE PUBLIC KEY-----\n{public_key_data}\n-----END SIMPLE PUBLIC KEY-----"
        
        return public_pem, private_pem
    
    def register_user(self, registration_data: Dict) -> Dict[str, Any]:
        """Register a new user with comprehensive validation"""
        errors = []
        
        # Required fields validation
        required_fields = ['username', 'password', 'legal_first_name', 'legal_last_name', 'date_of_birth']
        for field in required_fields:
            if not registration_data.get(field):
                errors.append(f"{field} is required")
        
        # At least one email is required
        if not registration_data.get('email_addresses'):
            errors.append("At least one email address is required")
        
        # At least one phone number is required
        if not registration_data.get('phone_numbers'):
            errors.append("At least one phone number is required")
        
        # At least one residence address is required
        addresses = registration_data.get('addresses', [])
        has_residence = any(addr.get('type') == 'residence' for addr in addresses)
        if not has_residence:
            errors.append("At least one residence address is required")
        
        if errors:
            return {"success": False, "errors": errors}
        
        # Validate individual fields
        username = registration_data['username']
        if not UserValidator.validate_username(username):
            errors.append("Username must be 3-30 characters, alphanumeric and underscores only")
        
        if username in self.username_to_id:
            errors.append("Username already exists")
        
        if not UserValidator.validate_name(registration_data['legal_first_name']):
            errors.append("Invalid first name format")
        
        if not UserValidator.validate_name(registration_data['legal_last_name']):
            errors.append("Invalid last name format")
        
        if registration_data.get('legal_middle_name') and not UserValidator.validate_name(registration_data['legal_middle_name']):
            errors.append("Invalid middle name format")
        
        if not UserValidator.validate_date_of_birth(registration_data['date_of_birth']):
            errors.append("Invalid date of birth (must be YYYY-MM-DD format and reasonable age)")
        
        # Validate email addresses
        email_addresses = []
        for i, email_data in enumerate(registration_data['email_addresses']):
            email = email_data.get('email', '').lower()
            if not UserValidator.validate_email(email):
                errors.append(f"Invalid email format: {email}")
                continue
            
            if email in self.email_to_id:
                errors.append(f"Email already registered: {email}")
                continue
            
            email_addresses.append(EmailAddress(
                email=email,
                is_primary=email_data.get('is_primary', i == 0),
                verification_token=str(uuid.uuid4())
            ))
        
        # Validate phone numbers
        phone_numbers = []
        for phone_data in registration_data.get('phone_numbers', []):
            phone = phone_data.get('number', '')
            if phone and not UserValidator.validate_phone(phone):
                errors.append(f"Invalid phone number format: {phone}")
                continue
            
            if phone:
                try:
                    phone_type = PhoneType(phone_data.get('type', 'mobile'))
                except ValueError:
                    errors.append(f"Invalid phone type: {phone_data.get('type')}")
                    continue
                
                phone_numbers.append(PhoneNumber(
                    number=phone,
                    phone_type=phone_type,
                    country_code=phone_data.get('country_code', '+1'),
                    is_primary=phone_data.get('is_primary', len(phone_numbers) == 0),
                    verification_code=str(uuid.uuid4())[:6]
                ))
        
        # Validate addresses
        addresses = []
        for addr_data in registration_data.get('addresses', []):
            if not addr_data.get('street_address'):
                continue
            
            try:
                addr_type = AddressType(addr_data.get('type', 'residence'))
            except ValueError:
                errors.append(f"Invalid address type: {addr_data.get('type')}")
                continue
            
            addresses.append(Address(
                address_type=addr_type,
                street_address=addr_data['street_address'],
                street_address_2=addr_data.get('street_address_2', ''),
                city=addr_data.get('city', ''),
                state_province=addr_data.get('state_province', ''),
                postal_code=addr_data.get('postal_code', ''),
                country=addr_data.get('country', ''),
                is_primary=addr_data.get('is_primary', len(addresses) == 0)
            ))
        
        if errors:
            return {"success": False, "errors": errors}
        
        # Generate cryptographic keys
        public_key, private_key = self.generate_key_pair()
        
        # Create user
        user_id = str(uuid.uuid4())
        user = User(
            user_id=user_id,
            username=username,
            password_hash=self.hash_password(registration_data['password']),
            legal_first_name=registration_data['legal_first_name'],
            legal_middle_name=registration_data.get('legal_middle_name', ''),
            legal_last_name=registration_data['legal_last_name'],
            date_of_birth=registration_data['date_of_birth'],
            public_key_pem=public_key,
            private_key_pem=private_key,
            email_addresses=email_addresses,
            phone_numbers=phone_numbers,
            addresses=addresses,
            countries_of_citizenship=registration_data.get('countries_of_citizenship', [])
        )
        
        # Store user
        self.users[user_id] = user
        self.username_to_id[username] = user_id
        
        # Index email addresses
        for email in email_addresses:
            self.email_to_id[email.email] = user_id
        
        self.save_users()
        
        return {
            "success": True,
            "user_id": user_id,
            "message": "User registered successfully. Please verify your email address.",
            "verification_required": True
        }
    
    def authenticate_user(self, username: str, password: str) -> Optional[User]:
        """Authenticate user by username/password"""
        user_id = self.username_to_id.get(username)
        if not user_id:
            return None
        
        user = self.users.get(user_id)
        if not user or not user.is_active:
            return None
        
        if user.password_hash == self.hash_password(password):
            user.last_login = datetime.now().isoformat()
            self.save_users()
            return user
        
        return None
    
    def get_user_by_id(self, user_id: str) -> Optional[User]:
        """Get user by ID"""
        return self.users.get(user_id)
    
    def get_user_by_username(self, username: str) -> Optional[User]:
        """Get user by username"""
        user_id = self.username_to_id.get(username)
        return self.users.get(user_id) if user_id else None
    
    def get_user_by_email(self, email: str) -> Optional[User]:
        """Get user by email address"""
        user_id = self.email_to_id.get(email.lower())
        return self.users.get(user_id) if user_id else None
    
    def request_organization_membership(self, user_id: str, organization_id: str, organization_name: str, reason: str) -> bool:
        """Request to join an organization"""
        user = self.users.get(user_id)
        if not user:
            return False
        
        # Check if request already exists
        for req in user.organization_requests:
            if req.organization_id == organization_id and req.status == "pending":
                return False  # Already pending
        
        # Add new request
        request = OrganizationRequest(
            organization_id=organization_id,
            organization_name=organization_name,
            request_reason=reason
        )
        
        user.organization_requests.append(request)
        user.updated_at = datetime.now().isoformat()
        self.save_users()
        
        return True
    
    def update_user_profile(self, user_id: str, updates: Dict) -> Dict[str, Any]:
        """Update user profile information"""
        user = self.users.get(user_id)
        if not user:
            return {"success": False, "error": "User not found"}
        
        # Update allowed fields
        allowed_updates = [
            'legal_first_name', 'legal_middle_name', 'legal_last_name',
            'email_addresses', 'phone_numbers', 'addresses', 'countries_of_citizenship'
        ]
        
        errors = []
        
        for field, value in updates.items():
            if field not in allowed_updates:
                errors.append(f"Field '{field}' cannot be updated")
                continue
            
            # Validate based on field type
            if field in ['legal_first_name', 'legal_last_name']:
                if not UserValidator.validate_name(value):
                    errors.append(f"Invalid {field} format")
                    continue
            elif field == 'legal_middle_name':
                if value and not UserValidator.validate_name(value):
                    errors.append(f"Invalid {field} format")
                    continue
            
            setattr(user, field, value)
        
        if not errors:
            user.updated_at = datetime.now().isoformat()
            self.save_users()
            return {"success": True, "message": "Profile updated successfully"}
        else:
            return {"success": False, "errors": errors}
    
    def list_all_users(self) -> List[Dict]:
        """List all users (admin function)"""
        users_list = []
        for user in self.users.values():
            users_list.append({
                "user_id": user.user_id,
                "username": user.username,
                "full_name": f"{user.legal_first_name} {user.legal_last_name}",
                "primary_email": user.get_primary_email().email if user.get_primary_email() else None,
                "is_active": user.is_active,
                "is_verified": user.is_verified,
                "verification_level": user.verification_level,
                "created_at": user.created_at,
                "last_login": user.last_login
            })
        return users_list

if __name__ == "__main__":
    # Example usage and testing
    user_manager = UserManager()
    
    # Example registration
    registration_data = {
        "username": "john_doe",
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
    
    result = user_manager.register_user(registration_data)
    print("Registration result:", result)
    
    if result["success"]:
        # Test authentication
        user = user_manager.authenticate_user("john_doe", "secure_password123")
        if user:
            print(f"Authentication successful for {user.legal_first_name} {user.legal_last_name}")
            print(f"Primary email: {user.get_primary_email().email}")
            print(f"Primary phone: {user.get_primary_phone().number}")
            
            # Test organization request
            user_manager.request_organization_membership(
                user.user_id,
                "org_001",
                "Civic Engagement Society",
                "I want to contribute to democratic processes"
            )
            print("Organization membership requested")
        else:
            print("Authentication failed")