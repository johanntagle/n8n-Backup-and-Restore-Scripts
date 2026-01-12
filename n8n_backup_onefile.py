#!/usr/bin/env -S uv run --quiet --script
# /// script
# requires-python = ">=3.10"
# dependencies = [
#     "requests",
# ]
# ///
"""
🚀 N8N Workflow Backup - One-File Edition

Ultra-portable single-file backup script. Just run it!

Usage:
    export N8N_API_KEY='your-key'
    uv run n8n_backup_onefile.py

Or without uv:
    chmod +x n8n_backup_onefile.py
    ./n8n_backup_onefile.py
"""

import os
import sys
import json
import requests
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any

# ============================================================================
# CONFIGURATION - Edit these if needed
# ============================================================================

N8N_API_URL = "https://n8ndev.aiautomationsfactory.com"
N8N_API_KEY = os.environ.get("N8N_API_KEY", "")
OUTPUT_DIR = Path.home() / "n8n-workflows-backup"
BACKUP_TIMESTAMP = datetime.now().strftime("%Y%m%d_%H%M%S")

# ============================================================================
# COLOR OUTPUT
# ============================================================================

class Colors:
    BLUE = '\033[0;34m'
    GREEN = '\033[0;32m'
    YELLOW = '\033[1;33m'
    RED = '\033[0;31m'
    BOLD = '\033[1m'
    RESET = '\033[0m'

def print_header(text: str):
    print(f"\n{Colors.BLUE}{Colors.BOLD}{'=' * 60}{Colors.RESET}")
    print(f"{Colors.BLUE}{Colors.BOLD}{text:^60}{Colors.RESET}")
    print(f"{Colors.BLUE}{Colors.BOLD}{'=' * 60}{Colors.RESET}\n")

def print_success(text: str):
    print(f"{Colors.GREEN}✓ {text}{Colors.RESET}")

def print_error(text: str):
    print(f"{Colors.RED}✗ {text}{Colors.RESET}")

def print_info(text: str):
    print(f"{Colors.BLUE}ℹ {text}{Colors.RESET}")

def print_warning(text: str):
    print(f"{Colors.YELLOW}⚠ {text}{Colors.RESET}")

# ============================================================================
# MAIN BACKUP CLASS
# ============================================================================

class N8NBackup:
    def __init__(self, api_url: str, api_key: str, output_dir: Path):
        self.api_url = api_url.rstrip('/')
        self.api_key = api_key
        self.output_dir = output_dir
        self.session = requests.Session()
        self.session.headers.update({
            'X-N8N-API-KEY': self.api_key,
            'Content-Type': 'application/json'
        })
        
    def get_all_workflows(self) -> List[Dict[str, Any]]:
        """Fetch all workflows"""
        print_info(f"Fetching workflows from {self.api_url}...")
        
        all_workflows = []
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
                
                workflows = data.get('data', [])
                all_workflows.extend(workflows)
                
                print(f"  → Fetched {len(workflows)} workflows (total: {len(all_workflows)})")
                
                if not data.get('nextCursor'):
                    break
                cursor = data['nextCursor']
                
            except requests.exceptions.RequestException as e:
                print_error(f"Failed to fetch workflows: {e}")
                return []
        
        return all_workflows
    
    def get_workflow_details(self, workflow_id: str) -> Dict[str, Any]:
        """Fetch full workflow details"""
        url = f"{self.api_url}/api/v1/workflows/{workflow_id}"
        
        try:
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print_error(f"Failed to fetch workflow {workflow_id}: {e}")
            return None
    
    def get_workflow_project(self, workflow_id: str, workflow_summary: Dict) -> str:
        """Get the project/user name for a workflow"""
        workflow_data = self.get_workflow_details(workflow_id)
        
        project_name = 'Unknown Project'
        if workflow_data:
            shared = workflow_data.get('shared', [])
            if shared and len(shared) > 0:
                project = shared[0].get('project', {})
                project_name = project.get('name', 'Unknown Project')
                project_type = project.get('type', '')
                
                # Clean up personal project names
                if project_type == 'personal' and '<' in project_name:
                    project_name = project_name.split('<')[0].strip()
        
        return project_name
    
    def organize_by_folders(self, workflows: List[Dict]) -> Dict[str, List[Dict]]:
        """Organize workflows by User/Project > Tags hierarchy"""
        # Filter out archived workflows entirely
        active_workflows = [w for w in workflows if not w.get('isArchived', False)]
        
        archived_count = len(workflows) - len(active_workflows)
        print_info(f"Found {len(active_workflows)} active workflows")
        if archived_count > 0:
            print_info(f"Skipping {archived_count} archived workflows")
        
        organized = {}
        
        print_info("Organizing by user and tags...")
        
        for workflow in active_workflows:
            workflow_id = workflow['id']
            workflow_name = workflow.get('name', 'Unnamed')
            
            # Get project/user
            project_name = self.get_workflow_project(workflow_id, workflow)
            # Sanitize project name for filesystem
            project_name_safe = self.sanitize_filename(project_name)
            
            # Get tags
            tags = workflow.get('tags', [])
            
            if tags:
                # Has tags - organize under Project/Tag
                for tag in tags:
                    tag_name = tag.get('name', 'Untagged')
                    # Sanitize tag name for filesystem
                    tag_name_safe = self.sanitize_filename(tag_name)
                    # Use / for folder path (don't sanitize this!)
                    folder_path = f"{project_name_safe}/{tag_name_safe}"
                    
                    if folder_path not in organized:
                        organized[folder_path] = []
                    
                    organized[folder_path].append(workflow)
                    print(f"  → [{project_name}/{tag_name}] {workflow_name}")
            else:
                # No tags - organize under Project/No Tag
                folder_path = f"{project_name_safe}/No Tag"
                if folder_path not in organized:
                    organized[folder_path] = []
                
                organized[folder_path].append(workflow)
                print(f"  → [{project_name}/No Tag] {workflow_name}")
        
        return organized
        
        return organized
    
    def sanitize_filename(self, name: str) -> str:
        """Make filename safe"""
        invalid_chars = '<>:"/\\|?*'
        for char in invalid_chars:
            name = name.replace(char, '_')
        return name.strip()
    
    def download_workflow(self, workflow: Dict, folder_path: str, backup_dir: Path) -> bool:
        """Download single workflow to nested folder structure"""
        workflow_id = workflow['id']
        workflow_name = workflow.get('name', 'Unnamed')
        
        print(f"  → {workflow_name}")
        
        workflow_data = self.get_workflow_details(workflow_id)
        if not workflow_data:
            return False
        
        # Create nested folder path
        full_folder_path = backup_dir / folder_path
        full_folder_path.mkdir(parents=True, exist_ok=True)
        
        safe_name = self.sanitize_filename(workflow_name)
        filename = f"{safe_name}_{workflow_id}.json"
        filepath = full_folder_path / filename
        
        output = {
            'metadata': {
                'downloaded_at': datetime.now().isoformat(),
                'workflow_id': workflow_id,
                'workflow_name': workflow_name,
                'active': workflow.get('active', False),
                'archived': workflow.get('isArchived', False),
                'created_at': workflow.get('createdAt'),
                'updated_at': workflow.get('updatedAt'),
                'tags': [tag.get('name') for tag in workflow.get('tags', [])],
                'node_count': workflow.get('nodeCount', 0)
            },
            'workflow': workflow_data
        }
        
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(output, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            print_error(f"Failed to save {filename}: {e}")
            return False
    
    def create_index(self, backup_dir: Path, organized: Dict, stats: Dict):
        """Create index and README"""
        index = {
            'backup_info': {
                'timestamp': datetime.now().isoformat(),
                'n8n_instance': self.api_url,
                'total_workflows': stats['total'],
                'successful': stats['success'],
                'failed': stats['failed']
            },
            'folders': {
                folder: len(workflows) 
                for folder, workflows in organized.items()
            }
        }
        
        with open(backup_dir / 'index.json', 'w') as f:
            json.dump(index, f, indent=2)
        
        with open(backup_dir / 'README.md', 'w') as f:
            f.write(f"# N8N Workflows Backup\n\n")
            f.write(f"**Date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"**Instance:** {self.api_url}\n")
            f.write(f"**Total:** {stats['total']} workflows\n\n")
            
            for folder, workflows in organized.items():
                f.write(f"## {folder} ({len(workflows)})\n\n")
                for w in workflows:
                    status = "✓" if w.get('active') else "○"
                    f.write(f"- {status} {w['name']}\n")
                f.write("\n")
    
    def run(self):
        """Main backup process"""
        print_header("N8N WORKFLOW BACKUP")
        
        # Validate API key
        if not self.api_key:
            print_error("N8N_API_KEY not set!")
            print_info("Set it with: export N8N_API_KEY='your-key'")
            sys.exit(1)
        
        # Create backup directory
        backup_dir = self.output_dir / f"backup_{BACKUP_TIMESTAMP}"
        backup_dir.mkdir(parents=True, exist_ok=True)
        print_success(f"Backup directory: {backup_dir}")
        
        # Fetch workflows
        workflows = self.get_all_workflows()
        if not workflows:
            print_error("No workflows found!")
            sys.exit(1)
        
        print_success(f"Found {len(workflows)} workflows\n")
        
        # Organize by folders/projects
        organized = self.organize_by_folders(workflows)
        stats = {'total': len(workflows), 'success': 0, 'failed': 0}
        
        # Download
        for folder_path, workflow_list in organized.items():
            if not workflow_list:
                continue
            
            print(f"\n{Colors.BOLD}{folder_path}{Colors.RESET} ({len(workflow_list)} workflows)")
            print("-" * 60)
            
            for workflow in workflow_list:
                if self.download_workflow(workflow, folder_path, backup_dir):
                    stats['success'] += 1
                else:
                    stats['failed'] += 1
        
        # Create index
        print("\n")
        print_info("Creating index files...")
        self.create_index(backup_dir, organized, stats)
        
        # Summary
        print_header("BACKUP COMPLETE")
        print_success(f"Total: {stats['total']} workflows")
        print_success(f"Downloaded: {stats['success']}")
        if stats['failed'] > 0:
            print_warning(f"Failed: {stats['failed']}")
        print_info(f"Location: {backup_dir}\n")

# ============================================================================
# MAIN ENTRY POINT
# ============================================================================

if __name__ == "__main__":
    backup = N8NBackup(N8N_API_URL, N8N_API_KEY, OUTPUT_DIR)
    backup.run()
