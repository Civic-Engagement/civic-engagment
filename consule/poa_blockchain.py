#!/usr/bin/env python3
"""
PROOF OF AUTHORITY (PoA) BLOCKCHAIN IMPLEMENTATION
Tracks block creators, validators, and complete authority chain
"""

import json
import socket
import threading
import time
import hashlib
import sys
import os
from datetime import datetime
from typing import Dict, List, Optional, Set
import uuid

class Authority:
    """Represents a blockchain authority with validation powers"""
    def __init__(self, authority_id: str, name: str, public_key: str, 
                 node_address: str, granted_by: str = None, granted_at: str = None):
        self.authority_id = authority_id
        self.name = name
        self.public_key = public_key
        self.node_address = node_address
        self.granted_by = granted_by or "GENESIS"
        self.granted_at = granted_at or datetime.now().isoformat()
        self.is_active = True
        self.blocks_created = 0
        self.blocks_validated = 0
    
    def to_dict(self) -> Dict:
        return {
            'authority_id': self.authority_id,
            'name': self.name,
            'public_key': self.public_key,
            'node_address': self.node_address,
            'granted_by': self.granted_by,
            'granted_at': self.granted_at,
            'is_active': self.is_active,
            'blocks_created': self.blocks_created,
            'blocks_validated': self.blocks_validated
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'Authority':
        authority = cls(
            data['authority_id'],
            data['name'],
            data['public_key'],
            data['node_address'],
            data.get('granted_by', 'GENESIS'),
            data.get('granted_at')
        )
        authority.is_active = data.get('is_active', True)
        authority.blocks_created = data.get('blocks_created', 0)
        authority.blocks_validated = data.get('blocks_validated', 0)
        return authority

class Validation:
    """Represents a block validation by an authority"""
    def __init__(self, validator_id: str, validator_name: str, 
                 validation_timestamp: str, signature: str = None):
        self.validator_id = validator_id
        self.validator_name = validator_name
        self.validation_timestamp = validation_timestamp
        self.signature = signature or f"SIG_{hashlib.sha256(f'{validator_id}{validation_timestamp}'.encode()).hexdigest()[:16]}"
    
    def to_dict(self) -> Dict:
        return {
            'validator_id': self.validator_id,
            'validator_name': self.validator_name,
            'validation_timestamp': self.validation_timestamp,
            'signature': self.signature
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'Validation':
        return cls(
            data['validator_id'],
            data['validator_name'],
            data['validation_timestamp'],
            data.get('signature')
        )

class PoABlock:
    """Proof of Authority blockchain block with complete authority tracking"""
    def __init__(self, index: int, data: Dict, previous_hash: str = "",
                 creator_id: str = "", creator_name: str = ""):
        self.index = index
        self.timestamp = datetime.now().isoformat()
        self.data = data
        self.previous_hash = previous_hash
        self.creator_id = creator_id
        self.creator_name = creator_name
        self.created_at = datetime.now().isoformat()
        self.validations: List[Validation] = []
        self.is_finalized = False
        self.finalized_at: Optional[str] = None
        self.hash = self.calculate_hash()
    
    def calculate_hash(self) -> str:
        """Calculate block hash including authority information"""
        content = f"{self.index}{self.timestamp}{json.dumps(self.data, sort_keys=True)}{self.previous_hash}{self.creator_id}{self.created_at}"
        return hashlib.sha256(content.encode()).hexdigest()
    
    def add_validation(self, validator_id: str, validator_name: str) -> bool:
        """Add validation from an authority"""
        if self.is_finalized:
            return False
        
        # Check if this validator already validated
        for validation in self.validations:
            if validation.validator_id == validator_id:
                return False
        
        validation = Validation(validator_id, validator_name, datetime.now().isoformat())
        self.validations.append(validation)
        return True
    
    def finalize_block(self, min_validations: int = 1) -> bool:
        """Finalize block if it has enough validations"""
        if len(self.validations) >= min_validations and not self.is_finalized:
            self.is_finalized = True
            self.finalized_at = datetime.now().isoformat()
            return True
        return False
    
    def get_validation_info(self) -> Dict:
        """Get summary of validation information"""
        return {
            'validation_count': len(self.validations),
            'validators': [v.validator_name for v in self.validations],
            'is_finalized': self.is_finalized,
            'finalized_at': self.finalized_at
        }
    
    def to_dict(self) -> Dict:
        return {
            'index': self.index,
            'timestamp': self.timestamp,
            'data': self.data,
            'previous_hash': self.previous_hash,
            'creator_id': self.creator_id,
            'creator_name': self.creator_name,
            'created_at': self.created_at,
            'validations': [v.to_dict() for v in self.validations],
            'is_finalized': self.is_finalized,
            'finalized_at': self.finalized_at,
            'hash': self.hash
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'PoABlock':
        block = cls(
            data['index'],
            data['data'],
            data['previous_hash'],
            data.get('creator_id', ''),
            data.get('creator_name', '')
        )
        block.timestamp = data['timestamp']
        block.created_at = data.get('created_at', data['timestamp'])
        block.validations = [Validation.from_dict(v) for v in data.get('validations', [])]
        block.is_finalized = data.get('is_finalized', False)
        block.finalized_at = data.get('finalized_at')
        block.hash = data['hash']
        return block

class PoABlockchain:
    """Proof of Authority Blockchain with complete authority management"""
    def __init__(self, node_id: str, node_name: str, host: str = "localhost", 
                 port: int = 8333, blockchain_file: str = None):
        self.node_id = node_id
        self.node_name = node_name
        self.host = host
        self.port = port
        self.blockchain_file = blockchain_file or f"poa_blockchain_{port}.json"
        
        # Authority management
        self.authorities: Dict[str, Authority] = {}
        self.my_authority: Optional[Authority] = None
        
        # Blockchain
        self.chain: List[PoABlock] = []
        self.pending_blocks: List[PoABlock] = []
        
        # Network
        self.peers: List[str] = []
        self.running = False
        
        # Configuration
        self.min_validations_required = 1  # Minimum validations to finalize a block
        self.max_authorities = 10  # Maximum number of authorities
        
        # Initialize
        self.load_blockchain()
        if not self.chain:
            self.create_genesis_block()
    
    def create_genesis_block(self):
        """Create the initial genesis block and bootstrap authority"""
        print(f"🌱 Creating genesis block for PoA blockchain")
        
        # Create genesis authority
        genesis_authority = Authority(
            authority_id="GENESIS_AUTH",
            name="Genesis Authority",
            public_key="GENESIS_PUBLIC_KEY",
            node_address=f"{self.host}:{self.port}",
            granted_by="SYSTEM",
            granted_at=datetime.now().isoformat()
        )
        self.authorities["GENESIS_AUTH"] = genesis_authority
        
        # Create genesis block
        genesis_data = {
            "type": "GENESIS",
            "message": "Genesis Block - PoA Blockchain Initialized",
            "authorities_initialized": 1,
            "blockchain_started_at": datetime.now().isoformat()
        }
        
        genesis_block = PoABlock(
            index=0,
            data=genesis_data,
            previous_hash="0",
            creator_id="GENESIS_AUTH",
            creator_name="Genesis Authority"
        )
        
        # Auto-validate genesis block
        genesis_block.add_validation("GENESIS_AUTH", "Genesis Authority")
        genesis_block.finalize_block(min_validations=1)
        
        self.chain.append(genesis_block)
        self.save_blockchain()
    
    def grant_authority(self, new_authority_name: str, new_authority_public_key: str,
                       new_authority_address: str, granter_id: str) -> bool:
        """Grant authority to a new node"""
        if len(self.authorities) >= self.max_authorities:
            print(f"❌ Maximum authorities ({self.max_authorities}) reached")
            return False
        
        if granter_id not in self.authorities:
            print(f"❌ Granter {granter_id} is not an authority")
            return False
        
        if not self.authorities[granter_id].is_active:
            print(f"❌ Granter {granter_id} is not active")
            return False
        
        # Create new authority
        new_authority_id = f"AUTH_{len(self.authorities)}_{int(time.time())}"
        new_authority = Authority(
            authority_id=new_authority_id,
            name=new_authority_name,
            public_key=new_authority_public_key,
            node_address=new_authority_address,
            granted_by=granter_id,
            granted_at=datetime.now().isoformat()
        )
        
        self.authorities[new_authority_id] = new_authority
        
        # Create authority grant block
        grant_data = {
            "type": "AUTHORITY_GRANT",
            "new_authority_id": new_authority_id,
            "new_authority_name": new_authority_name,
            "new_authority_address": new_authority_address,
            "granted_by": granter_id,
            "granted_by_name": self.authorities[granter_id].name,
            "granted_at": new_authority.granted_at
        }
        
        return self.create_block(grant_data, granter_id)
    
    def revoke_authority(self, authority_id: str, revoker_id: str) -> bool:
        """Revoke authority from a node"""
        if authority_id not in self.authorities:
            print(f"❌ Authority {authority_id} not found")
            return False
        
        if revoker_id not in self.authorities:
            print(f"❌ Revoker {revoker_id} is not an authority")
            return False
        
        if authority_id == "GENESIS_AUTH":
            print(f"❌ Cannot revoke genesis authority")
            return False
        
        # Deactivate authority
        self.authorities[authority_id].is_active = False
        
        # Create revocation block
        revoke_data = {
            "type": "AUTHORITY_REVOKE",
            "revoked_authority_id": authority_id,
            "revoked_authority_name": self.authorities[authority_id].name,
            "revoked_by": revoker_id,
            "revoked_by_name": self.authorities[revoker_id].name,
            "revoked_at": datetime.now().isoformat()
        }
        
        return self.create_block(revoke_data, revoker_id)
    
    def create_block(self, data: Dict, creator_id: str) -> bool:
        """Create a new block (must be created by an authority)"""
        if creator_id not in self.authorities:
            print(f"❌ Creator {creator_id} is not an authority")
            return False
        
        if not self.authorities[creator_id].is_active:
            print(f"❌ Creator {creator_id} is not active")
            return False
        
        # Get previous block hash
        previous_hash = self.chain[-1].hash if self.chain else "0"
        
        # Create new block
        new_block = PoABlock(
            index=len(self.chain),
            data=data,
            previous_hash=previous_hash,
            creator_id=creator_id,
            creator_name=self.authorities[creator_id].name
        )
        
        # Add to pending blocks for validation
        self.pending_blocks.append(new_block)
        self.authorities[creator_id].blocks_created += 1
        
        print(f"📦 Block #{new_block.index} created by {self.authorities[creator_id].name}")
        return True
    
    def validate_block(self, block_index: int, validator_id: str) -> bool:
        """Validate a pending block"""
        if validator_id not in self.authorities:
            print(f"❌ Validator {validator_id} is not an authority")
            return False
        
        if not self.authorities[validator_id].is_active:
            print(f"❌ Validator {validator_id} is not active")
            return False
        
        # Find the block in pending blocks
        block_to_validate = None
        for block in self.pending_blocks:
            if block.index == block_index:
                block_to_validate = block
                break
        
        if not block_to_validate:
            print(f"❌ Block #{block_index} not found in pending blocks")
            return False
        
        # Add validation
        if block_to_validate.add_validation(validator_id, self.authorities[validator_id].name):
            self.authorities[validator_id].blocks_validated += 1
            print(f"✅ Block #{block_index} validated by {self.authorities[validator_id].name}")
            
            # Check if block can be finalized
            if block_to_validate.finalize_block(self.min_validations_required):
                # Move from pending to main chain
                self.pending_blocks.remove(block_to_validate)
                self.chain.append(block_to_validate)
                self.save_blockchain()
                print(f"🔒 Block #{block_index} finalized and added to chain")
            
            return True
        else:
            print(f"❌ Failed to validate block #{block_index}")
            return False
    
    def get_authority_stats(self) -> Dict:
        """Get statistics about authorities"""
        active_authorities = [auth for auth in self.authorities.values() if auth.is_active]
        inactive_authorities = [auth for auth in self.authorities.values() if not auth.is_active]
        
        return {
            'total_authorities': len(self.authorities),
            'active_authorities': len(active_authorities),
            'inactive_authorities': len(inactive_authorities),
            'authorities': {auth_id: auth.to_dict() for auth_id, auth in self.authorities.items()},
            'blocks_in_chain': len(self.chain),
            'pending_blocks': len(self.pending_blocks)
        }
    
    def get_block_details(self, block_index: int) -> Optional[Dict]:
        """Get detailed information about a specific block"""
        if block_index < 0 or block_index >= len(self.chain):
            return None
        
        block = self.chain[block_index]
        return {
            'block_info': block.to_dict(),
            'validation_info': block.get_validation_info(),
            'creator_info': self.authorities.get(block.creator_id, {}).to_dict() if block.creator_id in self.authorities else None
        }
    
    def save_blockchain(self):
        """Save blockchain and authorities to JSON file"""
        data = {
            'node_id': self.node_id,
            'node_name': self.node_name,
            'blockchain_type': 'Proof_of_Authority',
            'authorities': {auth_id: auth.to_dict() for auth_id, auth in self.authorities.items()},
            'chain_length': len(self.chain),
            'pending_blocks_count': len(self.pending_blocks),
            'min_validations_required': self.min_validations_required,
            'blocks': [block.to_dict() for block in self.chain],
            'pending_blocks': [block.to_dict() for block in self.pending_blocks],
            'last_saved': datetime.now().isoformat()
        }
        
        try:
            with open(self.blockchain_file, 'w') as f:
                json.dump(data, f, indent=2)
            print(f"💾 PoA Blockchain saved to {self.blockchain_file}")
        except Exception as e:
            print(f"❌ Error saving blockchain: {e}")
    
    def load_blockchain(self):
        """Load blockchain and authorities from JSON file"""
        if not os.path.exists(self.blockchain_file):
            print(f"📁 No existing PoA blockchain file found, will create new one")
            return
        
        try:
            with open(self.blockchain_file, 'r') as f:
                data = json.load(f)
            
            # Load authorities
            for auth_id, auth_data in data.get('authorities', {}).items():
                self.authorities[auth_id] = Authority.from_dict(auth_data)
            
            # Load main chain
            for block_data in data.get('blocks', []):
                block = PoABlock.from_dict(block_data)
                self.chain.append(block)
            
            # Load pending blocks
            for block_data in data.get('pending_blocks', []):
                block = PoABlock.from_dict(block_data)
                self.pending_blocks.append(block)
            
            self.min_validations_required = data.get('min_validations_required', 1)
            
            print(f"📁 Loaded PoA blockchain with {len(self.chain)} blocks and {len(self.authorities)} authorities")
            
        except Exception as e:
            print(f"❌ Error loading blockchain: {e}")
    
    def display_blockchain_summary(self):
        """Display a summary of the blockchain"""
        print(f"\n🔗 PROOF OF AUTHORITY BLOCKCHAIN SUMMARY")
        print(f"=" * 60)
        print(f"Node: {self.node_name} ({self.node_id})")
        print(f"Blockchain File: {self.blockchain_file}")
        print(f"Blocks in Chain: {len(self.chain)}")
        print(f"Pending Blocks: {len(self.pending_blocks)}")
        print(f"Total Authorities: {len(self.authorities)}")
        print(f"Active Authorities: {len([a for a in self.authorities.values() if a.is_active])}")
        print(f"Minimum Validations Required: {self.min_validations_required}")
        
        if self.authorities:
            print(f"\n👥 AUTHORITIES:")
            for auth_id, authority in self.authorities.items():
                status = "🟢 ACTIVE" if authority.is_active else "🔴 INACTIVE"
                print(f"   {status} {authority.name} ({auth_id})")
                print(f"      Created: {authority.blocks_created} blocks")
                print(f"      Validated: {authority.blocks_validated} blocks")
                print(f"      Granted by: {authority.granted_by}")
        
        if self.chain:
            print(f"\n📦 RECENT BLOCKS:")
            for block in self.chain[-3:]:  # Show last 3 blocks
                validation_info = block.get_validation_info()
                status = "🔒 FINALIZED" if block.is_finalized else "⏳ PENDING"
                print(f"   Block #{block.index}: {status}")
                print(f"      Creator: {block.creator_name}")
                print(f"      Validations: {validation_info['validation_count']}")
                print(f"      Type: {block.data.get('type', 'UNKNOWN')}")

def main():
    """Main function to run PoA blockchain demo"""
    print("🔗 PROOF OF AUTHORITY BLOCKCHAIN DEMO")
    print("=" * 50)
    
    # Create a PoA blockchain node
    node = PoABlockchain(
        node_id=f"NODE_{int(time.time())}",
        node_name="Demo Authority Node",
        port=8333
    )
    
    # Display initial state
    node.display_blockchain_summary()
    
    # Demo operations
    print(f"\n🚀 DEMO OPERATIONS")
    print(f"-" * 30)
    
    # Create some test blocks as genesis authority
    test_data_1 = {
        "type": "USER_REGISTRATION",
        "username": "testuser1",
        "action": "User registered on blockchain"
    }
    
    test_data_2 = {
        "type": "ORGANIZATION_CREATE",
        "org_name": "Test Organization",
        "action": "Organization created"
    }
    
    # Create blocks using genesis authority
    if node.create_block(test_data_1, "GENESIS_AUTH"):
        node.validate_block(1, "GENESIS_AUTH")  # Self-validate
    
    if node.create_block(test_data_2, "GENESIS_AUTH"):
        node.validate_block(2, "GENESIS_AUTH")  # Self-validate
    
    # Grant authority to a new node
    node.grant_authority(
        new_authority_name="Secondary Authority",
        new_authority_public_key="SEC_AUTH_PUBLIC_KEY",
        new_authority_address="localhost:8334",
        granter_id="GENESIS_AUTH"
    )
    
    # Validate the authority grant block
    if node.pending_blocks:
        node.validate_block(node.pending_blocks[0].index, "GENESIS_AUTH")
    
    # Final state
    print(f"\n" + "=" * 60)
    node.display_blockchain_summary()
    
    # Show detailed block information
    print(f"\n📋 DETAILED BLOCK INFORMATION")
    print(f"-" * 40)
    for i in range(len(node.chain)):
        details = node.get_block_details(i)
        if details:
            block_info = details['block_info']
            validation_info = details['validation_info']
            print(f"\nBlock #{i}:")
            print(f"  Type: {block_info['data'].get('type', 'UNKNOWN')}")
            print(f"  Creator: {block_info['creator_name']}")
            print(f"  Created: {block_info['created_at']}")
            print(f"  Validations: {validation_info['validation_count']}")
            print(f"  Finalized: {validation_info['is_finalized']}")

if __name__ == "__main__":
    main()