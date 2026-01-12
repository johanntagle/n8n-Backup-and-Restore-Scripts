#!/usr/bin/env -S uv run --quiet --script
# /// script
# requires-python = ">=3.10"
# dependencies = [
#     "requests",
# ]
# ///
"""
N8N Workflow Downloader
Downloads all workflows from n8n instance and organizes them by tags/folders

Configuration:
    Create a .env file with:
    N8N_API_URL=https://your-n8n-instance.com
    N8N_API_KEY=your-api-key

Usage:
    uv run download_n8n_workflows.py
"""

import os
import json
import requests
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any

# Import configuration module
from n8n_config import get_n8n_api_url, get_n8n_api_key, get_backup_dir

# Configuration
N8N_API_URL = get_n8n_api_url()
N8N_API_KEY = get_n8n_api_key()
OUTPUT_DIR = get_backup_dir()
BACKUP_TIMESTAMP = datetime.now().strftime("%Y%m%d_%H%M%S")

class N8NWorkflowDownloader:
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
        """Fetch all workflows from n8n instance"""
        print(f"Fetching workflows from {self.api_url}...")
        
        all_workflows = []
        cursor = None
        
        while True:
            url = f"{self.api_url}/api/v1/workflows"
            params = {'limit': 100}
            if cursor:
                params['cursor'] = cursor
            
            try:
                response = self.session.get(url, params=params)
                response.raise_for_status()
                data = response.json()
                
                workflows = data.get('data', [])
                all_workflows.extend(workflows)
                
                print(f"  Fetched {len(workflows)} workflows (total: {len(all_workflows)})")
                
                # Check if there are more pages
                if not data.get('nextCursor'):
                    break
                cursor = data['nextCursor']
                
            except requests.exceptions.RequestException as e:
                print(f"Error fetching workflows: {e}")
                break
        
        return all_workflows
    
    def get_workflow_details(self, workflow_id: str) -> Dict[str, Any]:
        """Fetch full workflow details including nodes and connections"""
        url = f"{self.api_url}/api/v1/workflows/{workflow_id}"
        
        try:
            response = self.session.get(url)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error fetching workflow {workflow_id}: {e}")
            return None
    
    def get_workflow_project(self, workflow_id: str, workflow_summary: Dict[str, Any]) -> str:
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
    
    def organize_by_tags(self, workflow_list: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
        """Organize workflows by User/Project > Tags hierarchy"""
        # Filter out archived workflows entirely
        active_workflows = [w for w in workflow_list if not w.get('isArchived', False)]
        
        archived_count = len(workflow_list) - len(active_workflows)
        print(f"Found {len(active_workflows)} active workflows")
        if archived_count > 0:
            print(f"Skipping {archived_count} archived workflows")
        
        organized = {}
        
        print("Organizing by user and tags...")
        
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
                    print(f"  [{project_name}/{tag_name}] {workflow_name}")
            else:
                # No tags - organize under Project/No Tag
                folder_path = f"{project_name_safe}/No Tag"
                if folder_path not in organized:
                    organized[folder_path] = []
                
                organized[folder_path].append(workflow)
                print(f"  [{project_name}/No Tag] {workflow_name}")
        
        return organized
        
        return organized
    
    def sanitize_filename(self, name: str) -> str:
        """Sanitize filename to be filesystem-safe"""
        # Replace invalid characters
        invalid_chars = '<>:"/\\|?*'
        for char in invalid_chars:
            name = name.replace(char, '_')
        return name.strip()

    def download_workflow(self, workflow_summary: Dict[str, Any], folder_path: str, backup_dir: Path) -> bool:
        """Download a single workflow to nested folder structure"""
        workflow_id = workflow_summary['id']
        workflow_name = workflow_summary.get('name', 'Unnamed')

        print(f"  Downloading: {workflow_name} ({workflow_id})")

        # Get full workflow details
        workflow_data = self.get_workflow_details(workflow_id)
        if not workflow_data:
            return False

        # Create nested folder structure
        full_folder_path = backup_dir / folder_path
        full_folder_path.mkdir(parents=True, exist_ok=True)

        # Create safe filename
        safe_name = self.sanitize_filename(workflow_name)
        filename = f"{safe_name}.json"
        filepath = full_folder_path / filename

        # Save workflow data exactly as returned by API (no modifications)
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(workflow_data, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"    Error saving {filename}: {e}")
            return False
    
    def create_folder_structure(self) -> Path:
        """Create the backup folder structure"""
        backup_dir = self.output_dir / f"backup_{BACKUP_TIMESTAMP}"
        backup_dir.mkdir(parents=True, exist_ok=True)
        return backup_dir
    
    def create_index_file(self, backup_dir: Path, organized: Dict[str, List], stats: Dict):
        """Create an index file with backup information"""
        index_data = {
            'backup_info': {
                'timestamp': datetime.now().isoformat(),
                'n8n_instance': self.api_url,
                'total_workflows': stats['total'],
                'successful_downloads': stats['success'],
                'failed_downloads': stats['failed']
            },
            'folder_structure': {
                folder: len(workflows) 
                for folder, workflows in organized.items()
            },
            'workflows_by_folder': {
                folder: [
                    {
                        'id': w['id'],
                        'name': w['name'],
                        'active': w.get('active', False),
                        'tags': [tag.get('name') for tag in w.get('tags', [])]
                    }
                    for w in workflows
                ]
                for folder, workflows in organized.items()
            }
        }
        
        index_file = backup_dir / 'index.json'
        with open(index_file, 'w', encoding='utf-8') as f:
            json.dump(index_data, f, indent=2, ensure_ascii=False)
        
        # Also create a readable README
        readme = backup_dir / 'README.md'
        with open(readme, 'w', encoding='utf-8') as f:
            f.write(f"# N8N Workflows Backup\n\n")
            f.write(f"**Backup Date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"**N8N Instance:** {self.api_url}\n")
            f.write(f"**Total Workflows:** {stats['total']}\n")
            f.write(f"**Successfully Downloaded:** {stats['success']}\n\n")
            f.write(f"## Folder Structure\n\n")
            
            for folder, workflows in organized.items():
                f.write(f"### {folder} ({len(workflows)} workflows)\n\n")
                for w in workflows:
                    status = "✓ Active" if w.get('active') else "○ Inactive"
                    f.write(f"- {status} **{w['name']}** (`{w['id']}`)\n")
                f.write("\n")
    
    def download_all(self):
        """Main download process"""
        print("=" * 60)
        print("N8N WORKFLOW DOWNLOADER")
        print("=" * 60)
        print()
        
        # Create backup directory
        backup_dir = self.create_folder_structure()
        print(f"Backup directory: {backup_dir}\n")
        
        # Fetch all workflows
        workflows = self.get_all_workflows()
        if not workflows:
            print("No workflows found or error occurred.")
            return
        
        print(f"\nFound {len(workflows)} workflows\n")
        
        # Organize by tags
        organized = self.organize_by_tags(workflows)
        
        # Download workflows
        stats = {'total': len(workflows), 'success': 0, 'failed': 0}
        
        for folder_path, workflow_list in organized.items():
            if not workflow_list:
                continue
            
            print(f"\n{folder_path.upper()} ({len(workflow_list)} workflows)")
            print("-" * 60)
            
            # Download each workflow
            for workflow in workflow_list:
                if self.download_workflow(workflow, folder_path, backup_dir):
                    stats['success'] += 1
                else:
                    stats['failed'] += 1
        
        # Create index file
        print("\nCreating index file...")
        self.create_index_file(backup_dir, organized, stats)
        
        # Summary
        print("\n" + "=" * 60)
        print("DOWNLOAD COMPLETE")
        print("=" * 60)
        print(f"Total workflows: {stats['total']}")
        print(f"Successfully downloaded: {stats['success']}")
        print(f"Failed: {stats['failed']}")
        print(f"\nBackup location: {backup_dir}")
        print("\nFiles created:")
        print(f"  - index.json (backup metadata)")
        print(f"  - README.md (human-readable index)")
        print(f"  - {len(organized)} folders with workflow files")
        print()


def main():
    if not N8N_API_KEY:
        print("ERROR: N8N_API_KEY not configured!")
        print("Set it in .env file or with: export N8N_API_KEY='your-api-key'")
        return
    
    downloader = N8NWorkflowDownloader(N8N_API_URL, N8N_API_KEY, OUTPUT_DIR)
    downloader.download_all()


if __name__ == "__main__":
    main()
