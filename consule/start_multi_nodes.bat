@echo off
echo 🌐 STARTING CIVIC ENGAGEMENT MULTI-NODE NETWORK
echo ================================================

set BASE_DIR=%~dp0
set PYTHON_EXE=%BASE_DIR%..\\.venv\Scripts\python.exe
cd /d "%BASE_DIR%"

echo 🚀 Starting Node 1 (Bootstrap) on port 8333...
set CIVIC_CONFIG=config/blockchain_config.json
start "Blockchain Node 1" cmd /k "%PYTHON_EXE%" main.py --interactive

echo ⏳ Waiting 5 seconds for Node 1 to start...
timeout /t 5 /nobreak > nul

echo 🚀 Starting Node 2 on port 8334...
set CIVIC_CONFIG=config/node2_config.json
start "Blockchain Node 2" cmd /k "%PYTHON_EXE%" main.py --interactive

echo ⏳ Waiting 3 seconds for Node 2 to start...
timeout /t 3 /nobreak > nul

echo 🚀 Starting Node 3 on port 8335...
set CIVIC_CONFIG=config/node3_config.json
start "Blockchain Node 3" cmd /k "%PYTHON_EXE%" main.py --interactive

echo.
echo ✅ All nodes starting in separate windows!
echo 📡 Network topology:
echo    Node 1 (Port 8333) ← Bootstrap Node
echo    Node 2 (Port 8334) → Connects to Node 1
echo    Node 3 (Port 8335) → Connects to Node 1 ^& 2
echo.
echo 💡 Testing suggestions:
echo    1. Try 'peers' command in each node to see connections
echo    2. Try 'status' command to check node health
echo    3. Try 'chain' command to see blockchain sync
echo    4. Use 'validators' to check consensus
echo.
pause