#!/usr/bin/env -S uv run --quiet --script
# /// script
# requires-python = ">=3.10"
# dependencies = [
#     "requests",
# ]
# ///
"""
N8N Workflow Restore Script
Restores workflows from backup to n8n instance

Configuration:
    Create a .env file with:
    N8N_API_URL=https://your-n8n-instance.com
    N8N_API_KEY=your-api-key

Usage:
    uv run restore_n8n_workflows.py [backup_directory]

Examples:
    uv run restore_n8n_workflows.py
    uv run restore_n8n_workflows.py ~/n8n-workflows-backup/backup_20260112_111221
"""

import os
import sys
import json
import requests
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any, Optional

# Import configuration module
from n8n_config import get_n8n_api_url, get_n8n_api_key, get_backup_dir

# Configuration from .env file or environment
N8N_API_URL = get_n8n_api_url()
N8N_API_KEY = get_n8n_api_key()
BACKUP_BASE_DIR = get_backup_dir()

# ANSI color codes
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    END = '\033[0m'
    BOLD = '\033[1m'

def print_header(text: str):
    """Print colored header"""
    print(f"\n{Colors.HEADER}{Colors.BOLD}{'='*60}")
    print(f"{text.center(60)}")
    print(f"{'='*60}{Colors.END}\n")

def print_success(text: str):
    """Print success message"""
    print(f"{Colors.GREEN}✓ {text}{Colors.END}")

def print_error(text: str):
    """Print error message"""
    print(f"{Colors.RED}✗ {text}{Colors.END}")

def print_warning(text: str):
    """Print warning message"""
    print(f"{Colors.YELLOW}⚠ {text}{Colors.END}")

def print_info(text: str):
    """Print info message"""
    print(f"{Colors.CYAN}ℹ {text}{Colors.END}")

class N8NWorkflowRestore:
    def __init__(self, api_url: str, api_key: str):
        self.api_url = api_url.rstrip('/')
        self.api_key = api_key
        self.session = requests.Session()
        self.session.headers.update({
            'X-N8N-API-KEY': self.api_key,
            'Content-Type': 'application/json'
        })
        
    def get_existing_workflows(self) -> Dict[str, str]:
        """Get map of existing workflow names to IDs"""
        print_info("Fetching existing workflows from n8n...")
        
        existing = {}
        cursor = None
        
        while True:
            url = f"{self.api_url}/api/v1/workflows"
            params = {'limit': 100}
            if cursor:
                params['cursor'] = cursor
            
            try:
                response = self.session.get(url, params=params, timeout=30)
                response.raise_for_status()
                data = response.json()
                
                for workflow in data.get('data', []):
                    name = workflow.get('name', '')
                    wf_id = workflow.get('id', '')
                    if name and wf_id:
                        existing[name] = wf_id
                
                cursor = data.get('nextCursor')
                if not cursor:
                    break
                    
            except requests.exceptions.RequestException as e:
                print_error(f"Failed to fetch existing workflows: {e}")
                return {}
        
        print_info(f"Found {len(existing)} existing workflows")
        return existing

    def clean_workflow_for_api(self, workflow_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Clean workflow data before sending to API for creating new workflow.

        Only keeps fields that are accepted by the POST /api/v1/workflows endpoint.
        """
        # ONLY keep fields that n8n API accepts when creating workflows
        allowed_fields = [
            'name',         # Required
            'nodes',        # Required
            'connections',  # Required
        ]

        # Create a copy with only allowed fields
        cleaned_data = {k: v for k, v in workflow_data.items() if k in allowed_fields}

        # Add settings with only accepted fields
        # Based on API docs, most settings fields are NOT accepted when creating
        # We include only the minimal settings object
        cleaned_data['settings'] = {}

        return cleaned_data

    def create_workflow(self, workflow_data: Dict[str, Any]) -> Optional[str]:
        """Create a new workflow"""
        url = f"{self.api_url}/api/v1/workflows"

        # Clean the workflow data before sending to API
        cleaned_data = self.clean_workflow_for_api(workflow_data)

        try:
            response = self.session.post(url, json=cleaned_data, timeout=30)
            response.raise_for_status()
            result = response.json()
            return result.get('id')
        except requests.exceptions.RequestException as e:
            print_error(f"Failed to create workflow: {e}")
            if hasattr(e.response, 'text'):
                print_error(f"Response: {e.response.text}")
            return None
    
    def update_workflow(self, workflow_id: str, workflow_data: Dict[str, Any]) -> bool:
        """Update an existing workflow"""
        url = f"{self.api_url}/api/v1/workflows/{workflow_id}"
        
        try:
            response = self.session.put(url, json=workflow_data, timeout=30)
            response.raise_for_status()
            return True
        except requests.exceptions.RequestException as e:
            print_error(f"Failed to update workflow: {e}")
            if hasattr(e.response, 'text'):
                print_error(f"Response: {e.response.text}")
            return False
    
    def find_backup_files(self, backup_dir: Path) -> List[Path]:
        """Find all workflow JSON files in backup directory"""
        workflow_files = []
        
        for file_path in backup_dir.rglob("*.json"):
            # Skip index.json and README files
            if file_path.name in ['index.json', 'README.json']:
                continue
            # Skip hidden files
            if file_path.name.startswith('.'):
                continue
            workflow_files.append(file_path)
        
        return sorted(workflow_files)
    
    def restore_workflow(self, file_path: Path, existing_workflows: Dict[str, str], 
                        mode: str = 'skip') -> Dict[str, Any]:
        """Restore a single workflow from backup file"""
        result = {
            'file': file_path.name,
            'status': 'unknown',
            'action': None,
            'workflow_id': None
        }
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                backup_data = json.load(f)
            
            # Extract workflow data
            if 'workflow' in backup_data:
                workflow_data = backup_data['workflow']
                metadata = backup_data.get('metadata', {})
            else:
                # Assume entire file is workflow data
                workflow_data = backup_data
                metadata = {}
            
            workflow_name = workflow_data.get('name', 'Unnamed')
            
            # Check if workflow exists
            existing_id = existing_workflows.get(workflow_name)
            
            if existing_id:
                if mode == 'skip':
                    result['status'] = 'skipped'
                    result['action'] = 'exists'
                    result['workflow_id'] = existing_id
                    print(f"  ⊘ Skipped: {workflow_name} (already exists)")
                elif mode == 'update':
                    if self.update_workflow(existing_id, workflow_data):
                        result['status'] = 'success'
                        result['action'] = 'updated'
                        result['workflow_id'] = existing_id
                        print(f"  ↻ Updated: {workflow_name}")
                    else:
                        result['status'] = 'failed'
                        result['action'] = 'update_failed'
                        print_error(f"Failed to update: {workflow_name}")
                elif mode == 'rename':
                    # Create with new name
                    new_name = f"{workflow_name} (restored {datetime.now().strftime('%Y%m%d_%H%M%S')})"
                    workflow_data['name'] = new_name
                    new_id = self.create_workflow(workflow_data)
                    if new_id:
                        result['status'] = 'success'
                        result['action'] = 'created_renamed'
                        result['workflow_id'] = new_id
                        print(f"  + Created: {new_name}")
                    else:
                        result['status'] = 'failed'
                        result['action'] = 'create_failed'
                        print_error(f"Failed to create: {new_name}")
            else:
                # Create new workflow
                new_id = self.create_workflow(workflow_data)
                if new_id:
                    result['status'] = 'success'
                    result['action'] = 'created'
                    result['workflow_id'] = new_id
                    print(f"  + Created: {workflow_name}")
                else:
                    result['status'] = 'failed'
                    result['action'] = 'create_failed'
                    print_error(f"Failed to create: {workflow_name}")
            
        except Exception as e:
            result['status'] = 'error'
            result['action'] = 'exception'
            print_error(f"Error processing {file_path.name}: {e}")
        
        return result
    
    def restore_from_backup(self, backup_dir: Path, mode: str = 'skip', 
                           dry_run: bool = False) -> Dict[str, Any]:
        """Restore all workflows from backup directory"""
        stats = {
            'total': 0,
            'created': 0,
            'updated': 0,
            'skipped': 0,
            'failed': 0,
            'results': []
        }
        
        # Find all workflow files
        workflow_files = self.find_backup_files(backup_dir)
        stats['total'] = len(workflow_files)
        
        if stats['total'] == 0:
            print_warning("No workflow files found in backup directory")
            return stats
        
        print_info(f"Found {stats['total']} workflow files to restore")
        
        if dry_run:
            print_warning("DRY RUN MODE - No changes will be made")
            print_info("Workflows that would be restored:")
            for file_path in workflow_files:
                print(f"  • {file_path.relative_to(backup_dir)}")
            return stats
        
        # Get existing workflows
        existing_workflows = self.get_existing_workflows()
        
        print_info(f"Restoring workflows (mode: {mode})...")
        
        # Restore each workflow
        for file_path in workflow_files:
            result = self.restore_workflow(file_path, existing_workflows, mode)
            stats['results'].append(result)
            
            # Update counters
            if result['status'] == 'success':
                if result['action'] in ['created', 'created_renamed']:
                    stats['created'] += 1
                elif result['action'] == 'updated':
                    stats['updated'] += 1
            elif result['status'] == 'skipped':
                stats['skipped'] += 1
            elif result['status'] in ['failed', 'error']:
                stats['failed'] += 1
        
        return stats

def select_backup_dir() -> Optional[Path]:
    """Interactively select a backup directory"""
    if not BACKUP_BASE_DIR.exists():
        print_error(f"Backup directory not found: {BACKUP_BASE_DIR}")
        return None
    
    # Find all backup directories
    backup_dirs = sorted([d for d in BACKUP_BASE_DIR.iterdir() 
                         if d.is_dir() and d.name.startswith('backup_')],
                        reverse=True)
    
    if not backup_dirs:
        print_error(f"No backup directories found in {BACKUP_BASE_DIR}")
        return None
    
    print_info("Available backups:")
    for i, backup_dir in enumerate(backup_dirs, 1):
        # Read index if available
        index_file = backup_dir / "index.json"
        workflow_count = "?"
        if index_file.exists():
            try:
                with open(index_file) as f:
                    index = json.load(f)
                    workflow_count = index.get('backup_info', {}).get('total_workflows', '?')
            except:
                pass
        
        print(f"  {i}. {backup_dir.name} ({workflow_count} workflows)")
    
    while True:
        try:
            choice = input(f"\nSelect backup (1-{len(backup_dirs)}) or 'q' to quit: ").strip()
            if choice.lower() == 'q':
                return None
            
            idx = int(choice) - 1
            if 0 <= idx < len(backup_dirs):
                return backup_dirs[idx]
            else:
                print_error("Invalid selection")
        except (ValueError, KeyboardInterrupt):
            print()
            return None

def select_restore_mode() -> Optional[str]:
    """Interactively select restore mode"""
    print_info("Restore mode:")
    print("  1. skip     - Skip workflows that already exist (default)")
    print("  2. update   - Update existing workflows with backup data")
    print("  3. rename   - Create new workflows with renamed duplicates")
    
    while True:
        try:
            choice = input("\nSelect mode (1-3) or press Enter for default: ").strip()
            if not choice:
                return 'skip'
            
            modes = {'1': 'skip', '2': 'update', '3': 'rename'}
            if choice in modes:
                return modes[choice]
            else:
                print_error("Invalid selection")
        except KeyboardInterrupt:
            print()
            return None

def main():
    print_header("N8N WORKFLOW RESTORE")
    
    # Check API key
    if not N8N_API_KEY:
        print_error("N8N_API_KEY not configured!")
        print_info("Set it in .env file or with: export N8N_API_KEY='your-api-key'")
        sys.exit(1)
    
    # Determine backup directory
    if len(sys.argv) > 1:
        backup_dir = Path(sys.argv[1])
        if not backup_dir.exists():
            print_error(f"Backup directory not found: {backup_dir}")
            sys.exit(1)
    else:
        backup_dir = select_backup_dir()
        if not backup_dir:
            print_warning("Restore cancelled")
            sys.exit(0)
    
    print_success(f"Backup directory: {backup_dir}")
    
    # Select restore mode
    mode = select_restore_mode()
    if not mode:
        print_warning("Restore cancelled")
        sys.exit(0)
    
    print_success(f"Restore mode: {mode}")
    
    # Confirm
    print()
    confirm = input(f"Restore workflows from {backup_dir.name}? (yes/no): ").strip().lower()
    if confirm not in ['yes', 'y']:
        print_warning("Restore cancelled")
        sys.exit(0)
    
    # Initialize restorer
    restorer = N8NWorkflowRestore(N8N_API_URL, N8N_API_KEY)
    
    # Restore workflows
    stats = restorer.restore_from_backup(backup_dir, mode=mode)
    
    # Print summary
    print_header("RESTORE COMPLETE")
    
    print_success(f"Total workflows: {stats['total']}")
    if stats['created'] > 0:
        print_success(f"Created: {stats['created']}")
    if stats['updated'] > 0:
        print_success(f"Updated: {stats['updated']}")
    if stats['skipped'] > 0:
        print_info(f"Skipped: {stats['skipped']}")
    if stats['failed'] > 0:
        print_error(f"Failed: {stats['failed']}")
    
    print()
    print_info(f"Target: {N8N_API_URL}")

if __name__ == "__main__":
    main()
