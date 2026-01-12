# 🚀 Quick Start Guide - Choose Your Style

## Three Ways to Backup Your N8N Workflows

All scripts do the same thing - pick the one that fits your workflow!

---

## Option 1: One-File Edition (Simplest!) ⭐

**Best for:** Quick backups, one-off downloads, sharing with others

```bash
# Just run it!
export N8N_API_KEY='your-key'
uv run n8n_backup_onefile.py
```

**Features:**
- ✓ Single file - easiest to share
- ✓ Beautiful colored output
- ✓ Zero configuration needed
- ✓ Self-contained with inline dependencies

---

## Option 2: Bash Wrapper (Most Automated)

**Best for:** Cron jobs, automated backups, production use

```bash
# One command does everything
export N8N_API_KEY='your-key'
./backup_n8n_workflows.sh
```

**Features:**
- ✓ Auto-installs UV if missing
- ✓ Validates everything before running
- ✓ Great error messages
- ✓ Perfect for automation

---

## Option 3: Direct Python Script (Most Flexible)

**Best for:** Customization, integration with other tools

```bash
# Run directly with UV
export N8N_API_KEY='your-key'
uv run download_n8n_workflows.py
```

**Features:**
- ✓ Easy to modify and customize
- ✓ Well-documented code
- ✓ Extensible for your needs
- ✓ Same as Option 1 but with bash wrapper

---

## What's UV and Why Do I Need It?

**UV** is a blazingly fast Python package manager created by Astral (the folks behind Ruff).

### Benefits:
- **10-100x faster** than pip
- **No virtual environments** needed
- **Automatic dependency management** - just run the script!
- **Inline dependencies** - no separate requirements.txt

### Auto-Installation:
UV auto-installs when you run `backup_n8n_workflows.sh`. Or install manually:

```bash
# macOS/Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# Homebrew
brew install uv
```

---

## First Time Setup (All Options)

### 1. Get Your N8N API Key

1. Open your n8n instance: https://n8ndev.aiautomationsfactory.com
2. Go to **Settings** → **API**
3. Click **Generate new API key**
4. Copy the key

### 2. Set Environment Variable

**Temporary (current session):**
```bash
export N8N_API_KEY='n8n_api_xxxxxxxxxxxxx'
```

**Permanent (add to ~/.bashrc or ~/.zshrc):**
```bash
echo 'export N8N_API_KEY="n8n_api_xxxxxxxxxxxxx"' >> ~/.bashrc
source ~/.bashrc
```

### 3. Run Your Chosen Script

Pick one from the options above!

---

## What You'll Get

```
~/n8n-workflows-backup/
└── backup_20260112_103045/
    ├── index.json                    # Machine-readable metadata
    ├── README.md                     # Human-readable index
    ├── Johann Tagle/                 # Your project (user)
    │   ├── Google MCP/               # Tag = subfolder
    │   │   ├── Calendar_Manager_abc123.json
    │   │   └── MCP_Server_def456.json
    │   ├── AIAFMCP/                  # Another tag
    │   │   └── Workflow_xyz789.json
    │   └── No Tag/                   # Untagged workflows
    │       └── My_Workflow_ghi012.json
    └── Genesis Badajos/              # Another user
        └── No Tag/
            └── Their_Workflow_jkl345.json
```

**Note:** n8n's visual folder feature is not available in the public API yet. This script uses tags as the organization method.

**Archived workflows are not included in backups** - only active workflows are backed up.

Each workflow file contains:
- Complete workflow JSON (nodes, connections, settings)
- Metadata (dates, status, tags, node count)
- Everything needed to restore

---

## Pro Tips

### Schedule Automatic Backups

**Daily at 2 AM:**
```bash
# Add to crontab (crontab -e)
0 2 * * * export N8N_API_KEY='your-key' && /path/to/backup_n8n_workflows.sh
```

**Weekly with systemd:**
```bash
# See BACKUP_README.md for systemd setup
```

### Backup to Cloud

```bash
# Run backup then sync to S3
./backup_n8n_workflows.sh
aws s3 sync ~/n8n-workflows-backup/ s3://my-bucket/n8n-backups/
```

### Quick Restore

To restore a workflow:
1. Open the JSON file
2. Copy the `workflow` object
3. In n8n: **Import from File**
4. Paste and save

---

## Troubleshooting

### "N8N_API_KEY not set"
```bash
export N8N_API_KEY='your-actual-key'
# Don't forget the export!
```

### "uv: command not found"
The bash wrapper auto-installs UV, but if it fails:
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
source ~/.bashrc
```

### Permission denied
```bash
chmod +x backup_n8n_workflows.sh
chmod +x n8n_backup_onefile.py
```

### Connection refused
- Verify your n8n URL is correct
- Check API key is valid
- Ensure n8n instance is accessible

---

## Comparison Chart

| Feature | One-File | Bash Wrapper | Python Direct |
|---------|----------|--------------|---------------|
| Ease of use | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| Setup time | Instant | Instant | Instant |
| Customization | ⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| Automation | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| Portability | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| Best for | Quick use | Production | Development |

---

## Your Current Setup

**N8N Instance:** https://n8ndev.aiautomationsfactory.com
**Total Workflows:** 45

- Active: 2
- Inactive: 38  
- Archived: 5

**Distribution:**
- Hierarchical: User/Project > Tags
- Archived workflows are skipped (not backed up)
- Uses public API (project ownership + tags)

---

## Next Steps

1. ✓ Choose your preferred script
2. ✓ Set N8N_API_KEY environment variable
3. ✓ Run the backup
4. ✓ Check `~/n8n-workflows-backup/` for results
5. ✓ Optional: Set up automated backups

Need help? All three scripts have identical output - they just offer different ways to run!
