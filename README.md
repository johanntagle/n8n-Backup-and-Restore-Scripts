# N8N Workflow Backup Scripts

Complete backup solution for n8n workflows with hierarchical organization by user/project and tags.

## 📦 What's Included

This package contains three different ways to backup your n8n workflows:

1. **`n8n_backup_onefile.py`** - Single-file portable script (⭐ **RECOMMENDED**)
2. **`download_n8n_workflows.py`** - Standard Python script  
3. **`backup_n8n_workflows.sh`** - Bash wrapper with auto-install

All three scripts do the exact same thing - choose based on your preference!

## 🎯 Features

- ✅ **Hierarchical organization**: User/Project > Tags structure
- ✅ **Skips archived workflows** - only backs up active workflows
- ✅ **Complete workflow data** - nodes, connections, settings, metadata
- ✅ **UV package manager** - fast, no virtual env needed
- ✅ **Portable** - inline dependencies using PEP 723
- ✅ **Index files** - JSON and markdown for easy browsing

## 📁 Output Structure

```
~/n8n-workflows-backup/
└── backup_20260112_111221/
    ├── index.json                    # Machine-readable metadata
    ├── README.md                     # Human-readable index
    ├── Johann Tagle/                 # User/Project owner
    │   ├── Google MCP/               # Tag = subfolder
    │   │   ├── Workflow_1_abc123.json
    │   │   └── Workflow_2_def456.json
    │   ├── AIAFMCP/                  # Another tag
    │   │   └── Calendar_xyz789.json
    │   └── No Tag/                   # Untagged workflows
    │       └── My_Workflow_ghi012.json
    └── Genesis Badajos/              # Another user
        └── No Tag/
            └── Their_Workflow_jkl345.json
```

## 🚀 Quick Start

### Option 1: Single-File Script (Recommended)

```bash
# Set your API key
export N8N_API_KEY='your-n8n-api-key-here'

# Run the script
uv run n8n_backup_onefile.py
```

### Option 2: Standard Python Script

```bash
export N8N_API_KEY='your-api-key'
uv run download_n8n_workflows.py
```

### Option 3: Bash Wrapper

```bash
export N8N_API_KEY='your-api-key'
./backup_n8n_workflows.sh
```

## ⚙️ Configuration

All scripts use environment variables for configuration:

```bash
# Required
export N8N_API_KEY='your-api-key-here'

# Optional (with defaults)
export N8N_API_URL='https://n8ndev.aiautomationsfactory.com'
export BACKUP_DIR="$HOME/n8n-workflows-backup"
```

## 📋 Requirements

- Python 3.10+
- [UV package manager](https://docs.astral.sh/uv/) (installs automatically with bash script)
- n8n API key with read access

### Installing UV

```bash
# macOS/Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# Windows
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"

# Or via pip
pip install uv
```

## 📖 How It Works

1. **Fetches all workflows** from your n8n instance using the public API
2. **Filters out archived** workflows (only active workflows are backed up)
3. **Organizes hierarchically**:
   - First level: User/Project owner (e.g., "Johann Tagle")
   - Second level: Tags (e.g., "Google MCP", "AIAFMCP")
   - Workflows without tags go to "No Tag" subfolder
4. **Saves complete data** for each workflow as JSON
5. **Creates index files** for easy browsing

## 🔍 What Gets Backed Up

Each workflow JSON file contains:

```json
{
  "metadata": {
    "downloaded_at": "2026-01-12T11:12:21",
    "workflow_id": "abc123",
    "workflow_name": "My Workflow",
    "active": true,
    "archived": false,
    "tags": ["Google MCP"],
    "node_count": 5
  },
  "workflow": {
    // Complete workflow data
    "nodes": [...],
    "connections": {...},
    "settings": {...}
  }
}
```

## 📝 Important Notes

### Folder Limitations

**n8n's visual folder feature is not available in the public API yet.** These scripts use:
- Project ownership (User/Project name)
- Tags as subfolders

This is the most reliable organization method using the official n8n public API.

### Archived Workflows

Archived workflows are **not backed up**. Only active workflows are included in backups.

### Multiple Tags

If a workflow has multiple tags, it will appear in multiple folders (one copy per tag).

## 🛠️ Troubleshooting

### "UV cache issue"

If you see unexpected behavior after updating scripts:

```bash
rm -rf ~/.cache/uv
uv run n8n_backup_onefile.py
```

### "API connection failed"

Check your API key and URL:

```bash
# Test connection
curl -H "X-N8N-API-KEY: your-key" https://your-n8n-url/api/v1/workflows
```

### "No workflows found"

- Verify your API key has read permissions
- Check that you have workflows in your n8n instance
- Ensure you're not filtering out all workflows (e.g., all archived)

## 📄 Files Included

| File | Description |
|------|-------------|
| `n8n_backup_onefile.py` | ⭐ Single-file portable script (recommended) |
| `download_n8n_workflows.py` | Standard Python script |
| `backup_n8n_workflows.sh` | Bash wrapper with auto-install |
| `BACKUP_README.md` | Detailed documentation |
| `QUICKSTART.md` | Quick comparison guide |
| `README.md` | This file |

## 🔒 Security

- **Never commit your API key** to version control
- Use environment variables for sensitive data
- Store backups in a secure location
- Consider encrypting backup directory

## 📚 Additional Documentation

- **QUICKSTART.md** - Quick comparison of all three scripts
- **BACKUP_README.md** - Comprehensive backup documentation

## 🤝 Support

If you encounter issues:
1. Check the troubleshooting section above
2. Verify your n8n API version compatibility
3. Review the n8n API documentation: https://docs.n8n.io/api/

## 📄 License

MIT License - Feel free to use and modify as needed.

---

**Created by:** Johann Tagle @ AIAutomationsFactory  
**Last Updated:** January 12, 2026
