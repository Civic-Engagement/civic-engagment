#!/usr/bin/env python3
"""
ORGANIZATION MANAGEMENT SYSTEM
System for creating and managing organizations that users can join
"""

import json
import uuid
from datetime import datetime
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict, field
from enum import Enum

class OrganizationType(Enum):
    GOVERNMENT = "government"
    NON_PROFIT = "non_profit"
    EDUCATIONAL = "educational"
    BUSINESS = "business"
    COMMUNITY = "community"
    POLITICAL = "political"
    PROFESSIONAL = "professional"
    RELIGIOUS = "religious"
    OTHER = "other"

class MembershipStatus(Enum):
    PENDING = "pending"
    ACTIVE = "active"
    SUSPENDED = "suspended"
    TERMINATED = "terminated"

class MembershipRole(Enum):
    MEMBER = "member"
    MODERATOR = "moderator"
    ADMIN = "admin"
    OWNER = "owner"

@dataclass
class OrganizationMember:
    """Member of an organization"""
    user_id: str
    username: str
    full_name: str
    role: MembershipRole
    status: MembershipStatus
    joined_at: str = field(default_factory=lambda: datetime.now().isoformat())
    approved_by: Optional[str] = None
    approved_at: Optional[str] = None
    notes: str = ""
    
    def to_dict(self) -> Dict:
        result = asdict(self)
        result['role'] = self.role.value
        result['status'] = self.status.value
        return result
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'OrganizationMember':
        data['role'] = MembershipRole(data['role'])
        data['status'] = MembershipStatus(data['status'])
        return cls(**data)

@dataclass
class Organization:
    """Complete organization information"""
    organization_id: str
    name: str
    display_name: str
    description: str
    organization_type: OrganizationType
    
    # Contact Information
    website: str = ""
    contact_email: str = ""
    contact_phone: str = ""
    
    # Address Information
    street_address: str = ""
    city: str = ""
    state_province: str = ""
    postal_code: str = ""
    country: str = ""
    
    # Settings
    is_public: bool = True  # Can anyone see this organization
    requires_approval: bool = True  # Do membership requests need approval
    is_active: bool = True
    
    # Members
    members: List[OrganizationMember] = field(default_factory=list)
    
    # Metadata
    created_by: str = ""  # User ID of creator
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    updated_at: str = field(default_factory=lambda: datetime.now().isoformat())
    
    def to_dict(self) -> Dict:
        result = asdict(self)
        result['organization_type'] = self.organization_type.value
        result['members'] = [member.to_dict() for member in self.members]
        return result
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'Organization':
        data['organization_type'] = OrganizationType(data['organization_type'])
        data['members'] = [OrganizationMember.from_dict(member) for member in data.get('members', [])]
        return cls(**data)
    
    def get_member(self, user_id: str) -> Optional[OrganizationMember]:
        """Get member by user ID"""
        for member in self.members:
            if member.user_id == user_id:
                return member
        return None
    
    def get_active_members(self) -> List[OrganizationMember]:
        """Get all active members"""
        return [member for member in self.members if member.status == MembershipStatus.ACTIVE]
    
    def get_pending_members(self) -> List[OrganizationMember]:
        """Get all pending members"""
        return [member for member in self.members if member.status == MembershipStatus.PENDING]
    
    def get_admins(self) -> List[OrganizationMember]:
        """Get all admin-level members (admin and owner)"""
        return [member for member in self.members 
                if member.role in [MembershipRole.ADMIN, MembershipRole.OWNER] 
                and member.status == MembershipStatus.ACTIVE]
    
    def can_approve_members(self, user_id: str) -> bool:
        """Check if user can approve new members"""
        member = self.get_member(user_id)
        if not member or member.status != MembershipStatus.ACTIVE:
            return False
        return member.role in [MembershipRole.ADMIN, MembershipRole.OWNER]

class OrganizationManager:
    """Manages organizations and memberships"""
    
    def __init__(self, data_file: str = "organizations.json"):
        self.data_file = data_file
        self.organizations: Dict[str, Organization] = {}
        self.name_to_id: Dict[str, str] = {}
        self.load_organizations()
    
    def load_organizations(self):
        """Load organizations from storage"""
        try:
            with open(self.data_file, 'r') as f:
                data = json.load(f)
                for org_id, org_data in data.items():
                    org = Organization.from_dict(org_data)
                    self.organizations[org_id] = org
                    self.name_to_id[org.name.lower()] = org_id
        except FileNotFoundError:
            self.save_organizations()
    
    def save_organizations(self):
        """Save organizations to storage"""
        data = {}
        for org_id, org in self.organizations.items():
            data[org_id] = org.to_dict()
        
        with open(self.data_file, 'w') as f:
            json.dump(data, f, indent=2)
    
    def create_organization(self, creator_user_id: str, org_data: Dict) -> Dict[str, Any]:
        """Create a new organization"""
        errors = []
        
        # Required fields
        required_fields = ['name', 'display_name', 'description', 'organization_type']
        for field in required_fields:
            if not org_data.get(field):
                errors.append(f"{field} is required")
        
        if errors:
            return {"success": False, "errors": errors}
        
        # Validate organization name is unique
        name = org_data['name'].strip().lower()
        if name in self.name_to_id:
            errors.append("Organization name already exists")
        
        # Validate organization type
        try:
            org_type = OrganizationType(org_data['organization_type'])
        except ValueError:
            errors.append(f"Invalid organization type: {org_data['organization_type']}")
            return {"success": False, "errors": errors}
        
        if errors:
            return {"success": False, "errors": errors}
        
        # Create organization
        org_id = str(uuid.uuid4())
        organization = Organization(
            organization_id=org_id,
            name=org_data['name'].strip(),
            display_name=org_data['display_name'].strip(),
            description=org_data['description'].strip(),
            organization_type=org_type,
            website=org_data.get('website', ''),
            contact_email=org_data.get('contact_email', ''),
            contact_phone=org_data.get('contact_phone', ''),
            street_address=org_data.get('street_address', ''),
            city=org_data.get('city', ''),
            state_province=org_data.get('state_province', ''),
            postal_code=org_data.get('postal_code', ''),
            country=org_data.get('country', ''),
            is_public=org_data.get('is_public', True),
            requires_approval=org_data.get('requires_approval', True),
            created_by=creator_user_id
        )
        
        # Add creator as owner
        # Note: You'll need to get user info from UserManager
        creator_member = OrganizationMember(
            user_id=creator_user_id,
            username="creator",  # This should come from UserManager
            full_name="Creator",  # This should come from UserManager
            role=MembershipRole.OWNER,
            status=MembershipStatus.ACTIVE,
            approved_by=creator_user_id,
            approved_at=datetime.now().isoformat()
        )
        
        organization.members.append(creator_member)
        
        # Store organization
        self.organizations[org_id] = organization
        self.name_to_id[name] = org_id
        self.save_organizations()
        
        return {
            "success": True,
            "organization_id": org_id,
            "message": "Organization created successfully"
        }
    
    def get_organization(self, org_id: str) -> Optional[Organization]:
        """Get organization by ID"""
        return self.organizations.get(org_id)
    
    def get_organization_by_name(self, name: str) -> Optional[Organization]:
        """Get organization by name"""
        org_id = self.name_to_id.get(name.lower())
        return self.organizations.get(org_id) if org_id else None
    
    def list_public_organizations(self) -> List[Dict]:
        """List all public organizations"""
        orgs = []
        for org in self.organizations.values():
            if org.is_public and org.is_active:
                orgs.append({
                    "organization_id": org.organization_id,
                    "name": org.name,
                    "display_name": org.display_name,
                    "description": org.description,
                    "organization_type": org.organization_type.value,
                    "member_count": len(org.get_active_members()),
                    "requires_approval": org.requires_approval,
                    "created_at": org.created_at
                })
        return orgs
    
    def request_membership(self, org_id: str, user_id: str, username: str, full_name: str, reason: str = "") -> Dict[str, Any]:
        """Request membership in an organization"""
        org = self.organizations.get(org_id)
        if not org:
            return {"success": False, "error": "Organization not found"}
        
        if not org.is_active:
            return {"success": False, "error": "Organization is not active"}
        
        # Check if user is already a member
        existing_member = org.get_member(user_id)
        if existing_member:
            if existing_member.status == MembershipStatus.PENDING:
                return {"success": False, "error": "Membership request already pending"}
            elif existing_member.status == MembershipStatus.ACTIVE:
                return {"success": False, "error": "Already a member of this organization"}
            elif existing_member.status == MembershipStatus.SUSPENDED:
                return {"success": False, "error": "Membership is suspended"}
        
        # Create membership request
        if org.requires_approval:
            status = MembershipStatus.PENDING
            message = "Membership request submitted for approval"
        else:
            status = MembershipStatus.ACTIVE
            message = "Membership approved automatically"
        
        member = OrganizationMember(
            user_id=user_id,
            username=username,
            full_name=full_name,
            role=MembershipRole.MEMBER,
            status=status,
            notes=reason
        )
        
        if not org.requires_approval:
            member.approved_at = datetime.now().isoformat()
        
        # Remove any existing membership record
        org.members = [m for m in org.members if m.user_id != user_id]
        org.members.append(member)
        
        org.updated_at = datetime.now().isoformat()
        self.save_organizations()
        
        return {"success": True, "message": message}
    
    def approve_membership(self, org_id: str, user_id: str, approver_user_id: str, approve: bool = True) -> Dict[str, Any]:
        """Approve or deny a membership request"""
        org = self.organizations.get(org_id)
        if not org:
            return {"success": False, "error": "Organization not found"}
        
        if not org.can_approve_members(approver_user_id):
            return {"success": False, "error": "You do not have permission to approve members"}
        
        member = org.get_member(user_id)
        if not member:
            return {"success": False, "error": "Membership request not found"}
        
        if member.status != MembershipStatus.PENDING:
            return {"success": False, "error": "Membership is not pending approval"}
        
        if approve:
            member.status = MembershipStatus.ACTIVE
            member.approved_by = approver_user_id
            member.approved_at = datetime.now().isoformat()
            message = "Membership approved"
        else:
            # Remove the membership record for denied requests
            org.members = [m for m in org.members if m.user_id != user_id]
            message = "Membership request denied"
        
        org.updated_at = datetime.now().isoformat()
        self.save_organizations()
        
        return {"success": True, "message": message}
    
    def update_member_role(self, org_id: str, user_id: str, new_role: str, updater_user_id: str) -> Dict[str, Any]:
        """Update a member's role"""
        org = self.organizations.get(org_id)
        if not org:
            return {"success": False, "error": "Organization not found"}
        
        if not org.can_approve_members(updater_user_id):
            return {"success": False, "error": "You do not have permission to update member roles"}
        
        member = org.get_member(user_id)
        if not member:
            return {"success": False, "error": "Member not found"}
        
        if member.status != MembershipStatus.ACTIVE:
            return {"success": False, "error": "Member is not active"}
        
        try:
            new_role_enum = MembershipRole(new_role)
        except ValueError:
            return {"success": False, "error": f"Invalid role: {new_role}"}
        
        # Prevent demoting the last owner
        if member.role == MembershipRole.OWNER and new_role_enum != MembershipRole.OWNER:
            owners = [m for m in org.members if m.role == MembershipRole.OWNER and m.status == MembershipStatus.ACTIVE]
            if len(owners) <= 1:
                return {"success": False, "error": "Cannot remove the last owner"}
        
        member.role = new_role_enum
        org.updated_at = datetime.now().isoformat()
        self.save_organizations()
        
        return {"success": True, "message": f"Member role updated to {new_role}"}
    
    def get_user_organizations(self, user_id: str) -> List[Dict]:
        """Get all organizations where user is a member"""
        user_orgs = []
        for org in self.organizations.values():
            member = org.get_member(user_id)
            if member:
                user_orgs.append({
                    "organization_id": org.organization_id,
                    "name": org.name,
                    "display_name": org.display_name,
                    "role": member.role.value,
                    "status": member.status.value,
                    "joined_at": member.joined_at
                })
        return user_orgs
    
    def get_organization_members(self, org_id: str, requester_user_id: str) -> Dict[str, Any]:
        """Get organization members (for admins)"""
        org = self.organizations.get(org_id)
        if not org:
            return {"success": False, "error": "Organization not found"}
        
        # Check if requester is a member
        requester = org.get_member(requester_user_id)
        if not requester or requester.status != MembershipStatus.ACTIVE:
            return {"success": False, "error": "You are not a member of this organization"}
        
        members_data = []
        for member in org.members:
            members_data.append({
                "user_id": member.user_id,
                "username": member.username,
                "full_name": member.full_name,
                "role": member.role.value,
                "status": member.status.value,
                "joined_at": member.joined_at,
                "approved_at": member.approved_at
            })
        
        return {
            "success": True,
            "organization": {
                "name": org.name,
                "display_name": org.display_name,
                "member_count": len(org.get_active_members())
            },
            "members": members_data
        }

if __name__ == "__main__":
    # Example usage
    org_manager = OrganizationManager()
    
    # Create example organization
    org_data = {
        "name": "civic_engagement_society",
        "display_name": "Civic Engagement Society",
        "description": "A community organization focused on promoting democratic participation and civic engagement.",
        "organization_type": "community",
        "website": "https://civicengagement.org",
        "contact_email": "info@civicengagement.org",
        "city": "Springfield",
        "state_province": "IL",
        "country": "USA",
        "is_public": True,
        "requires_approval": True
    }
    
    result = org_manager.create_organization("creator_user_id", org_data)
    print("Organization creation result:", result)
    
    if result["success"]:
        org_id = result["organization_id"]
        
        # Test membership request
        membership_result = org_manager.request_membership(
            org_id, 
            "test_user_id", 
            "test_user", 
            "Test User",
            "I want to contribute to civic engagement"
        )
        print("Membership request result:", membership_result)
        
        # List public organizations
        public_orgs = org_manager.list_public_organizations()
        print("Public organizations:", public_orgs)