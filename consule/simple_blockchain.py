#!/usr/bin/env python3
"""
CLEAN MULTI-NODE BLOCKCHAIN IMPLEMENTATION
Simple P2P blockchain network with proper node communication
"""

import json
import socket
import threading
import time
import hashlib
import sys
import os
from datetime import datetime
from typing import Dict, List, Optional
import argparse

class SimpleBlock:
    """Basic blockchain block"""
    def __init__(self, index: int, data: str, previous_hash: str = ""):
        self.index = index
        self.timestamp = datetime.now().isoformat()
        self.data = data
        self.previous_hash = previous_hash
        self.hash = self.calculate_hash()
    
    def calculate_hash(self) -> str:
        """Calculate block hash"""
        content = f"{self.index}{self.timestamp}{self.data}{self.previous_hash}"
        return hashlib.sha256(content.encode()).hexdigest()
    
    def to_dict(self) -> Dict:
        return {
            'index': self.index,
            'timestamp': self.timestamp,
            'data': self.data,
            'previous_hash': self.previous_hash,
            'hash': self.hash
        }

class SimpleP2PNode:
    """Simple P2P networking node"""
    def __init__(self, host: str = "localhost", port: int = 8333, node_id: str = None):
        self.host = host
        self.port = port
        self.node_id = node_id or f"node-{port}"
        self.peers: List[str] = []
        self.blockchain: List[SimpleBlock] = []
        self.running = False
        
        # Create genesis block
        genesis = SimpleBlock(0, "Genesis Block")
        self.blockchain.append(genesis)
        
        # Socket for listening
        self.server_socket = None
        self.peer_sockets: Dict[str, socket.socket] = {}
        
        print(f"🚀 Initializing node {self.node_id} on {host}:{port}")
    
    def start_server(self):
        """Start P2P server to accept connections"""
        try:
            self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.server_socket.bind((self.host, self.port))
            self.server_socket.listen(10)
            
            print(f"✅ {self.node_id} listening on {self.host}:{self.port}")
            
            while self.running:
                try:
                    client_socket, addr = self.server_socket.accept()
                    print(f"📡 {self.node_id} received connection from {addr}")
                    threading.Thread(target=self.handle_peer, args=(client_socket, addr), daemon=True).start()
                except Exception as e:
                    if self.running:
                        print(f"❌ Server error: {e}")
                    break
                    
        except Exception as e:
            print(f"❌ Failed to start server on {self.host}:{self.port}: {e}")
    
    def handle_peer(self, client_socket: socket.socket, addr):
        """Handle incoming peer connection"""
        peer_id = f"{addr[0]}:{addr[1]}"
        try:
            while self.running:
                data = client_socket.recv(1024).decode()
                if not data:
                    break
                
                try:
                    message = json.loads(data)
                    self.process_message(message, peer_id)
                except json.JSONDecodeError:
                    print(f"⚠️ Invalid JSON from {peer_id}")
                
        except Exception as e:
            print(f"❌ Error handling peer {peer_id}: {e}")
        finally:
            client_socket.close()
            if peer_id in self.peer_sockets:
                del self.peer_sockets[peer_id]
    
    def connect_to_peer(self, host: str, port: int) -> bool:
        """Connect to a peer node"""
        peer_id = f"{host}:{port}"
        
        if peer_id in self.peer_sockets:
            return True
        
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(10.0)
            sock.connect((host, port))
            
            self.peer_sockets[peer_id] = sock
            self.peers.append(peer_id)
            
            # Send hello message
            hello_msg = {
                'type': 'hello',
                'node_id': self.node_id,
                'blockchain_length': len(self.blockchain)
            }
            self.send_to_peer(peer_id, hello_msg)
            
            print(f"✅ {self.node_id} connected to {peer_id}")
            
            # Start receiving from this peer
            threading.Thread(target=self.handle_peer, args=(sock, (host, port)), daemon=True).start()
            
            return True
            
        except Exception as e:
            print(f"❌ {self.node_id} failed to connect to {peer_id}: {e}")
            return False
    
    def send_to_peer(self, peer_id: str, message: Dict):
        """Send message to a specific peer"""
        if peer_id in self.peer_sockets:
            try:
                data = json.dumps(message).encode()
                self.peer_sockets[peer_id].send(data)
            except Exception as e:
                print(f"❌ Failed to send to {peer_id}: {e}")
                self.disconnect_peer(peer_id)
    
    def broadcast_to_peers(self, message: Dict):
        """Broadcast message to all connected peers"""
        for peer_id in list(self.peer_sockets.keys()):
            self.send_to_peer(peer_id, message)
    
    def process_message(self, message: Dict, peer_id: str):
        """Process incoming message from peer"""
        msg_type = message.get('type')
        
        if msg_type == 'hello':
            print(f"👋 Received hello from {message.get('node_id', peer_id)}")
            # Send our blockchain if theirs is shorter
            if message.get('blockchain_length', 0) < len(self.blockchain):
                self.send_blockchain(peer_id)
        
        elif msg_type == 'blockchain':
            print(f"⛓️ Received blockchain from {peer_id}")
            self.update_blockchain(message.get('blocks', []))
        
        elif msg_type == 'new_block':
            print(f"🆕 Received new block from {peer_id}")
            self.add_block_from_peer(message.get('block'))
    
    def send_blockchain(self, peer_id: str):
        """Send our blockchain to a peer"""
        blockchain_msg = {
            'type': 'blockchain',
            'blocks': [block.to_dict() for block in self.blockchain]
        }
        self.send_to_peer(peer_id, blockchain_msg)
    
    def update_blockchain(self, blocks: List[Dict]):
        """Update our blockchain if received one is longer and valid"""
        if len(blocks) > len(self.blockchain):
            # Simple validation: check if it's a valid chain
            if self.validate_blockchain(blocks):
                print(f"🔄 Updating blockchain: {len(self.blockchain)} -> {len(blocks)} blocks")
                self.blockchain = self.dict_to_blocks(blocks)
            else:
                print("❌ Received invalid blockchain")
    
    def validate_blockchain(self, blocks: List[Dict]) -> bool:
        """Basic blockchain validation"""
        for i in range(1, len(blocks)):
            if blocks[i]['previous_hash'] != blocks[i-1]['hash']:
                return False
        return True
    
    def dict_to_blocks(self, block_dicts: List[Dict]) -> List[SimpleBlock]:
        """Convert dict representation to Block objects"""
        blocks = []
        for block_dict in block_dicts:
            block = SimpleBlock(
                block_dict['index'],
                block_dict['data'],
                block_dict['previous_hash']
            )
            # Use the hash from the dict to maintain consistency
            block.hash = block_dict['hash']
            blocks.append(block)
        return blocks
    
    def add_block(self, data: str):
        """Add new block to our blockchain"""
        previous_block = self.blockchain[-1]
        new_block = SimpleBlock(
            len(self.blockchain),
            data,
            previous_block.hash
        )
        self.blockchain.append(new_block)
        
        print(f"➕ {self.node_id} added block #{new_block.index}: {data}")
        
        # Broadcast new block to peers
        block_msg = {
            'type': 'new_block',
            'block': new_block.to_dict()
        }
        self.broadcast_to_peers(block_msg)
    
    def add_block_from_peer(self, block_dict: Dict):
        """Add block received from peer"""
        if not block_dict:
            return
        
        # Check if this block extends our chain
        if (block_dict['index'] == len(self.blockchain) and 
            block_dict['previous_hash'] == self.blockchain[-1].hash):
            
            block = SimpleBlock(
                block_dict['index'],
                block_dict['data'],
                block_dict['previous_hash']
            )
            block.hash = block_dict['hash']
            self.blockchain.append(block)
            
            print(f"✅ {self.node_id} accepted block #{block.index} from peer")
    
    def disconnect_peer(self, peer_id: str):
        """Disconnect from a peer"""
        if peer_id in self.peer_sockets:
            try:
                self.peer_sockets[peer_id].close()
            except:
                pass
            del self.peer_sockets[peer_id]
        
        if peer_id in self.peers:
            self.peers.remove(peer_id)
    
    def start(self):
        """Start the node"""
        self.running = True
        
        # Start server in a separate thread
        server_thread = threading.Thread(target=self.start_server, daemon=True)
        server_thread.start()
        
        time.sleep(1)  # Give server time to start
        return True
    
    def stop(self):
        """Stop the node"""
        print(f"🛑 Stopping {self.node_id}...")
        self.running = False
        
        # Close all peer connections
        for peer_id in list(self.peer_sockets.keys()):
            self.disconnect_peer(peer_id)
        
        # Close server socket
        if self.server_socket:
            try:
                self.server_socket.close()
            except:
                pass
        
        print(f"✅ {self.node_id} stopped")
    
    def get_status(self) -> Dict:
        """Get node status"""
        return {
            'node_id': self.node_id,
            'running': self.running,
            'peers': len(self.peers),
            'peer_list': self.peers.copy(),
            'blockchain_length': len(self.blockchain),
            'latest_block': self.blockchain[-1].to_dict() if self.blockchain else None
        }
    
    def print_status(self):
        """Print current status"""
        print(f"\n📊 {self.node_id} Status:")
        print(f"   Running: {self.running}")
        print(f"   Peers: {len(self.peers)} - {self.peers}")
        print(f"   Blockchain: {len(self.blockchain)} blocks")
        if self.blockchain:
            latest = self.blockchain[-1]
            print(f"   Latest block: #{latest.index} - {latest.data[:50]}...")
        print()

def run_interactive_node(node: SimpleP2PNode):
    """Run node with interactive commands"""
    print(f"\n🖥️  {node.node_id} Interactive Mode")
    print("Commands: status, peers, chain, add <data>, connect <host:port>, stop, help")
    print("-" * 60)
    
    while node.running:
        try:
            cmd = input(f"{node.node_id}> ").strip()
            
            if not cmd:
                continue
            elif cmd == 'stop' or cmd == 'quit':
                break
            elif cmd == 'status':
                node.print_status()
            elif cmd == 'peers':
                print(f"Connected peers: {node.peers}")
            elif cmd == 'chain':
                print(f"Blockchain ({len(node.blockchain)} blocks):")
                for block in node.blockchain[-5:]:  # Show last 5 blocks
                    print(f"  #{block.index}: {block.data} (hash: {block.hash[:8]}...)")
            elif cmd.startswith('add '):
                data = cmd[4:]
                node.add_block(data)
            elif cmd.startswith('connect '):
                addr = cmd[8:]
                if ':' in addr:
                    host, port = addr.split(':')
                    node.connect_to_peer(host, int(port))
                else:
                    print("Usage: connect <host:port>")
            elif cmd == 'help':
                print("Available commands:")
                print("  status              - Show node status")
                print("  peers               - List connected peers")
                print("  chain               - Show blockchain")
                print("  add <data>          - Add new block with data")
                print("  connect <host:port> - Connect to peer")
                print("  stop                - Stop node")
            else:
                print(f"Unknown command: {cmd}. Type 'help' for available commands.")
        
        except KeyboardInterrupt:
            break
        except EOFError:
            break
        except Exception as e:
            print(f"Error: {e}")
    
    node.stop()

def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description='Simple P2P Blockchain Node')
    parser.add_argument('--port', type=int, default=8333, help='P2P port (default: 8333)')
    parser.add_argument('--host', type=str, default='localhost', help='Host address (default: localhost)')
    parser.add_argument('--connect', type=str, help='Bootstrap node to connect to (host:port)')
    parser.add_argument('--node-id', type=str, help='Node identifier')
    
    args = parser.parse_args()
    
    # Create and start node
    node = SimpleP2PNode(
        host=args.host,
        port=args.port,
        node_id=args.node_id
    )
    
    print(f"🚀 Starting blockchain node on {args.host}:{args.port}")
    
    if node.start():
        print(f"✅ Node started successfully")
        
        # Connect to bootstrap node if specified
        if args.connect:
            if ':' in args.connect:
                host, port = args.connect.split(':')
                print(f"🔗 Connecting to bootstrap node {host}:{port}...")
                time.sleep(2)  # Give our server time to start
                
                if node.connect_to_peer(host, int(port)):
                    print(f"✅ Connected to bootstrap node")
                else:
                    print(f"❌ Failed to connect to bootstrap node")
        
        # Run interactive mode
        try:
            run_interactive_node(node)
        except KeyboardInterrupt:
            print("\n🔔 Received interrupt signal")
        
    else:
        print("❌ Failed to start node")
    
    print("👋 Goodbye!")

if __name__ == '__main__':
    main()