#!/usr/bin/env python3
"""
POA BLOCKCHAIN USER INTEGRATION
Integrates user management with Proof of Authority blockchain system
"""

import json
from datetime import datetime
from typing import Dict, List, Optional, Any
from user_manager import UserManager, User
from organization_manager import OrganizationManager
from poa_blockchain import PoABlockchain, Authority

class PoABlockchainUserSystem:
    """Integration of user management with PoA blockchain"""
    
    def __init__(self, node_name: str = "User Management Node", blockchain_port: int = 8333):
        self.user_manager = UserManager()
        self.org_manager = OrganizationManager()
        self.blockchain = None
        self.blockchain_port = blockchain_port
        self.node_name = node_name
        self.current_user = None
        self.my_authority_id = None
    
    def initialize_blockchain(self, authority_name: str = None):
        """Initialize PoA blockchain for user management"""
        if not authority_name:
            authority_name = f"Authority-{self.blockchain_port}"
        
        node_id = f"USER_NODE_{self.blockchain_port}_{int(datetime.now().timestamp())}"
        
        self.blockchain = PoABlockchain(
            node_id=node_id,
            node_name=self.node_name,
            host="localhost",
            port=self.blockchain_port,
            blockchain_file=f"user_management_blockchain_{self.blockchain_port}.json"
        )
        
        print(f"🔗 PoA Blockchain initialized for user management on port {self.blockchain_port}")
        return self.blockchain
    
    def grant_user_authority(self, user_id: str, granter_authority_id: str = None) -> bool:
        """Grant blockchain authority to a user"""
        if not self.blockchain:
            print("❌ Blockchain not initialized")
            return False
        
        user = self.user_manager.get_user_by_id(user_id)
        if not user:
            print(f"❌ User {user_id} not found")
            return False
        
        # Use genesis authority if no granter specified
        if not granter_authority_id:
            granter_authority_id = "GENESIS_AUTH"
        
        # Create authority name from user info
        authority_name = f"{user.legal_first_name} {user.legal_last_name} Authority"
        authority_address = f"localhost:{self.blockchain_port + len(self.blockchain.authorities)}"
        
        success = self.blockchain.grant_authority(
            new_authority_name=authority_name,
            new_authority_public_key=user.public_key_pem[:100] if user.public_key_pem else f"USER_KEY_{user_id}",
            new_authority_address=authority_address,
            granter_id=granter_authority_id
        )
        
        if success:
            print(f"✅ Authority granted to user {user.username}")
            # Auto-validate the authority grant if we have the granting authority
            if self.blockchain.pending_blocks:
                self.blockchain.validate_block(
                    self.blockchain.pending_blocks[-1].index, 
                    granter_authority_id
                )
        
        return success
    
    def register_user_with_blockchain(self, registration_data: Dict, creator_authority_id: str = None) -> Dict[str, Any]:
        """Register user and log to PoA blockchain"""
        # Register user normally
        result = self.user_manager.register_user(registration_data)
        
        if not result['success']:
            return result
        
        # Log to blockchain if available
        if self.blockchain:
            if not creator_authority_id:
                creator_authority_id = "GENESIS_AUTH"
            
            # Create comprehensive blockchain record
            blockchain_data = {
                "type": "USER_REGISTRATION",
                "user_id": result['user_id'],
                "username": registration_data['username'],
                "legal_name": f"{registration_data['legal_first_name']} {registration_data.get('legal_middle_name', '')} {registration_data['legal_last_name']}".strip(),
                "date_of_birth": registration_data['date_of_birth'],
                "email_addresses": [email['email'] for email in registration_data.get('email_addresses', [])],
                "phone_numbers": [f"{phone['type']}: {phone['number']}" for phone in registration_data.get('phone_numbers', [])],
                "addresses": [f"{addr['type']}: {addr['street']}, {addr['city']}, {addr['state']} {addr['zip_code']}" for addr in registration_data.get('addresses', [])],
                "citizenship_countries": registration_data.get('citizenship_countries', []),
                "public_key": registration_data.get('public_key_pem', '')[:100] + "..." if registration_data.get('public_key_pem') else None,
                "registration_timestamp": datetime.now().isoformat(),
                "blockchain_node": self.blockchain.node_id
            }
            
            # Create block
            block_created = self.blockchain.create_block(blockchain_data, creator_authority_id)
            
            if block_created and self.blockchain.pending_blocks:
                # Auto-validate with the creator authority
                validation_success = self.blockchain.validate_block(
                    self.blockchain.pending_blocks[-1].index,
                    creator_authority_id
                )
                
                if validation_success:
                    result['blockchain_logged'] = True
                    result['blockchain_block_index'] = len(self.blockchain.chain) - 1
                    print(f"✅ User registration logged to PoA blockchain")
                else:
                    result['blockchain_logged'] = False
                    print(f"⚠️ User registered but blockchain validation failed")
            else:
                result['blockchain_logged'] = False
                print(f"⚠️ User registered but blockchain logging failed")
        
        return result
    
    def create_organization_with_blockchain(self, org_data: Dict, creator_user_id: str, creator_authority_id: str = None) -> Dict[str, Any]:
        """Create organization and log to PoA blockchain"""
        # Create organization normally
        result = self.org_manager.create_organization(org_data, creator_user_id)
        
        if not result['success']:
            return result
        
        # Log to blockchain if available
        if self.blockchain:
            if not creator_authority_id:
                creator_authority_id = "GENESIS_AUTH"
            
            blockchain_data = {
                "type": "ORGANIZATION_CREATION",
                "organization_id": result['organization_id'],
                "organization_name": org_data['name'],
                "organization_type": org_data.get('type', 'Unknown'),
                "creator_user_id": creator_user_id,
                "description": org_data.get('description', ''),
                "creation_timestamp": datetime.now().isoformat(),
                "blockchain_node": self.blockchain.node_id
            }
            
            # Create and validate block
            block_created = self.blockchain.create_block(blockchain_data, creator_authority_id)
            
            if block_created and self.blockchain.pending_blocks:
                validation_success = self.blockchain.validate_block(
                    self.blockchain.pending_blocks[-1].index,
                    creator_authority_id
                )
                
                if validation_success:
                    result['blockchain_logged'] = True
                    result['blockchain_block_index'] = len(self.blockchain.chain) - 1
                    print(f"✅ Organization creation logged to PoA blockchain")
        
        return result
    
    def join_organization_with_blockchain(self, org_id: str, user_id: str, creator_authority_id: str = None) -> Dict[str, Any]:
        """Join organization and log to PoA blockchain"""
        # Join organization normally
        result = self.org_manager.join_organization(org_id, user_id)
        
        if not result['success']:
            return result
        
        # Log to blockchain if available
        if self.blockchain:
            if not creator_authority_id:
                creator_authority_id = "GENESIS_AUTH"
            
            user = self.user_manager.get_user_by_id(user_id)
            org = self.org_manager.get_organization(org_id)
            
            blockchain_data = {
                "type": "ORGANIZATION_JOIN",
                "organization_id": org_id,
                "organization_name": org.name if org else "Unknown",
                "user_id": user_id,
                "username": user.username if user else "Unknown",
                "join_timestamp": datetime.now().isoformat(),
                "blockchain_node": self.blockchain.node_id
            }
            
            # Create and validate block
            block_created = self.blockchain.create_block(blockchain_data, creator_authority_id)
            
            if block_created and self.blockchain.pending_blocks:
                validation_success = self.blockchain.validate_block(
                    self.blockchain.pending_blocks[-1].index,
                    creator_authority_id
                )
                
                if validation_success:
                    result['blockchain_logged'] = True
                    result['blockchain_block_index'] = len(self.blockchain.chain) - 1
                    print(f"✅ Organization join logged to PoA blockchain")
        
        return result
    
    def get_user_blockchain_history(self, user_id: str) -> List[Dict]:
        """Get all blockchain entries for a specific user"""
        if not self.blockchain:
            return []
        
        user_blocks = []
        for block in self.blockchain.chain:
            if block.data.get('user_id') == user_id or block.data.get('creator_user_id') == user_id:
                user_blocks.append({
                    'block_index': block.index,
                    'type': block.data.get('type'),
                    'timestamp': block.timestamp,
                    'creator': block.creator_name,
                    'data': block.data,
                    'validations': len(block.validations),
                    'is_finalized': block.is_finalized
                })
        
        return user_blocks
    
    def get_blockchain_stats(self) -> Dict:
        """Get comprehensive blockchain statistics"""
        if not self.blockchain:
            return {'error': 'Blockchain not initialized'}
        
        stats = self.blockchain.get_authority_stats()
        
        # Add user management specific stats
        user_registrations = len([b for b in self.blockchain.chain if b.data.get('type') == 'USER_REGISTRATION'])
        org_creations = len([b for b in self.blockchain.chain if b.data.get('type') == 'ORGANIZATION_CREATION'])
        org_joins = len([b for b in self.blockchain.chain if b.data.get('type') == 'ORGANIZATION_JOIN'])
        authority_grants = len([b for b in self.blockchain.chain if b.data.get('type') == 'AUTHORITY_GRANT'])
        
        stats.update({
            'user_registrations_on_blockchain': user_registrations,
            'organization_creations_on_blockchain': org_creations,
            'organization_joins_on_blockchain': org_joins,
            'authority_grants_on_blockchain': authority_grants
        })
        
        return stats
    
    def display_comprehensive_dashboard(self):
        """Display a comprehensive dashboard of the entire system"""
        print(f"\n🔗 POA BLOCKCHAIN USER MANAGEMENT DASHBOARD")
        print(f"=" * 70)
        
        # System overview
        print(f"📊 SYSTEM OVERVIEW")
        print(f"-" * 20)
        print(f"Users Registered: {len(self.user_manager.users)}")
        print(f"Organizations: {len(self.org_manager.organizations)}")
        print(f"Current User: {self.current_user.username if self.current_user else 'Not logged in'}")
        
        # Blockchain stats
        if self.blockchain:
            stats = self.get_blockchain_stats()
            print(f"\n⛓️ BLOCKCHAIN STATISTICS")
            print(f"-" * 25)
            print(f"Blockchain Type: Proof of Authority (PoA)")
            print(f"Total Blocks: {stats['blocks_in_chain']}")
            print(f"Pending Blocks: {stats['pending_blocks']}")
            print(f"Active Authorities: {stats['active_authorities']}")
            print(f"User Registrations on Chain: {stats['user_registrations_on_blockchain']}")
            print(f"Organization Actions on Chain: {stats['organization_creations_on_blockchain'] + stats['organization_joins_on_blockchain']}")
            print(f"Authority Grants: {stats['authority_grants_on_blockchain']}")
            
            # Show authorities
            print(f"\n👥 BLOCKCHAIN AUTHORITIES")
            print(f"-" * 26)
            for auth_id, auth_info in stats['authorities'].items():
                status = "🟢 ACTIVE" if auth_info['is_active'] else "🔴 INACTIVE"
                print(f"   {status} {auth_info['name']}")
                print(f"      ID: {auth_id}")
                print(f"      Blocks Created: {auth_info['blocks_created']}")
                print(f"      Blocks Validated: {auth_info['blocks_validated']}")
            
            # Show recent blockchain activity
            print(f"\n📈 RECENT BLOCKCHAIN ACTIVITY")
            print(f"-" * 32)
            recent_blocks = self.blockchain.chain[-5:] if len(self.blockchain.chain) > 5 else self.blockchain.chain
            for block in recent_blocks:
                block_type = block.data.get('type', 'UNKNOWN')
                validation_count = len(block.validations)
                status = "🔒" if block.is_finalized else "⏳"
                print(f"   {status} Block #{block.index}: {block_type}")
                print(f"      Creator: {block.creator_name}")
                print(f"      Validations: {validation_count}")
                print(f"      Time: {block.timestamp}")
        else:
            print(f"\n⛓️ BLOCKCHAIN: Not initialized")
    
    def login_user(self, username: str, password: str) -> Dict[str, Any]:
        """Login user and return user info"""
        result = self.user_manager.login_user(username, password)
        if result['success']:
            self.current_user = result['user']
        return result

def main():
    """Main function for PoA blockchain user system demo"""
    print("🔗 POA BLOCKCHAIN USER MANAGEMENT SYSTEM")
    print("=" * 60)
    
    # Initialize system
    system = PoABlockchainUserSystem(node_name="Demo User Management", blockchain_port=8333)
    system.initialize_blockchain()
    
    while True:
        print(f"\n📋 MAIN MENU")
        print("1. 📝 Register User")
        print("2. 🔐 Login")
        print("3. 📊 Dashboard")
        print("4. 🏢 Create Organization")
        print("5. 🤝 Join Organization")
        print("6. 📋 List Organizations")
        print("7. 👑 Grant User Authority")
        print("8. 📜 View Blockchain History")
        print("9. 📈 Blockchain Stats")
        print("10. 👤 User Blockchain History")
        print("11. 🚪 Exit")
        
        try:
            choice = input("\nSelect option (1-11): ").strip()
            
            if choice == "1":
                print("Use user_registration_cli.py for detailed registration")
                # Could integrate here, but CLI provides better UX
                
            elif choice == "2":
                if system.current_user:
                    print(f"Already logged in as {system.current_user.username}")
                    continue
                
                username = input("Username: ")
                password = input("Password: ")
                
                result = system.login_user(username, password)
                if result['success']:
                    print(f"✅ Logged in as {result['user'].username}")
                else:
                    print(f"❌ {result['message']}")
            
            elif choice == "3":
                if not system.current_user:
                    print("❌ Not logged in")
                    continue
                
                system.display_comprehensive_dashboard()
                
            elif choice == "4":
                if not system.current_user:
                    print("❌ Not logged in")
                    continue
                
                name = input("Organization name: ")
                org_type = input("Organization type (optional): ") or "General"
                description = input("Description (optional): ") or ""
                
                org_data = {
                    'name': name,
                    'type': org_type,
                    'description': description
                }
                
                result = system.create_organization_with_blockchain(
                    org_data, 
                    system.current_user.user_id
                )
                
                if result['success']:
                    print(f"✅ Organization '{name}' created successfully")
                    if result.get('blockchain_logged'):
                        print(f"✅ Logged to blockchain at block #{result.get('blockchain_block_index')}")
                else:
                    print(f"❌ {result['message']}")
            
            elif choice == "5":
                if not system.current_user:
                    print("❌ Not logged in")
                    continue
                
                # List organizations first
                orgs = system.org_manager.get_all_organizations()
                if not orgs:
                    print("No organizations available")
                    continue
                
                print("\nAvailable Organizations:")
                for i, org in enumerate(orgs, 1):
                    print(f"{i}. {org.name} ({org.type})")
                
                try:
                    org_choice = int(input("Select organization number: ")) - 1
                    if 0 <= org_choice < len(orgs):
                        selected_org = orgs[org_choice]
                        result = system.join_organization_with_blockchain(
                            selected_org.organization_id,
                            system.current_user.user_id
                        )
                        
                        if result['success']:
                            print(f"✅ Joined organization '{selected_org.name}'")
                            if result.get('blockchain_logged'):
                                print(f"✅ Logged to blockchain at block #{result.get('blockchain_block_index')}")
                        else:
                            print(f"❌ {result['message']}")
                    else:
                        print("Invalid selection")
                except ValueError:
                    print("Invalid input")
            
            elif choice == "6":
                orgs = system.org_manager.get_all_organizations()
                if not orgs:
                    print("No organizations found")
                else:
                    print(f"\n📋 ORGANIZATIONS ({len(orgs)} found)")
                    print("-" * 40)
                    for org in orgs:
                        print(f"• {org.name} ({org.type})")
                        print(f"  Members: {len(org.members)}")
                        if org.description:
                            print(f"  Description: {org.description}")
            
            elif choice == "7":
                if not system.current_user:
                    print("❌ Not logged in")
                    continue
                
                # List users
                users = list(system.user_manager.users.values())
                if not users:
                    print("No users found")
                    continue
                
                print("\nUsers:")
                for i, user in enumerate(users, 1):
                    print(f"{i}. {user.username} ({user.legal_first_name} {user.legal_last_name})")
                
                try:
                    user_choice = int(input("Select user number to grant authority: ")) - 1
                    if 0 <= user_choice < len(users):
                        selected_user = users[user_choice]
                        success = system.grant_user_authority(selected_user.user_id)
                        if success:
                            print(f"✅ Authority granted to {selected_user.username}")
                        else:
                            print(f"❌ Failed to grant authority")
                    else:
                        print("Invalid selection")
                except ValueError:
                    print("Invalid input")
            
            elif choice == "8":
                if system.blockchain:
                    system.blockchain.display_blockchain_summary()
                else:
                    print("❌ Blockchain not initialized")
            
            elif choice == "9":
                stats = system.get_blockchain_stats()
                if 'error' not in stats:
                    print(f"\n📊 DETAILED BLOCKCHAIN STATISTICS")
                    print(f"=" * 45)
                    for key, value in stats.items():
                        if key != 'authorities':
                            print(f"{key.replace('_', ' ').title()}: {value}")
                else:
                    print(f"❌ {stats['error']}")
            
            elif choice == "10":
                if not system.current_user:
                    print("❌ Not logged in")
                    continue
                
                history = system.get_user_blockchain_history(system.current_user.user_id)
                if history:
                    print(f"\n📜 BLOCKCHAIN HISTORY FOR {system.current_user.username}")
                    print(f"=" * 50)
                    for entry in history:
                        status = "🔒 FINALIZED" if entry['is_finalized'] else "⏳ PENDING"
                        print(f"Block #{entry['block_index']}: {entry['type']} {status}")
                        print(f"  Creator: {entry['creator']}")
                        print(f"  Time: {entry['timestamp']}")
                        print(f"  Validations: {entry['validations']}")
                else:
                    print("No blockchain history found for this user")
            
            elif choice == "11":
                print("👋 Goodbye!")
                break
            
            else:
                print("Invalid option")
                
        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"❌ An error occurred: {e}")

if __name__ == "__main__":
    main()