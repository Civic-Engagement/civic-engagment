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

### User Management
```bash
python user_registration_cli.py    # Register new users
python blockchain_user_system.py   # Integrated user/blockchain system
```

## 📁 Files Overview

| File | Purpose | Status |
|------|---------|--------|
| **Blockchain Core** | | |
| `simple_blockchain.py` | Core P2P blockchain node | ✅ Working |
| `start_simple_network.py` | Multi-node launcher | ✅ Working |  
| `start_multi_nodes.ps1` | PowerShell launcher | ✅ Working |
| `start_multi_nodes.bat` | Batch launcher | ✅ Working |
| **User Management** | | |
| `user_manager.py` | Complete user registration system | ✅ Working |
| `user_registration_cli.py` | Interactive user registration | ✅ Working |
| `organization_manager.py` | Organization creation/management | ✅ Working |
| `blockchain_user_system.py` | Integrated blockchain + users | ✅ Working |
| **Testing** | | |
| `test_simple_network.py` | Connectivity test | ✅ Passing |
| `test_p2p_connections.py` | P2P test | ✅ Passing |
| `test_blockchain_sync.py` | Sync test | ✅ Passing |
| **Documentation** | | |
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

## 👥 User Management Features

### 📝 User Registration
- **Legal Identity**: First, middle, last name + date of birth
- **Contact Info**: Multiple emails (required) and phone numbers (optional)
- **Addresses**: Multiple complete addresses with types (residence, mailing, work)
- **Citizenship**: Multiple countries of citizenship
- **Verification**: Email verification system with tokens

### 🏢 Organizations
- **Create Organizations**: Government, non-profit, community, business types
- **Membership Requests**: Users can request to join organizations
- **Role Management**: Member, moderator, admin, owner roles
- **Approval Workflow**: Configurable approval process for new members

### 🔗 Blockchain Integration
- **Action Logging**: All user actions logged to blockchain
- **Transparent History**: Immutable audit trail of registrations and activities
- **Decentralized Identity**: User data stored locally with blockchain verification

---

**Status**: ✅ **development** - Clean, tested, functional blockchain network