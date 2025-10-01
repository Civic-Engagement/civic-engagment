#!/usr/bin/env python3
"""
SIMPLE MULTI-NODE NETWORK STARTER
Start a clean 3-node blockchain network for testing
"""

import subprocess
import time
import sys
import os

def start_node(port, node_id, connect_to=None):
    """Start a blockchain node"""
    cmd = [
        sys.executable,
        'simple_blockchain.py',
        '--port', str(port),
        '--node-id', node_id
    ]
    
    if connect_to:
        cmd.extend(['--connect', connect_to])
    
    print(f"🚀 Starting {node_id} on port {port}...")
    
    # Start in new window on Windows
    if os.name == 'nt':
        subprocess.Popen([
            'start', 'powershell', '-NoExit', '-Command',
            f"cd '{os.getcwd()}'; {' '.join(cmd)}"
        ], shell=True)
    else:
        # For Unix-like systems
        subprocess.Popen(['gnome-terminal', '--', 'bash', '-c', f"cd {os.getcwd()} && {' '.join(cmd)}; bash"])

def main():
    print("🌐 STARTING SIMPLE MULTI-NODE BLOCKCHAIN NETWORK")
    print("=" * 60)
    
    # Start Node 1 (Bootstrap)
    start_node(8333, "bootstrap-node")
    print("⏳ Waiting 3 seconds for bootstrap node to initialize...")
    time.sleep(3)
    
    # Start Node 2
    start_node(8334, "node-2", "localhost:8333")
    print("⏳ Waiting 2 seconds for node 2 to connect...")
    time.sleep(2)
    
    # Start Node 3
    start_node(8335, "node-3", "localhost:8333")
    print("⏳ Waiting 2 seconds for node 3 to connect...")
    time.sleep(2)
    
    print("\n✅ All nodes started!")
    print("\n📋 TEST INSTRUCTIONS:")
    print("1. In any node window, type 'status' to see node info")
    print("2. Type 'peers' to see connected peers")
    print("3. Type 'add Hello World' to create a new block")
    print("4. Type 'chain' to see the blockchain")
    print("5. Watch how blocks propagate between nodes!")
    print("\n🔗 EXPECTED CONNECTIONS:")
    print("   Node 2 → Bootstrap Node (8333)")
    print("   Node 3 → Bootstrap Node (8333)")
    print("\n⌨️  Commands in each node:")
    print("   status, peers, chain, add <data>, help, stop")

if __name__ == '__main__':
    main()