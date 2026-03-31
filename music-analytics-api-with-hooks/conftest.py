"""pytest hook that logs test results."""
import subprocess
from datetime import datetime

LOG_FILE = "/tmp/pytest_results.log"


def pytest_terminal_summary(terminalreporter, exitstatus, config):
    """Log test results to file."""
    passed = len(terminalreporter.stats.get('passed', []))
    failed = len(terminalreporter.stats.get('failed', []))
    errors = len(terminalreporter.stats.get('error', []))
    timestamp = datetime.now().strftime("%H:%M:%S")
    
    if failed or errors:
        message = f"{failed} failed, {errors} errors, {passed} passed"
        title = "pytest FAILED"
    else:
        message = f"All {passed} tests passed!"
        title = "pytest PASSED"
    
    with open(LOG_FILE, "a") as f:
        f.write(f"[{timestamp}] {title}: {message}\n")
    
    try:
        subprocess.run(
            ["notify-send", title, message],
            check=False, capture_output=True
        )
    except Exception:
        pass
