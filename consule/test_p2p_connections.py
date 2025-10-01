#!/usr/bin/env python3
"""
P2P CONNECTION TESTER
Test actual peer connections between blockchain nodes
"""

import socket
import json
import time

def test_node_connection(host, port, node_name):
    """Test connection to a node and get its status"""
    try:
        # Connect to the node
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(5)
        sock.connect((host, port))
        
        # Send a hello message
        hello_msg = {
            'type': 'hello',
            'node_id': 'test-client',
            'blockchain_length': 0
        }
        
        sock.send(json.dumps(hello_msg).encode())
        
        # Try to receive response (nodes might not respond to test clients)
        sock.settimeout(2)
        try:
            response = sock.recv(1024).decode()
            if response:
                print(f"✅ {node_name} responded: {response[:100]}...")
            else:
                print(f"✅ {node_name} accepted connection (no response)")
        except socket.timeout:
            print(f"✅ {node_name} accepted connection (timeout on response)")
        
        sock.close()
        return True
        
    except Exception as e:
        print(f"❌ {node_name} connection failed: {e}")
        return False

def test_all_connections():
    """Test connections to all nodes"""
    print("🔍 TESTING P2P CONNECTIONS")
    print("=" * 40)
    
    nodes = [
        ('localhost', 8333, 'Bootstrap Node'),
        ('localhost', 8334, 'Node 2'),
        ('localhost', 8335, 'Node 3')
    ]
    
    successful_connections = 0
    
    for host, port, name in nodes:
        if test_node_connection(host, port, name):
            successful_connections += 1
        time.sleep(1)  # Brief pause between tests
    
    print(f"\n📊 CONNECTION TEST RESULTS:")
    print(f"   Successful connections: {successful_connections}/{len(nodes)}")
    
    if successful_connections == len(nodes):
        print("   🎉 All nodes are accepting P2P connections!")
        print("\n💡 NEXT STEPS:")
        print("   1. Open the node windows created by start_simple_network.py")
        print("   2. In Node 2 or Node 3 window, type 'peers' to see connections")
        print("   3. In any node, type 'add My First Block' to create a block")
        print("   4. In other nodes, type 'chain' to verify block propagation")
    else:
        print("   ⚠️ Some nodes are not accepting connections")

if __name__ == '__main__':
    test_all_connections()