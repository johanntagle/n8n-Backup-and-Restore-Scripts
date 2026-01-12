# N8N Workflow Restore Documentation

Complete guide for restoring n8n workflows from backups.

## 📦 Available Restore Scripts

Three different ways to restore your workflows:

1. **`n8n_restore_onefile.py`** - Single-file portable script (⭐ **RECOMMENDED**)
2. **`restore_n8n_workflows.py`** - Standard Python script  
3. **`restore_n8n_workflows.sh`** - Bash wrapper with auto-install

All three scripts do the exact same thing - choose based on your preference!

## 🎯 Restore Modes

The restore script supports three different modes for handling existing workflows:

### 1. Skip Mode (Default) ⊘
- **Skips workflows that already exist** in n8n
- Only creates workflows that don't exist yet
- **Safest option** - no data is overwritten
- **Use when**: You want to restore missing workflows only

### 2. Update Mode ↻
- **Updates existing workflows** with backup data
- Overwrites current workflow content with backup version
- Creates workflows that don't exist
- **Use when**: You want to restore workflows to their backed-up state

### 3. Rename Mode +
- **Creates renamed copies** of existing workflows
- Appends timestamp to duplicate workflow names
- Example: `"My Workflow"` becomes `"My Workflow (restored 20260112_143052)"`
- **Use when**: You want to keep both versions

## 🚀 Quick Start

### Option 1: Single-File Script (Recommended)

```bash
# Set your API key
export N8N_API_KEY='your-n8n-api-key-here'

# Interactive restore (will prompt for backup and mode)
uv run n8n_restore_onefile.py

# Or specify backup directory directly
uv run n8n_restore_onefile.py ~/n8n-workflows-backup/backup_20260112_111221
```

### Option 2: Standard Python Script

```bash
export N8N_API_KEY='your-api-key'
uv run restore_n8n_workflows.py
```

### Option 3: Bash Wrapper

```bash
export N8N_API_KEY='your-api-key'
./restore_n8n_workflows.sh
```

## 📋 Interactive Prompts

When you run the script without arguments, it will guide you through:

### 1. Select Backup Directory

```
Available backups:
  1. backup_20260112_111221 (39 workflows)
  2. backup_20260111_093045 (38 workflows)
  3. backup_20260110_150230 (35 workflows)

Select backup (1-3) or 'q' to quit:
```

### 2. Select Restore Mode

```
Restore mode:
  1. skip     - Skip workflows that already exist (default)
  2. update   - Update existing workflows with backup data
  3. rename   - Create new workflows with renamed duplicates

Select mode (1-3) or press Enter for default:
```

### 3. Confirm Restore

```
Restore workflows from backup_20260112_111221? (yes/no):
```

## 📊 Restore Process

1. **Scans backup directory** for all workflow JSON files
2. **Fetches existing workflows** from n8n
3. **Processes each workflow** according to selected mode:
   - Checks if workflow exists (by name)
   - Creates or updates based on mode
   - Reports success/failure for each workflow
4. **Displays summary** with statistics

## 📈 Example Output

```
============================================================
                    N8N WORKFLOW RESTORE                     
============================================================

✓ Backup directory: /Users/johann/n8n-workflows-backup/backup_20260112_111221
✓ Restore mode: skip

Restore workflows from backup_20260112_111221? (yes/no): yes

ℹ Fetching existing workflows from n8n...
ℹ Found 25 existing workflows
ℹ Found 39 workflow files to restore
ℹ Restoring workflows (mode: skip)...
  + Created: GHL – Check Availability
  + Created: Google MCP Server
  ⊘ Skipped: MCP Google Calendar Manager (already exists)
  + Created: Voice Agent Integration Practice
  ...

============================================================
                      RESTORE COMPLETE                       
============================================================

✓ Total workflows: 39
✓ Created: 14
ℹ Skipped: 25
ℹ Target: https://n8ndev.aiautomationsfactory.com
```

## ⚙️ Configuration

### Environment Variables

```bash
# Required
export N8N_API_KEY='your-api-key-here'

# Optional (with defaults)
export N8N_API_URL='https://n8ndev.aiautomationsfactory.com'
export BACKUP_DIR="$HOME/n8n-workflows-backup"
```

### Command Line Arguments

```bash
# Specify backup directory directly
uv run n8n_restore_onefile.py /path/to/backup_directory

# Use default interactive mode
uv run n8n_restore_onefile.py
```

## 🔍 What Gets Restored

Each workflow file in the backup contains:

```json
{
  "metadata": {
    "workflow_name": "My Workflow",
    "workflow_id": "abc123",
    "tags": ["Google MCP"]
  },
  "workflow": {
    "name": "My Workflow",
    "nodes": [...],
    "connections": {...},
    "settings": {...}
  }
}
```

The restore script:
- Extracts the `workflow` object
- Creates/updates workflow in n8n via API
- Preserves all nodes, connections, and settings

## ⚠️ Important Notes

### Workflow Identification

Workflows are matched by **name only**. If you have multiple workflows with the same name, the script will only detect the first one.

### Tags and Folders

- Tags from backup are **preserved** in the restored workflow
- Folder structure from backup is **not preserved** (folders are not in public API)
- Workflows will appear in n8n with their tags, but not in specific folders

### Credentials

- **Credentials are NOT included** in workflow backups
- After restore, you'll need to:
  1. Manually configure credentials for each workflow
  2. Select the correct credentials in workflow nodes
  3. Test workflows before activating

### Workflow IDs

- New workflows get **new IDs** from n8n
- Original backup IDs are **not preserved**
- This may affect workflows that reference other workflows by ID

### Active Status

- Restored workflows are created **inactive** by default
- You must manually activate workflows after:
  1. Configuring credentials
  2. Testing workflow execution
  3. Verifying all nodes are working

## 🛡️ Safety Features

### Skip Mode Default
The default "skip" mode ensures existing workflows are never accidentally overwritten.

### Interactive Confirmation
All restore operations require explicit confirmation before proceeding.

### Detailed Reporting
Every workflow operation is logged with success/failure status.

### Error Handling
Failed restores don't stop the process - other workflows continue to be restored.

## 🔧 Common Scenarios

### Scenario 1: Restore All Missing Workflows

```bash
export N8N_API_KEY='your-key'
uv run n8n_restore_onefile.py

# Select backup
# Select mode: 1 (skip)
# Confirm: yes
```

Result: Only workflows that don't exist will be created.

### Scenario 2: Revert Workflows to Backup State

```bash
export N8N_API_KEY='your-key'
uv run n8n_restore_onefile.py

# Select backup
# Select mode: 2 (update)
# Confirm: yes
```

Result: All workflows updated to match backup versions.

### Scenario 3: Keep Both Versions

```bash
export N8N_API_KEY='your-key'
uv run n8n_restore_onefile.py

# Select backup
# Select mode: 3 (rename)
# Confirm: yes
```

Result: Duplicates created with timestamped names.

### Scenario 4: Restore Specific Backup

```bash
export N8N_API_KEY='your-key'
uv run n8n_restore_onefile.py ~/n8n-workflows-backup/backup_20260110_150230
```

Result: Skips interactive backup selection, uses specified backup.

## 🐛 Troubleshooting

### "N8N_API_KEY environment variable not set"

```bash
# Make sure to export the API key
export N8N_API_KEY='your-actual-api-key'

# Verify it's set
echo $N8N_API_KEY
```

### "No backup directories found"

Check that backups exist:

```bash
ls -la ~/n8n-workflows-backup/
```

Make sure directories start with `backup_` prefix.

### "Failed to create workflow"

Common causes:
- **API permissions** - ensure API key has write access
- **Invalid workflow data** - backup file may be corrupted
- **Name conflict** - workflow name might be problematic
- **Network issues** - check connection to n8n instance

Check the error message for details.

### "Failed to update workflow"

- Verify the workflow still exists in n8n
- Check API key has update permissions
- Ensure workflow is not locked or in use

### Restore seems stuck

The script processes workflows sequentially. For large backups:
- Each workflow requires 2 API calls (check + create/update)
- Network latency affects speed
- Be patient - progress is displayed for each workflow

## 📊 Performance

- **Small backups** (< 20 workflows): < 30 seconds
- **Medium backups** (20-100 workflows): 1-3 minutes
- **Large backups** (100+ workflows): 3-10 minutes

Time varies based on:
- Network speed
- n8n instance response time
- Number of existing workflows
- Workflow complexity

## 🔒 Security Considerations

### API Key Protection

```bash
# Never commit API key to version control
# Use environment variables only
export N8N_API_KEY='...'

# Or use a secure credential manager
export N8N_API_KEY=$(security find-generic-password -s n8n-api-key -w)
```

### Backup Verification

Before restoring:
1. Verify backup integrity
2. Check backup source
3. Review backup timestamp
4. Confirm correct n8n instance

### Test Restores

For critical restores:
1. Test on staging/dev instance first
2. Use "skip" mode initially
3. Verify credentials before activating
4. Test workflow execution

## 📝 Post-Restore Checklist

After restore completes:

- [ ] Review restore summary
- [ ] Configure missing credentials
- [ ] Test restored workflows
- [ ] Verify workflow connections
- [ ] Check workflow settings
- [ ] Activate workflows as needed
- [ ] Document any issues
- [ ] Update workflow tags if needed

## 🤝 Support

If you encounter issues:

1. Check troubleshooting section
2. Verify n8n API version compatibility
3. Review n8n API documentation
4. Check backup file format

## 📄 Related Documentation

- **README.md** - Main package documentation
- **BACKUP_README.md** - Backup process details
- **QUICKSTART.md** - Quick reference guide

---

**Created by:** Johann Tagle @ AIAutomationsFactory  
**Last Updated:** January 12, 2026
