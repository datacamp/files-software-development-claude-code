# Claude Code — Setup & Access Guide

This guide covers how to install Claude Code locally and the different environments you can use it from.

> **Note:** Claude Code is pre-configured in the DataCamp learning environment. You only need these steps to set it up on your own machine.

---

## Requirements

Before installing, make sure you have:

- A **Claude Pro, Max, Teams, Enterprise, or API Console** account — the free Claude.ai plan does not include Claude Code access.
- **macOS** 10.15+, **Linux** (64-bit), or **Windows** with Git for Windows or WSL2.

---

## Local Installation

### Install

Run the following in your terminal (macOS or Linux):

```bash
curl -fsSL https://claude.ai/install.sh | bash
```

On **Windows (PowerShell)**:

```powershell
irm https://claude.ai/install.ps1 | iex
```

On **Windows with WSL2** (recommended): use the macOS/Linux command above inside your WSL terminal.

The native installer requires no dependencies (no Node.js needed), adds Claude Code to your PATH, and enables automatic background updates.

### Authenticate

After installation, run:

```bash
claude
```

This opens a browser window to log in with your Anthropic account.

---

## Ways to Use Claude Code

### Terminal (CLI)

The most direct way to use Claude Code. Run `claude` from any project directory in your terminal. Full access to all features including hooks, MCP servers, and agentic workflows.

### IDE Extensions

Claude Code has native extensions for the most widely used editors.

**VS Code, Cursor, and Windsurf**

Install the **Claude Code** extension from the Extensions panel (`Cmd+Shift+X` on Mac, `Ctrl+Shift+X` on Windows/Linux). It works in VS Code and in VS Code forks like Cursor and Windsurf without any additional setup.

The extension adds a graphical panel where you can review Claude's plans, accept edits as visual diffs, reference files with `@`-mentions, and manage multiple conversations in separate tabs. It includes the CLI, and conversation history is shared between the panel and the integrated terminal.

**JetBrains IDEs**

Claude Code is available inside JetBrains IDEs (IntelliJ IDEA, PyCharm, WebStorm, and others) through the **JetBrains AI** subscription. It runs directly in the AI chat panel — no extra plugins or logins required. Supports multi-file diffs, approval-based edits, and MCP server integration.

There is also a standalone **Claude Code (Beta)** plugin on the JetBrains Marketplace if you prefer to use it outside the JetBrains AI subscription.

### Claude Desktop App

Claude Code is available as a tab inside the **Claude Desktop app** (macOS and Windows). A good option if you want a GUI experience without setting up an IDE extension. The Desktop app also supports Remote Control, which lets you hand off tasks to your machine from your phone.

### Web — claude.ai/code

[claude.ai/code](https://claude.ai/code) runs entirely in a **managed sandbox on Anthropic's infrastructure** — no local clone or environment setup needed. Link a GitHub repository, describe the task, and Claude executes it end-to-end in an isolated environment, then opens a pull request when done. Useful for kicking off longer tasks or making quick fixes without opening your local dev environment.

### iOS (Mobile)

Claude Code sessions can be monitored and continued from the **Claude iOS app**. Particularly useful alongside Remote Sessions, which run on Anthropic's cloud and stay active even when your computer is off.

---

## Troubleshooting

### `claude: command not found`

Close and reopen your terminal. If the issue persists, add the install directory to your PATH manually:

```bash
# Add to ~/.zshrc or ~/.bashrc
export PATH="$HOME/.local/bin:$PATH"
source ~/.zshrc
```

### Permission errors during install

Do **not** use `sudo`. The native installer handles permissions automatically. If you previously used the npm install method, switch to the native installer instead.

### API key not working

Make sure your key is set and has no extra spaces:

```bash
export ANTHROPIC_API_KEY="your-key-here"
```

Get your key at [console.anthropic.com](https://console.anthropic.com).

### General diagnostics

Run these in order to identify most issues:

```bash
claude --version        # Is Claude Code installed?
echo $ANTHROPIC_API_KEY # Is the key set?
ping claude.ai          # Can it reach the network?
```

### Full reset

```bash
rm ~/.claude.json
rm -rf ~/.claude/
curl -fsSL https://claude.ai/install.sh | bash
```

---

## Resources

- [Claude Code Documentation](https://code.claude.com/docs/en/overview)
- [Anthropic Console (API keys)](https://console.anthropic.com)
- [Claude Code on the Web](https://claude.ai/code)
- [VS Code Extension](https://marketplace.visualstudio.com/items?itemName=Anthropic.claude-code)
- [JetBrains Plugin](https://plugins.jetbrains.com/plugin/27310-claude-code-beta-)
