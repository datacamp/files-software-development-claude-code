# Claude Code PostToolUse Hook

Automatically run tests when Claude Code modifies files.

## Configuration

Add this to:
- **Global:** `~/.claude/settings.json` (applies to all projects)
- **Project-level:** `.claude/settings.local.json` in your project root (this project only)

```json
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Write|Edit|Update",
        "hooks": [
          {
            "type": "command",
            "command": "cd $CLAUDE_PROJECT_DIR && python -m pytest tests/ --tb=short -q"
          }
        ]
      }
    ]
  }
}
```

## How It Works

When Claude Code writes or edits a file:
1. Hook automatically triggers
2. pytest runs on your test suite
3. Results logged to `/tmp/pytest_results.log`
4. Desktop notification sent with pass/fail status

## Requirements

- Python in PATH
- pytest installed

## Customize the Command

Change the test directory or add flags:

```json
"command": "cd $CLAUDE_PROJECT_DIR && python -m pytest path/to/tests/ -v"
```

## Enhanced Notifications (Optional)

Add a `conftest.py` in your project root or `tests/` directory for formatted notifications with emoji indicators:

```python
"""pytest hook that logs results and sends desktop notifications."""
import subprocess
import platform
from datetime import datetime

LOG_FILE = "/tmp/pytest_results.log"

def pytest_terminal_summary(terminalreporter, exitstatus, config):
    """Log test results and send desktop notification."""
    passed = len(terminalreporter.stats.get('passed', []))
    failed = len(terminalreporter.stats.get('failed', []))
    errors = len(terminalreporter.stats.get('error', []))
    timestamp = datetime.now().strftime("%H:%M:%S")
    
    if failed or errors:
        message = f"❌ {failed} failed, {errors} errors — {passed} passed"
        title = "pytest — FAILED"
    else:
        message = f"✅ All {passed} tests passed!"
        title = "pytest — PASSED"
    
    with open(LOG_FILE, "a") as f:
        f.write(f"[{timestamp}] {title}: {message}\n")
    
    system = platform.system()
    if system == "Darwin":
        subprocess.run([
            "osascript", "-e",
            f'display notification "{message}" with title "{title}"'
        ])
    elif system == "Linux":
        subprocess.run(["notify-send", title, message])
    elif system == "Windows":
        subprocess.run([
            "powershell", "-Command",
            f'New-BurntToastNotification -Text "{title}", "{message}"'
        ])
```
