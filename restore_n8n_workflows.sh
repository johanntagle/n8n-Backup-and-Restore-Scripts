#!/bin/bash
# N8N Workflow Restore - Bash Wrapper
# Restores workflows from backup to n8n instance

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Check if UV is installed
if ! command -v uv &> /dev/null; then
    echo -e "${YELLOW}UV not found. Installing UV package manager...${NC}"
    curl -LsSf https://astral.sh/uv/install.sh | sh
    
    # Add UV to PATH for current session
    export PATH="$HOME/.local/bin:$PATH"
    
    if ! command -v uv &> /dev/null; then
        echo -e "${RED}Failed to install UV. Please install manually:${NC}"
        echo "curl -LsSf https://astral.sh/uv/install.sh | sh"
        exit 1
    fi
    echo -e "${GREEN}UV installed successfully${NC}"
fi

# Check for N8N_API_KEY
if [ -z "$N8N_API_KEY" ]; then
    echo -e "${RED}Error: N8N_API_KEY environment variable not set${NC}"
    echo ""
    echo "Usage:"
    echo "  export N8N_API_KEY='your-api-key-here'"
    echo "  $0 [backup_directory]"
    exit 1
fi

# Run the restore script
if [ -n "$1" ]; then
    uv run restore_n8n_workflows.py "$1"
else
    uv run restore_n8n_workflows.py
fi
