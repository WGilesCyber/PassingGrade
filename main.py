"""
PassingGrade — Password Compliance Checker
==========================================
Offline, zero-install tool for checking passwords against organizational policy.

SECURITY NOTE: This tool never saves, logs, or transmits passwords.
Passwords exist only in memory for the duration of the session.
"""
from __future__ import annotations

import argparse
import sys


def main() -> None:
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
