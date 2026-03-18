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
    parser.add_argument(
        "--policy",
        metavar="PATH",
        default=None,
        help="Path to a custom policy.json file",
    )
    args = parser.parse_args()

    from passinggrade.config import load_policy
    from passinggrade.ui.app import PassingGradeApp, show_error_dialog

    policy, error = load_policy(explicit_path=args.policy)

    if error:
        show_error_dialog(error)

    app = PassingGradeApp(policy=policy)
    app.mainloop()


if __name__ == "__main__":
    main()
