# Multi-Node Blockchain Tester for Windows PowerShell
# Starts multiple blockchain nodes in separate windows

param(
    [switch]$Stop,
    [int]$NodeCount = 3
)

$ErrorActionPreference = "Stop"
$BaseDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$PythonExe = "$BaseDir\..\.venv\Scripts\python.exe"

function Start-BlockchainNode {
    param($ConfigFile, $NodeName, $WindowTitle)
    
    Write-Host "🚀 Starting $NodeName..." -ForegroundColor Green
    
    # Set environment variable and start in new window
    $env:CIVIC_CONFIG = $ConfigFile
    $Command = "& '$PythonExe' main.py --interactive"
    
    Start-Process powershell -ArgumentList @(
        "-NoExit",
        "-Command", 
        "cd '$BaseDir'; `$env:CIVIC_CONFIG='$ConfigFile'; $Command"
    ) -WindowStyle Normal
    
    Write-Host "✅ $NodeName started in new window" -ForegroundColor Green
    Start-Sleep -Seconds 2
}

function Stop-AllNodes {
    Write-Host "🛑 Stopping all blockchain nodes..." -ForegroundColor Yellow
    
    # Find and stop all python processes running main.py
    $Processes = Get-Process python -ErrorAction SilentlyContinue | Where-Object {
        $_.CommandLine -like "*main.py*"
    }
    
    foreach ($Process in $Processes) {
        Write-Host "   Stopping PID $($Process.Id)..." -ForegroundColor Yellow
        Stop-Process -Id $Process.Id -Force -ErrorAction SilentlyContinue
    }
    
    Write-Host "✅ All nodes stopped" -ForegroundColor Green
}

# Main execution
Write-Host "🌐 CIVIC ENGAGEMENT MULTI-NODE TESTER" -ForegroundColor Cyan
Write-Host "=" * 40 -ForegroundColor Cyan

if ($Stop) {
    Stop-AllNodes
    exit 0
}

# Check if Python executable exists
if (-not (Test-Path $PythonExe)) {
    Write-Host "❌ Python executable not found: $PythonExe" -ForegroundColor Red
    exit 1
}

# Check if we're in the right directory
if (-not (Test-Path "main.py")) {
    Write-Host "❌ main.py not found. Please run from consule directory" -ForegroundColor Red
    exit 1
}

Write-Host "📋 Starting $NodeCount blockchain nodes..." -ForegroundColor Cyan
Write-Host "   Each node will open in a separate PowerShell window" -ForegroundColor Gray
Write-Host ""

# Start nodes
Start-BlockchainNode "config/blockchain_config.json" "Node 1 (Bootstrap)" "Blockchain Node 1"
Start-Sleep -Seconds 3

if ($NodeCount -ge 2) {
    Start-BlockchainNode "config/node2_config.json" "Node 2" "Blockchain Node 2"
    Start-Sleep -Seconds 3
}

if ($NodeCount -ge 3) {
    Start-BlockchainNode "config/node3_config.json" "Node 3" "Blockchain Node 3"
    Start-Sleep -Seconds 3
}

Write-Host ""
Write-Host "🎯 Multi-node network started!" -ForegroundColor Green
Write-Host "📡 Network topology:" -ForegroundColor Cyan
Write-Host "   Node 1 (Port 8333) ← Bootstrap Node" -ForegroundColor Gray
if ($NodeCount -ge 2) {
    Write-Host "   Node 2 (Port 8334) → Connects to Node 1" -ForegroundColor Gray
}
if ($NodeCount -ge 3) {
    Write-Host "   Node 3 (Port 8335) → Connects to Node 1 & 2" -ForegroundColor Gray
}

Write-Host ""
Write-Host "💡 Testing suggestions:" -ForegroundColor Yellow
Write-Host "   1. Try 'peers' command in each node to see connections" -ForegroundColor Gray
Write-Host "   2. Try 'status' command to check node health" -ForegroundColor Gray
Write-Host "   3. Try 'chain' command to see blockchain sync" -ForegroundColor Gray
Write-Host "   4. Use 'validators' to check consensus" -ForegroundColor Gray
Write-Host ""
Write-Host "🛑 To stop all nodes: .\start_multi_nodes.ps1 -Stop" -ForegroundColor Red