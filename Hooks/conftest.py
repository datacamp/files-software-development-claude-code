"""pytest hook that logs results and sends desktop notifications.

This module provides a pytest plugin that automatically logs test results to a file
and sends native desktop notifications when the test session completes. It's designed
to work with Claude Code's PostToolUse hooks to provide immediate feedback when files
are modified and tests run automatically.

The module is OS-agnostic and sends notifications using the appropriate system call
for macOS (osascript), Linux (notify-send), or Windows (PowerShell).

Example usage:
    Place this file as conftest.py in your project root or tests/ directory.
    Configure Claude Code to run pytest via a PostToolUse hook:

        {
          "hooks": {
            "PostToolUse": [{
              "matcher": "Write|Edit|Update",
              "hooks": [{
                "type": "command",
                "command": "python -m pytest tests/ --tb=short -q"
              }]
            }]
          }
        }

    When pytest finishes, this plugin will:
    1. Log results with timestamp to /tmp/pytest_results.log
    2. Send a desktop notification showing pass/fail status
"""
import subprocess
import platform
from datetime import datetime

LOG_FILE = "/tmp/pytest_results.log"


def pytest_terminal_summary(terminalreporter, exitstatus, config):
    """Log test results to file and send a desktop notification.

    This pytest hook is automatically called by pytest when a test session completes.
    It extracts test statistics (passed, failed, errors), logs them to a file with
    a timestamp, and sends a native desktop notification showing the results.

    Args:
        terminalreporter: pytest's TerminalReporter object containing test statistics.
            Provides access to test counts via terminalreporter.stats dict with keys:
            'passed', 'failed', 'error', 'skipped', etc.
        exitstatus (int): The exit status code pytest will return (0 for success,
            non-zero for failures). Not used in this implementation but available
            for conditional logic if needed.
        config: pytest's Config object containing session configuration, not used
            in this implementation but available for accessing pytest settings.

    Returns:
        None

    Side effects:
        - Appends a log line to LOG_FILE (/tmp/pytest_results.log) with timestamp,
          title, and summary message.
        - Sends a native desktop notification via:
          * macOS: osascript (AppleScript)
          * Linux: notify-send
          * Windows: PowerShell New-BurntToastNotification

    Notes:
        - The notification title indicates pass/fail status: "pytest — PASSED" or
          "pytest — FAILED"
        - The message includes emoji indicators (✅ for pass, ❌ for fail) for
          visual clarity in both log files and notifications
        - If notify-send or osascript is not available, subprocess.run() will
          fail silently (no exception raised)
    """
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
    
    # Write to log file (for tmux + asciinema recording)
    with open(LOG_FILE, "a") as f:
        f.write(f"[{timestamp}] {title}: {message}\n")
    
    # Send desktop notification (for screen recording)
    system = platform.system()
    if system == "Darwin":  # macOS
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
