# N8N Workflow Backup Tools

## Overview

These tools download all workflows from your n8n instance and organize them into folders based on their tags. Uses **UV** for fast, reliable Python package management.

## Files

- `download_n8n_workflows.py` - Main Python script (with inline UV dependencies)
- `backup_n8n_workflows.sh` - Bash wrapper for easy execution
- This README file

## Prerequisites

1. **UV** - Fast Python package manager (auto-installs if missing)
2. **N8N API Key** - Get this from your n8n instance:
   - Go to Settings → API
   - Generate new API key

**No manual Python setup needed!** UV handles everything automatically.

## Quick Start

### Step 1: Set Your API Key

```bash
export N8N_API_KEY='your-api-key-here'
```

For permanent setup, add to your `~/.bashrc` or `~/.zshrc`:
```bash
echo 'export N8N_API_KEY="your-api-key-here"' >> ~/.bashrc
source ~/.bashrc
```

### Step 2: Run the Backup

```bash
./backup_n8n_workflows.sh
```

The script will auto-install UV if needed!

Or run directly with UV:
```bash
uv run download_n8n_workflows.py
```

## Why UV?

- **Fast**: 10-100x faster than pip
- **Reliable**: Consistent dependency resolution
- **No venv needed**: Automatic isolated environments
- **Self-contained**: Dependencies declared inline in the script
- **Auto-install**: Missing dependencies installed automatically

## Manual UV Installation (if needed)

```bash
# macOS/Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# Or with Homebrew
brew install uv

# Or with pipx
pipx install uv
```

## What Gets Downloaded

The script will:

1. **Fetch all active workflows** from your n8n instance (archived workflows are skipped)
2. **Organize hierarchically** by User/Project > Tags:
   - First level: Project owner (e.g., "Johann Tagle", "Genesis Badajos")
   - Second level: Tags (e.g., "Google MCP", "AIAFMCP")
   - Workflows with multiple tags appear in multiple folders
   - Workflows without tags go to "No Tag" subfolder
3. **Save complete workflow data** including:
   - All nodes and connections
   - Workflow settings
   - Metadata (creation date, update date, etc.)
4. **Create index files**:
   - `index.json` - Machine-readable backup metadata
   - `README.md` - Human-readable workflow list

**Note:** n8n's visual folder feature is not available in the public API yet. This script uses the project owner and tags as the organization method.

## Output Structure

```
~/n8n-workflows-backup/
└── backup_YYYYMMDD_HHMMSS/
    ├── index.json
    ├── README.md
    ├── Johann Tagle/               # Project owner (you)
    │   ├── Google MCP/             # Tag = subfolder
    │   │   ├── Workflow_1_ID123.json
    │   │   └── Workflow_2_ID456.json
    │   ├── AIAFMCP/                # Another tag
    │   │   └── Calendar_Manager_ID789.json
    │   └── No Tag/                 # Untagged workflows
    │       └── My_Workflow_IDabc.json
    └── Genesis Badajos/            # Another user's workflows
        └── No Tag/
            └── Their_Workflow_IDdef.json
```

## Workflow File Format

Each workflow file contains:

```json
{
  "metadata": {
    "downloaded_at": "2026-01-12T10:30:00.000Z",
    "workflow_id": "abc123",
    "workflow_name": "My Workflow",
    "active": true,
    "archived": false,
    "created_at": "2026-01-01T00:00:00.000Z",
    "updated_at": "2026-01-11T12:00:00.000Z",
    "tags": ["Production", "API"],
    "node_count": 5
  },
  "workflow": {
    "id": "abc123",
    "name": "My Workflow",
    "nodes": [...],
    "connections": {...},
    "settings": {...}
  }
}
```

## Configuration

Edit the script to change:

```python
# Default backup location
OUTPUT_DIR = Path.home() / "n8n-workflows-backup"

# Your n8n instance URL
N8N_API_URL = "https://n8ndev.aiautomationsfactory.com"
```

## Restoring Workflows

To restore workflows to n8n:

1. Open the workflow JSON file
2. Copy the entire `workflow` object
3. In n8n, go to Workflows → Import from File
4. Paste the workflow JSON

Or use the n8n API to bulk import:

```bash
curl -X POST https://your-n8n.com/api/v1/workflows \
  -H "X-N8N-API-KEY: your-api-key" \
  -H "Content-Type: application/json" \
  -d @workflow-file.json
```

## Automation

### Daily Backup with Cron

Add to your crontab (`crontab -e`):

```bash
# Daily backup at 2 AM
0 2 * * * export N8N_API_KEY='your-key' && /path/to/backup_n8n_workflows.sh >> /var/log/n8n-backup.log 2>&1
```

### Weekly Backup with Systemd Timer

Create `/etc/systemd/system/n8n-backup.service`:

```ini
[Unit]
Description=N8N Workflow Backup
After=network.target

[Service]
Type=oneshot
Environment="N8N_API_KEY=your-api-key"
ExecStart=/path/to/backup_n8n_workflows.sh
User=yourusername
```

Create `/etc/systemd/system/n8n-backup.timer`:

```ini
[Unit]
Description=Weekly N8N Backup Timer

[Timer]
OnCalendar=Sun 02:00
Persistent=true

[Install]
WantedBy=timers.target
```

Enable:
```bash
sudo systemctl enable n8n-backup.timer
sudo systemctl start n8n-backup.timer
```

## Troubleshooting

### "N8N_API_KEY not set"
```bash
export N8N_API_KEY='your-api-key'
```

### "uv: command not found"
UV will auto-install, but if it fails:
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
# Then restart your terminal or run:
export PATH="$HOME/.cargo/bin:$PATH"
```

### Connection errors
- Check your n8n URL is correct
- Verify API key is valid
- Ensure n8n instance is accessible

### Permission denied
```bash
chmod +x backup_n8n_workflows.sh
chmod +x download_n8n_workflows.py
```

### UV cache issues
```bash
# Clear UV cache if needed
uv cache clean
```

## Your Current Setup

**N8N Instance:** https://n8ndev.aiautomationsfactory.com
**Total Workflows:** 45
- Active: 2
- Inactive: 38
- Archived: 5

**Workflow Distribution:**
- Untagged: 40 workflows
- Google MCP: 5 workflows (archived)

## Notes

- Each backup creates a new timestamped folder
- Workflow IDs are preserved in filenames
- All metadata is included for complete restore
- Safe to run multiple times (creates new backups)
- Does not modify or delete workflows on n8n

## Support

For issues or questions:
1. Check the troubleshooting section
2. Review n8n API documentation: https://docs.n8n.io/api/
3. Check backup logs in the output

## License

Free to use and modify for your needs.
