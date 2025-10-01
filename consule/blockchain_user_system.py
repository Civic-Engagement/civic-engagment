#!/usr/bin/env python3
"""
BLOCKCHAIN USER INTEGRATION
Integrates user management with the blockchain system
"""

import json
from datetime import datetime
from typing import Dict, List, Optional, Any
from user_manager import UserManager, User
from organization_manager import OrganizationManager
from simple_blockchain import SimpleP2PNode, SimpleBlock

class BlockchainUserSystem:
    """Integration of user management with blockchain"""
    
    def __init__(self, blockchain_port: int = 8333):
        self.user_manager = UserManager()
        self.org_manager = OrganizationManager()
        self.blockchain_node = None
        self.blockchain_port = blockchain_port
        self.current_user = None
    
    def start_blockchain_node(self, node_id: str = None):
        """Start blockchain node for this user system"""
        if not node_id:
            node_id = f"user-system-{self.blockchain_port}"
        
        self.blockchain_node = SimpleP2PNode(
            host="localhost",
            port=self.blockchain_port,
            node_id=node_id
        )
        
        print(f"🔗 Starting blockchain node on port {self.blockchain_port}")
        self.blockchain_node.start()
        return self.blockchain_node
    
    def log_to_blockchain(self, action: str, data: Dict) -> bool:
        """Log user actions to blockchain"""
        if not self.blockchain_node:
            return False
        
        block_data = {
            "action": action,
            "timestamp": datetime.now().isoformat(),
            "user_id": self.current_user.user_id if self.current_user else None,
            "data": data
        }
        
        try:
            self.blockchain_node.add_block(json.dumps(block_data))
            return True
        except Exception as e:
            print(f"Failed to log to blockchain: {e}")
            return False
    
    def register_user_with_blockchain(self, registration_data: Dict) -> Dict[str, Any]:
        """Register user and store ALL data on blockchain"""
        result = self.user_manager.register_user(registration_data)
        
        if result["success"]:
            # Get the complete user data
            user = self.user_manager.get_user_by_id(result["user_id"])
            
            # Store COMPLETE user data on blockchain
            blockchain_data = {
                "user_id": user.user_id,
                "username": user.username,
                "legal_first_name": user.legal_first_name,
                "legal_middle_name": user.legal_middle_name,
                "legal_last_name": user.legal_last_name,
                "date_of_birth": user.date_of_birth,
                "public_key": user.public_key_pem,
                "email_addresses": [email.to_dict() for email in user.email_addresses],
                "phone_numbers": [phone.to_dict() for phone in user.phone_numbers],
                "addresses": [addr.to_dict() for addr in user.addresses],
                "countries_of_citizenship": user.countries_of_citizenship,
                "verification_level": user.verification_level,
                "created_at": user.created_at
            }
            
            self.log_to_blockchain("user_registration_complete", blockchain_data)
            
            print(f"✅ Complete user registration data logged to blockchain")
            print(f"🔑 Public key generated and stored")
            print(f"🔒 Private key securely stored locally")
        
        return result
    
    def login_user_with_blockchain(self, username: str, password: str) -> Optional[User]:
        """Login user and log to blockchain"""
        user = self.user_manager.authenticate_user(username, password)
        
        if user:
            self.current_user = user
            
            # Log login to blockchain
            blockchain_data = {
                "user_id": user.user_id,
                "username": user.username,
                "login_timestamp": user.last_login
            }
            
            self.log_to_blockchain("user_login", blockchain_data)
            
            print(f"✅ User login logged to blockchain")
        
        return user
    
    def create_organization_with_blockchain(self, org_data: Dict) -> Dict[str, Any]:
        """Create organization and log to blockchain"""
        if not self.current_user:
            return {"success": False, "error": "Must be logged in to create organization"}
        
        result = self.org_manager.create_organization(self.current_user.user_id, org_data)
        
        if result["success"]:
            # Log organization creation to blockchain
            blockchain_data = {
                "organization_id": result["organization_id"],
                "name": org_data["name"],
                "type": org_data["organization_type"],
                "creator_id": self.current_user.user_id,
                "creator_username": self.current_user.username
            }
            
            self.log_to_blockchain("organization_created", blockchain_data)
            
            print(f"✅ Organization creation logged to blockchain")
        
        return result
    
    def join_organization_with_blockchain(self, org_id: str, reason: str = "") -> Dict[str, Any]:
        """Join organization and log to blockchain"""
        if not self.current_user:
            return {"success": False, "error": "Must be logged in to join organization"}
        
        result = self.org_manager.request_membership(
            org_id,
            self.current_user.user_id,
            self.current_user.username,
            f"{self.current_user.legal_first_name} {self.current_user.legal_last_name}",
            reason
        )
        
        if result["success"]:
            # Also update user's organization requests
            org = self.org_manager.get_organization(org_id)
            if org:
                self.user_manager.request_organization_membership(
                    self.current_user.user_id,
                    org_id,
                    org.name,
                    reason
                )
                
                # Log organization join to blockchain
                blockchain_data = {
                    "organization_id": org_id,
                    "organization_name": org.name,
                    "user_id": self.current_user.user_id,
                    "username": self.current_user.username,
                    "reason": reason
                }
                
                self.log_to_blockchain("organization_join_request", blockchain_data)
                
                print(f"✅ Organization join request logged to blockchain")
        
        return result
    
    def get_user_dashboard(self) -> Dict[str, Any]:
        """Get comprehensive user dashboard information"""
        if not self.current_user:
            return {"error": "Not logged in"}
        
        # Get user organizations
        user_orgs = self.org_manager.get_user_organizations(self.current_user.user_id)
        
        # Get blockchain stats
        blockchain_stats = {}
        if self.blockchain_node:
            blockchain_stats = {
                "node_id": self.blockchain_node.node_id,
                "chain_length": len(self.blockchain_node.blockchain),
                "peer_count": len(self.blockchain_node.peers),
                "is_running": self.blockchain_node.running
            }
        
        return {
            "user": {
                "user_id": self.current_user.user_id,
                "username": self.current_user.username,
                "full_name": f"{self.current_user.legal_first_name} {self.current_user.legal_last_name}",
                "primary_email": self.current_user.get_primary_email().email if self.current_user.get_primary_email() else None,
                "verification_level": self.current_user.verification_level,
                "is_verified": self.current_user.is_verified,
                "created_at": self.current_user.created_at,
                "last_login": self.current_user.last_login
            },
            "organizations": user_orgs,
            "blockchain": blockchain_stats
        }
    
    def get_blockchain_user_history(self, user_id: str = None) -> List[Dict]:
        """Get user's blockchain activity history"""
        if not self.blockchain_node:
            return []
        
        target_user_id = user_id or (self.current_user.user_id if self.current_user else None)
        if not target_user_id:
            return []
        
        user_blocks = []
        for block in self.blockchain_node.blockchain:
            try:
                block_data = json.loads(block.data)
                if isinstance(block_data, dict) and block_data.get("user_id") == target_user_id:
                    user_blocks.append({
                        "block_index": block.index,
                        "timestamp": block.timestamp,
                        "action": block_data.get("action"),
                        "data": block_data.get("data")
                    })
            except (json.JSONDecodeError, AttributeError):
                # Skip non-JSON or malformed blocks
                continue
        
        return user_blocks
    
    def display_dashboard(self):
        """Display user dashboard"""
        dashboard = self.get_user_dashboard()
        
        if "error" in dashboard:
            print(f"❌ {dashboard['error']}")
            return
        
        user = dashboard["user"]
        orgs = dashboard["organizations"]
        blockchain = dashboard["blockchain"]
        
        print("\n" + "=" * 60)
        print("📊 USER DASHBOARD")
        print("=" * 60)
        
        print(f"👤 User: {user['full_name']} (@{user['username']})")
        print(f"📧 Email: {user['primary_email'] or 'No primary email'}")
        print(f"🔒 Verification: {user['verification_level']} {'✅' if user['is_verified'] else '❌'}")
        print(f"📅 Member since: {user['created_at'][:10]}")
        print(f"🔄 Last login: {user['last_login'][:10] if user['last_login'] else 'Never'}")
        
        print(f"\n🏢 ORGANIZATIONS ({len(orgs)})")
        print("-" * 30)
        if orgs:
            for org in orgs:
                status_icon = "✅" if org['status'] == 'active' else "⏳" if org['status'] == 'pending' else "❌"
                print(f"{status_icon} {org['display_name']} ({org['role']})")
        else:
            print("No organization memberships")
        
        print(f"\n🔗 BLOCKCHAIN")
        print("-" * 30)
        if blockchain:
            print(f"Node ID: {blockchain['node_id']}")
            print(f"Chain Length: {blockchain['chain_length']} blocks")
            print(f"Peers: {blockchain['peer_count']}")
            print(f"Status: {'🟢 Running' if blockchain['is_running'] else '🔴 Stopped'}")
        else:
            print("Blockchain node not started")
        
        # Show recent blockchain activity
        history = self.get_blockchain_user_history()
        if history:
            print(f"\n📜 RECENT ACTIVITY ({len(history)} actions)")
            print("-" * 30)
            for activity in history[-5:]:  # Show last 5 activities
                print(f"• {activity['action']} - {activity['timestamp'][:10]}")

def main():
    """Main CLI interface for the integrated system"""
    system = BlockchainUserSystem()
    
    print("🔗 BLOCKCHAIN USER SYSTEM")
    print("=" * 40)
    
    while True:
        print("\n📋 MAIN MENU")
        print("1. 📝 Register User")
        print("2. 🔐 Login")
        print("3. 📊 Dashboard")
        print("4. 🏢 Create Organization")
        print("5. 🤝 Join Organization")
        print("6. 📋 List Organizations")
        print("7. 🔗 Start Blockchain Node")
        print("8. 📜 View Blockchain History")
        print("9. 🚪 Exit")
        
        choice = input("\nSelect option (1-9): ").strip()
        
        if choice == '1':
            # User registration (you could import the CLI here)
            print("Use user_registration_cli.py for detailed registration")
        
        elif choice == '2':
            username = input("Username: ")
            password = input("Password: ")
            user = system.login_user_with_blockchain(username, password)
            if user:
                print(f"✅ Welcome back, {user.legal_first_name}!")
            else:
                print("❌ Login failed")
        
        elif choice == '3':
            system.display_dashboard()
        
        elif choice == '4':
            if not system.current_user:
                print("❌ Must be logged in")
                continue
            
            name = input("Organization name: ")
            display_name = input("Display name: ")
            description = input("Description: ")
            org_type = input("Type (government/non_profit/community/etc): ")
            
            org_data = {
                "name": name,
                "display_name": display_name,
                "description": description,
                "organization_type": org_type
            }
            
            result = system.create_organization_with_blockchain(org_data)
            if result["success"]:
                print(f"✅ Organization created: {result['organization_id']}")
            else:
                print(f"❌ Failed: {result.get('errors', ['Unknown error'])}")
        
        elif choice == '5':
            if not system.current_user:
                print("❌ Must be logged in")
                continue
            
            # List available organizations
            orgs = system.org_manager.list_public_organizations()
            if not orgs:
                print("No public organizations available")
                continue
            
            print("\nAvailable Organizations:")
            for i, org in enumerate(orgs, 1):
                print(f"{i}. {org['display_name']} - {org['description'][:50]}...")
            
            try:
                choice_idx = int(input("Select organization (number): ")) - 1
                if 0 <= choice_idx < len(orgs):
                    org_id = orgs[choice_idx]['organization_id']
                    reason = input("Reason for joining: ")
                    
                    result = system.join_organization_with_blockchain(org_id, reason)
                    if result["success"]:
                        print(f"✅ {result['message']}")
                    else:
                        print(f"❌ {result['error']}")
                else:
                    print("Invalid selection")
            except ValueError:
                print("Invalid input")
        
        elif choice == '6':
            orgs = system.org_manager.list_public_organizations()
            print(f"\n🏢 PUBLIC ORGANIZATIONS ({len(orgs)})")
            print("-" * 50)
            for org in orgs:
                print(f"• {org['display_name']}")
                print(f"  Type: {org['organization_type']}, Members: {org['member_count']}")
                print(f"  {org['description'][:100]}...")
                print()
        
        elif choice == '7':
            if system.blockchain_node and system.blockchain_node.running:
                print("Blockchain node already running")
            else:
                system.start_blockchain_node()
                print("✅ Blockchain node started")
        
        elif choice == '8':
            if not system.current_user:
                print("❌ Must be logged in")
                continue
            
            history = system.get_blockchain_user_history()
            if history:
                print(f"\n📜 YOUR BLOCKCHAIN HISTORY ({len(history)} actions)")
                print("-" * 50)
                for activity in history:
                    print(f"Block {activity['block_index']}: {activity['action']}")
                    print(f"  Time: {activity['timestamp']}")
                    print(f"  Data: {activity['data']}")
                    print()
            else:
                print("No blockchain history found")
        
        elif choice == '9':
            if system.blockchain_node:
                system.blockchain_node.stop()
            print("👋 Goodbye!")
            break
        
        else:
            print("❌ Invalid choice")

if __name__ == "__main__":
    main()