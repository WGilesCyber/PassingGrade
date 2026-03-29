"""
PassingGrade — Password Compliance Checker
==========================================
Offline, zero-install tool for checking passwords against organizational policy.

SECURITY NOTE: This tool never saves, logs, or transmits passwords.
Passwords exist only in memory for the duration of the session.
"""
from __future__ import annotations

import argparse
import ctypes
import sys


def _configure_windows() -> None:
    """Apply Windows-specific process settings before any UI is created.

    DPI awareness: prevents blurry rendering on high-DPI / 4K displays.
    App User Model ID: lets Windows group the window correctly in the taskbar
    and allows the app to be pinned to the Start menu / taskbar.
    """
    try:
        # PROCESS_SYSTEM_DPI_AWARE — crisp on high-DPI displays
        ctypes.windll.shcore.SetProcessDpiAwareness(1)
    except (AttributeError, OSError):
        try:
            ctypes.windll.user32.SetProcessDPIAware()
        except (AttributeError, OSError):
            pass
    try:
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(
            "PassingGrade.PasswordChecker.1"
        )
    except (AttributeError, OSError):
        pass


def main() -> None:
    _configure_windows()

    parser = argparse.ArgumentParser(
        description="PassingGrade — Password Compliance Checker"
    )
    # --policy lets deployers point at a custom JSON without changing code
    parser.add_argument(
        "--policy",
        metavar="PATH",
        default=None,
        help="Path to a custom policy.json file",
    )
    args = parser.parse_args()

    # Deferred imports keep startup fast and avoid circular-import issues
    # when this module is imported by tests rather than run directly
    from passinggrade.config import load_policy
    from passinggrade.ui.app import PassingGradeApp, show_error_dialog

    # load_policy never raises — it returns (policy, error) so the app can
    # show a dialog and still run using built-in defaults if the file is bad
    policy, error = load_policy(explicit_path=args.policy)

    if error:
        # Show the error to the user but continue with default policy;
        # crashing on a bad config file would be worse than running with defaults
        show_error_dialog(error)

    app = PassingGradeApp(policy=policy)
    app.mainloop()


if __name__ == "__main__":
    main()
