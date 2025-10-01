#!/usr/bin/env python3
"""
SIMPLE NETWORK CONNECTIVITY TEST
Test if the simple blockchain nodes are running and connected
"""

import socket
import time

def check_port(host, port):
    """Check if a port is open"""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(2)
        result = sock.connect_ex((host, port))
        sock.close()
        return result == 0
    except:
        return False

def test_network():
    """Test the simple blockchain network"""
    print("🔍 SIMPLE BLOCKCHAIN NETWORK TEST")
    print("=" * 40)
    
    nodes = [
        (8333, "Bootstrap Node"),
        (8334, "Node 2"),
        (8335, "Node 3")
    ]
    
    running_nodes = 0
    
    for port, name in nodes:
        if check_port('localhost', port):
            print(f"✅ {name} (port {port}) - RUNNING")
            running_nodes += 1
        else:
            print(f"❌ {name} (port {port}) - NOT RUNNING")
    
    print(f"\n📊 NETWORK STATUS:")
    print(f"   Running nodes: {running_nodes}/{len(nodes)}")
    
    if running_nodes == 0:
        print("   🚨 No nodes running! Start with: python start_simple_network.py")
    elif running_nodes == 1:
        print("   ⚠️  Only one node - limited P2P functionality")
    elif running_nodes >= 2:
        print("   ✅ Multi-node network active!")
        print("\n🧪 TESTING SUGGESTIONS:")
        print("   1. In any node, type: add Test Block")
        print("   2. In other nodes, type: chain")
        print("   3. Verify the block appears in all nodes")
    
    return running_nodes

if __name__ == '__main__':
    test_network()