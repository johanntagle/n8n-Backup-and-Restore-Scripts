# N8N Workflow Backup & Restore Scripts

Complete backup and restore solution for n8n workflows with hierarchical organization by user/project and tags.

## 🎯 Features

- ✅ **Configuration file support** - Use `.env` file for API credentials
- ✅ **Hierarchical organization**: User/Project > Tags structure
- ✅ **Native n8n compatibility** - Backup files can be imported via n8n UI
- ✅ **Complete workflow data** - nodes, connections, settings preserved
- ✅ **Multiple restore modes** - skip, update, or rename existing workflows
- ✅ **UV package manager** - fast, no virtual env needed
- ✅ **Index files** - JSON and markdown for easy browsing

## ⚠️ Disclaimer

THESE SCRIPTS ARE PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

**USE OF THESE SCRIPTS IS AT YOUR OWN RISK.** THE AUTHOR IS NOT RESPONSIBLE FOR:

- Any loss of data, workflows, or configurations
- Any damage to your n8n instance or systems
- Any unintended consequences of backup or restore operations
- Security breaches resulting from improper use or configuration

**Always test backups in a non-production environment first and maintain your own backup strategy.**

## ⚙️ Configuration

### Step 1: Create Configuration File

Copy the example configuration file:

```bash
cp .env.example .env
```

Edit `.env` with your credentials:

```bash
# N8N Instance URL (required)
N8N_API_URL=https://your-n8n-instance.com

# N8N API Key (required)
# Get this from: Settings > API > Create API Key
N8N_API_KEY=your-api-key-here

# Optional: Backup directory (defaults to ~/n8n-workflows-backup)
# BACKUP_DIR=/path/to/your/backups
```

### Step 2: Set Permissions

```bash
chmod +x n8n_backup_onefile.py
chmod +x n8n_restore_onefile.py
```

### Environment Variables (Optional)

You can override `.env` values with environment variables:

```bash
export N8N_API_KEY='your-api-key'
export N8N_API_URL='https://your-n8n-instance.com'
```

Environment variables take precedence over `.env` file values.

## 📦 Available Scripts

### Backup Scripts

1. **`n8n_backup_onefile.py`** - Single-file portable script (⭐ **RECOMMENDED**)
2. **`download_n8n_workflows.py`** - Standard Python script

### Restore Scripts

1. **`n8n_restore_onefile.py`** - Single-file portable script (⭐ **RECOMMENDED**)
2. **`restore_n8n_workflows.py`** - Standard Python script

All scripts use the same configuration system and produce identical results.

## 🚀 Quick Start

### Backup Your Workflows

```bash
# Run backup script
uv run n8n_backup_onefile.py
```

Or make it executable and run directly:

```bash
./n8n_backup_onefile.py
```

### Restore Your Workflows

```bash
# Interactive restore (prompts for backup and mode)
uv run n8n_restore_onefile.py

# Or specify backup directory directly
uv run n8n_restore_onefile.py ~/n8n-workflows-backup/backup_20260112_111221
```

## 📁 Output Structure

```
~/n8n-workflows-backup/
└── backup_20260112_111221/
    ├── index.json                    # Machine-readable metadata
    ├── README.md                     # Human-readable index
    ├── Johann Tagle/                 # User/Project owner
    │   ├── Google MCP/               # Tag = subfolder
    │   │   ├── Calendar_Manager.json
    │   │   └── MCP_Server.json
    │   ├── AIAFMCP/                  # Another tag
    │   │   └── Workflow.json
    │   └── No Tag/                   # Untagged workflows
    │       └── My_Workflow.json
    └── Genesis Badajos/              # Another user
        └── No Tag/
            └── Their_Workflow.json
```

## 🔄 Restore Modes

The restore script supports three modes:

### 1. Skip Mode (Default) ⊘
- Skips workflows that already exist
- Only creates new workflows
- **Safest option** - no data overwritten

### 2. Update Mode ↻
- Updates existing workflows with backup data
- Overwrites current content with backup version
- **Use when**: You want to restore workflows to backed-up state

### 3. Rename Mode +
- Creates renamed copies of existing workflows
- Appends timestamp: `"My Workflow (restored 20260112_143052)"`
- **Use when**: You want to keep both versions

## 📖 How It Works

### Backup Process

1. Reads configuration from `.env` file
2. Fetches all **active** workflows from n8n API
3. Filters out **archived** workflows
4. Organizes by User/Project > Tags hierarchy
5. Saves workflow JSON **exactly as returned by API** (natively compatible with n8n UI import)
6. Creates index files for easy browsing

### Restore Process

1. Reads configuration from `.env` file
2. Scans backup directory for workflow JSON files
3. Fetches existing workflows from n8n
4. Processes each workflow according to selected mode:
   - **Creates** new workflows
   - **Updates** existing workflows (if mode = update)
   - **Skips** existing workflows (if mode = skip)
   - **Renames** duplicates (if mode = rename)
5. Preserves all nodes and connections

## 🔍 Backup File Format

Backup files contain **native n8n workflow JSON** (compatible with UI import):

```json
{
  "name": "My Workflow",
  "nodes": [...],
  "connections": {...},
  "settings": {...},
  "tags": [...],
  "staticData": null,
  "pinData": {},
  "meta": {
    "templateCredsSetupCompleted": true
  }
}
```

**Important**: Files are saved exactly as returned by n8n API with no modifications. This ensures:
- ✅ Can be imported directly via n8n UI
- ✅ Can be used with n8n's import functionality
- ✅ Full compatibility with n8n format

## ⚠️ Known API Limitations

### Creating Workflows via API

The n8n POST /workflows endpoint has strict validation:

**Accepted Fields:**
- `name` (required)
- `nodes` (required)
- `connections` (required)
- `settings` (required, but must be empty `{}`)

**NOT Accepted When Creating:**
- `tags` - read-only field
- `id`, `createdAt`, `updatedAt` - auto-generated
- `executionOrder`, `timezone`, `saveDataErrorExecution` - settings fields not accepted
- Most workflow settings - cannot be set via POST endpoint

**Impact:**
- ✅ **Workflow nodes and connections** are fully preserved
- ❌ **Settings** use n8n defaults after restore (configure manually in UI)
- ❌ **Tags** are not applied via restore (add manually in UI)

**Workaround:**
1. Restore workflows using the script
2. Open workflows in n8n UI
3. Manually configure settings (timezone, execution order, etc.)
4. Manually add tags as needed

**References:**
- n8n API Documentation: https://docs.n8n.io/api/api-reference/
- GitHub Issue #15835: Import API ignores workflow "settings" object
- Community discussions on API limitations

### Updating Workflows

When using "update" mode, the script can update workflow content (nodes, connections) but settings/tags must still be configured manually via UI.

## 🛠️ Manual Import

You can also import backup files manually via n8n UI:

1. Open n8n in your browser
2. Go to **Workflows** → **Import from File**
3. Select the workflow JSON file from backup
4. Click **Import**

This preserves **all** workflow data including settings and tags.

## 📋 Requirements

- Python 3.10+
- [UV package manager](https://docs.astral.sh/uv/)
- n8n API key with read/write access

### Installing UV

```bash
# macOS/Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# Windows
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"

# Or via pip
pip install uv
```

## 📝 Important Notes

### Archived Workflows

Archived workflows are **not backed up** by default. Only active workflows are included in backups.

### Folder Organization

**n8n's visual folder feature is not available in the public API yet.** These scripts use:
- Project ownership (User/Project name)
- Tags as subfolders

### Multiple Tags

If a workflow has multiple tags, it will appear in multiple folders (one copy per tag).

### Credentials

**Credentials are NOT included** in workflow backups. After restore:
1. Manually configure credentials
2. Select correct credentials in workflow nodes
3. Test workflows before activating

### Workflow IDs

- New workflows get **new IDs** from n8n
- Original backup IDs are **not preserved**
- This may affect workflows that reference other workflows by ID

## 🔒 Security

- **Never commit** `.env` file to version control
- `.env` is excluded by `.gitignore`
- Use environment variables for sensitive data when needed
- Store backups in a secure location
- Consider encrypting backup directory

## 🐛 Troubleshooting

### "N8N_API_KEY not configured"

Create a `.env` file:

```bash
cp .env.example .env
# Edit .env with your credentials
```

Or use environment variable:

```bash
export N8N_API_KEY='your-api-key'
```

### "No workflows found"

- Verify API key has read permissions
- Check you have workflows in your n8n instance
- Ensure N8N_API_URL is correct

### "Failed to create workflow: request/body must NOT have additional properties"

This is expected for certain workflows with complex settings. The script uses the minimum fields accepted by the n8n API. Settings will need to be configured manually in the UI after restore.

### UV cache issues

```bash
# Clear UV cache
uv cache clean
```

## 📊 Performance

- **Small backups** (< 20 workflows): < 30 seconds
- **Medium backups** (20-100 workflows): 1-3 minutes
- **Large backups** (100+ workflows): 3-10 minutes

Time varies based on network speed and n8n instance response time.

## 🤝 Support

If you encounter issues:
1. Check the troubleshooting section
2. Verify n8n API version compatibility
3. Review n8n API documentation: https://docs.n8n.io/api/
4. Check backup file format

## 📄 License

MIT License - Feel free to use and modify as needed.

---

**Created by:** Johann Tagle @ AIAutomationsFactory
**Last Updated:** January 12, 2026
