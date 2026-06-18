#!/usr/bin/env bash
# =======================================================================
# ENTERPRISE CONTEXT CONTAINER ENVIRONMENT CLEANUP SCRIPT
# Target: Headless maintenance routine for embedded open PLC nodes
# =======================================================================

set -e # Terminate script instantly if any command encounters an error

echo "🧹 Initializing headless environment log cleanup..."

# Define your testing log output locations inside the workspace directory
LOG_DIR="/var/log/revolutionary_technology"
WORK_DIR="/opt/revolutionary_technology"

# 1. Clear out temporary runtime testing log records if they exist
if [ -d "$LOG_DIR" ]; then
    echo "  Wiping runtime log directory logs under $LOG_DIR..."
    find "$LOG_DIR" -type f -name "*.log" -delete
    find "$LOG_DIR" -type f -name "*.out" -delete
fi

# 2. Purge compiled python caching folders to ensure a clean slate next init run
echo "  Clearing cached bytecode repositories..."
find "$WORK_DIR" -type d -name "__pycache__" -exec rm -rf {} +
find "$WORK_DIR" -type f -name "*.pyc" -delete
find "$WORK_DIR" -type f -name "*.pyo" -delete

# 3. Clean down standard Linux error report dumps to save memory bounds
echo "  Emptying embedded core dump caches..."
rm -f /var/crash/*
rm -f "$WORK_DIR"/*.tmp

echo "✅ SUCCESS: All temporary testing trails cleared from the container layout."
exit 0

