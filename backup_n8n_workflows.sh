#!/bin/bash
#
# N8N Workflow Backup Script
# Downloads all workflows from your n8n instance with folder organization
# Uses UV for fast Python package management
#

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}================================================${NC}"
echo -e "${BLUE}        N8N WORKFLOW BACKUP SCRIPT${NC}"
echo -e "${BLUE}================================================${NC}"
echo ""

# Check if N8N_API_KEY is set
if [ -z "$N8N_API_KEY" ]; then
    echo -e "${RED}ERROR: N8N_API_KEY environment variable is not set!${NC}"
    echo ""
    echo "Please set your API key first:"
    echo "  export N8N_API_KEY='your-api-key-here'"
    echo ""
    echo "You can find your API key in n8n:"
    echo "  Settings → API → Generate new API key"
    exit 1
fi

# Check if uv is installed
if ! command -v uv &> /dev/null; then
    echo -e "${YELLOW}UV is not installed. Installing now...${NC}"
    echo ""
    
    # Install uv
    if command -v curl &> /dev/null; then
        curl -LsSf https://astral.sh/uv/install.sh | sh
    else
        echo -e "${RED}ERROR: curl is required to install uv${NC}"
        echo "Please install uv manually:"
        echo "  https://docs.astral.sh/uv/getting-started/installation/"
        exit 1
    fi
    
    # Source the new PATH
    export PATH="$HOME/.cargo/bin:$PATH"
    
    # Verify installation
    if ! command -v uv &> /dev/null; then
        echo -e "${RED}Failed to install uv. Please install manually.${NC}"
        exit 1
    fi
    
    echo -e "${GREEN}✓ UV installed successfully!${NC}"
    echo ""
fi

# Get script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PYTHON_SCRIPT="${SCRIPT_DIR}/download_n8n_workflows.py"

# Check if Python script exists
if [ ! -f "$PYTHON_SCRIPT" ]; then
    echo -e "${RED}ERROR: Python script not found at ${PYTHON_SCRIPT}${NC}"
    exit 1
fi

# Run the Python script with uv
echo -e "${GREEN}Starting backup...${NC}"
echo ""
uv run "$PYTHON_SCRIPT"

# Check exit code
if [ $? -eq 0 ]; then
    echo ""
    echo -e "${GREEN}✓ Backup completed successfully!${NC}"
else
    echo ""
    echo -e "${RED}✗ Backup failed. Check the output above for details.${NC}"
    exit 1
fi
