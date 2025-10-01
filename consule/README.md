# 🔗 Clean Blockchain Implementation - consule/

This directory contains the clean, working multi-node blockchain implementation.

## 🚀 Quick Start

### Start Network
```bash
# PowerShell (Recommended)
.\start_multi_nodes.ps1

# Batch file
start_multi_nodes.bat

# Manual start
python start_simple_network.py
```

### Test Network
```bash
python test_simple_network.py      # Basic connectivity
python test_p2p_connections.py     # P2P communication  
python test_blockchain_sync.py     # Blockchain sync
```

## 📁 Files Overview

| File | Purpose | Status |
|------|---------|--------|
| `simple_blockchain.py` | Core P2P blockchain node | ✅ Working |
| `start_simple_network.py` | Multi-node launcher | ✅ Working |  
| `start_multi_nodes.ps1` | PowerShell launcher | ✅ Working |
| `start_multi_nodes.bat` | Batch launcher | ✅ Working |
| `test_simple_network.py` | Connectivity test | ✅ Passing |
| `test_p2p_connections.py` | P2P test | ✅ Passing |
| `test_blockchain_sync.py` | Sync test | ✅ Passing |
| `README.md` | This documentation | ✅ Current |

## 🎮 Interactive Commands

When running a node:
- `status` - Node status and chain info
- `peers` - Connected peer list
- `chain` - Display full blockchain
- `add <data>` - Create new block
- `quit` - Exit node

## 🧪 Expected Test Results

```
✅ 3/3 nodes running and accepting connections
✅ All nodes can communicate via P2P
✅ Blockchain synchronization working
🎉 SUCCESS: Multi-node network fully operational!
```

## 🏗️ Network Architecture

- **Bootstrap Node**: localhost:8333 (Coordinator)
- **Node 2**: localhost:8334 (Peer)  
- **Node 3**: localhost:8335 (Peer)
- **Protocol**: JSON over TCP sockets
- **Consensus**: Simple validation

---

**Status**: ✅ **development** - Clean, tested, functional blockchain network