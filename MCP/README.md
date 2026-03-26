# Claude Code SQLite MCP Server Configuration

Enable SQLite database access in Claude Code using the Model Context Protocol (MCP).

## Prerequisites

Before setting up, ensure you have **UV-X** installed on your system. UV-X is required to run the MCP server on demand.

### Check if UV-X is installed:
```bash
which uvx
```

### Install UV-X (if not already installed):

**macOS / Linux:**
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

**Windows:**
```bash
powershell -ExecutionPolicy BypassUser -c "irm https://astral.sh/uv/install.ps1 | iex"
```

For more details, see the [UV documentation](https://docs.astral.sh/uv/).

---

## Setup

### Option 1: Global Configuration (Recommended for Most Users)

This setup applies SQLite MCP to **all** your Claude Code projects without per-project config.

1. **Run this command once:**
```bash
claude mcp add-json sqlite '{"command":"uvx","args":["mcp-server-sqlite","--db-path","/path/to/your/database.db"]}'
```

Replace `/path/to/your/database.db` with the full path to your database file (or use an absolute path).

2. **Verify the configuration was added:**
```bash
cat ~/.claude/mcp.json
```

You should see the `sqlite` server listed in the output.

3. **Restart Claude Code** to load the new configuration.

You're done! The SQLite MCP server is now available globally.

---

### Option 2: Project-Level Configuration (Local to One Project)

Use this if you want SQLite MCP **only** in a specific project, or need to use `direnv` for environment-scoped activation.

#### 2a. Basic Project-Level Setup

1. **Create `.claude/mcp.json` in your project root:**
```bash
mkdir -p .claude
cat > .claude/mcp.json << 'EOF'
{
  "mcpServers": {
    "sqlite": {
      "command": "uvx",
      "args": ["mcp-server-sqlite", "--db-path", "./chinook.db"]
    }
  }
}
EOF
```

Replace `./chinook.db` with your actual database filename.

2. **Restart Claude Code** to load the project configuration.

#### 2b. Advanced: Project-Level + direnv (Activates Virtual Environment Automatically)

If you're using a Python virtual environment (`.venv`) alongside your project, use `direnv` to activate both the venv and the MCP config when you enter the directory.

**Prerequisites:**
- Install `direnv` (https://direnv.net/docs/installation.html)

**Steps:**

1. **Create `.envrc` in your project root:**
```bash
cat > .envrc << 'EOF'
export CLAUDE_MCP_CONFIG="$PWD/.claude/mcp.json"

if [ -d ".venv" ]; then
  source .venv/bin/activate
fi
EOF
```

2. **Allow direnv to run:**
```bash
direnv allow
```

3. **Create `.claude/mcp.json` (same as above):**
```bash
mkdir -p .claude
cat > .claude/mcp.json << 'EOF'
{
  "mcpServers": {
    "sqlite": {
      "command": "uvx",
      "args": ["mcp-server-sqlite", "--db-path", "./chinook.db"]
    }
  }
}
EOF
```

4. **Verify direnv is loaded:**
```bash
cd /path/to/your/project  # Enter the project directory
direnv status
echo $CLAUDE_MCP_CONFIG   # Should print the path to your .claude/mcp.json
```

5. **Restart Claude Code** and your virtual environment will be active automatically.

---

## What You Can Do

Once configured, Claude Code can:
- List tables in your database
- Describe table schemas
- Run read queries (SELECT statements)
- Execute bash commands with sqlite3

## Example Usage

After setup, you can ask Claude Code:
- "Show me the structure of the users table"
- "Run a SELECT query to get all records from the products table"
- "What tables are in this database?"
- "Count the rows in the artists table"

## Troubleshooting

**"uvx: command not found"**
- Ensure UV-X is installed: `curl -LsSf https://astral.sh/uv/install.sh | sh`
- Restart your terminal after installation

**MCP server not loading in Claude Code**
- Verify the config file exists: `cat ~/.claude/mcp.json` (global) or `.claude/mcp.json` (project)
- Restart Claude Code after making changes
- Check that the database path is correct and the file exists

**Database file not found**
- Use absolute paths in global config: `/home/username/path/to/database.db`
- Use relative paths in project config: `./chinook.db` (assumes db is in project root)