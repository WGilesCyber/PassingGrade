"""
Individual password rule functions.

All functions are pure: they take a password string and policy values,
return a result, and have no side effects. Passwords are never persisted.
"""
from __future__ import annotations

import os
import sys
import warnings
from dataclasses import dataclass

from passinggrade.config import Policy


@dataclass
class RuleResult:
    name: str
    passed: bool
    message: str
    is_hard: bool  # True = required (fail → Not Compliant); False = bonus only


# ---------------------------------------------------------------------------
# Common-password list — loaded once into a set for O(1) lookup
# ---------------------------------------------------------------------------

def _load_common_passwords() -> set[str]:
    # When bundled by PyInstaller the assets live under sys._MEIPASS
    if getattr(sys, "frozen", False):
        base = sys._MEIPASS  # type: ignore[attr-defined]
    else:
        base = os.path.join(os.path.dirname(__file__), "..", "assets")

    path = os.path.join(base, "common_passwords.txt")
    try:
        with open(path, "r", encoding="utf-8") as fh:
            return {line.strip().lower() for line in fh if line.strip()}
    except FileNotFoundError:
        warnings.warn(
            f"Common passwords file not found: {path}. "
            "Common password check will not block known weak passwords.",
            RuntimeWarning,
            stacklevel=2,
        )
        return set()


_COMMON_PASSWORDS: set[str] = _load_common_passwords()

# ---------------------------------------------------------------------------
# Sequence tables used for keyboard / alpha / numeric sequence detection
# ---------------------------------------------------------------------------

_SEQUENCES: list[str] = [
    "abcdefghijklmnopqrstuvwxyz",
    "zyxwvutsrqponmlkjihgfedcba",
    "0123456789",
    "9876543210",
    "qwertyuiop",
    "poiuytrewq",
    "asdfghjkl",
    "lkjhgfdsa",
    "zxcvbnm",
    "mnbvcxz",
    "!@#$%^&*()",
    ")(*&^%$#@!",
]


# ---------------------------------------------------------------------------
# Individual rule functions
# ---------------------------------------------------------------------------

def check_min_length(password: str, policy: Policy) -> RuleResult:
    # password is not persisted
    length = len(password)
    passed = length >= policy.min_length
    return RuleResult(
        name="min_length",
        passed=passed,
        message=(
            f"At least {policy.min_length} characters"
            if passed
            else f"At least {policy.min_length} characters (found {length})"
        ),
        is_hard=True,
    )


def check_max_length(password: str, policy: Policy) -> RuleResult:
    # password is not persisted
    length = len(password)
    passed = length <= policy.max_length
    return RuleResult(
        name="max_length",
        passed=passed,
        message=(
            f"No more than {policy.max_length} characters"
            if passed
            else f"No more than {policy.max_length} characters (found {length})"
        ),
        is_hard=True,
    )


def check_uppercase(password: str, policy: Policy) -> RuleResult:
    # password is not persisted
    if not policy.require_uppercase:
        return RuleResult(
            name="uppercase", passed=True,
            message="Uppercase letter (not required by policy)", is_hard=False
        )
    passed = any(c.isupper() for c in password)
    return RuleResult(
        name="uppercase",
        passed=passed,
        message="Contains an uppercase letter",
        is_hard=True,
    )


def check_lowercase(password: str, policy: Policy) -> RuleResult:
    # password is not persisted
    if not policy.require_lowercase:
        return RuleResult(
            name="lowercase", passed=True,
            message="Lowercase letter (not required by policy)", is_hard=False
        )
    passed = any(c.islower() for c in password)
    return RuleResult(
        name="lowercase",
        passed=passed,
        message="Contains a lowercase letter",
        is_hard=True,
    )


def check_digit(password: str, policy: Policy) -> RuleResult:
    # password is not persisted
    if not policy.require_digit:
        return RuleResult(
            name="digit", passed=True,
            message="Number (not required by policy)", is_hard=False
        )
    passed = any(c.isdigit() for c in password)
    return RuleResult(
        name="digit",
        passed=passed,
        message="Contains a number",
        is_hard=True,
    )


def check_special(password: str, policy: Policy) -> RuleResult:
    # password is not persisted
    if not policy.require_special:
        return RuleResult(
            name="special", passed=True,
            message="Special character (not required by policy)", is_hard=False
        )
    special_set = set(policy.special_chars)
    passed = any(c in special_set for c in password)
    return RuleResult(
        name="special",
        passed=passed,
        message="Contains a special character",
        is_hard=True,
    )


def check_no_spaces(password: str, policy: Policy) -> RuleResult:
    # password is not persisted
    if not policy.disallow_spaces:
        return RuleResult(
            name="no_spaces", passed=True,
            message="No spaces (spaces allowed by policy)", is_hard=False
        )
    passed = " " not in password
    return RuleResult(
        name="no_spaces",
        passed=passed,
        message="Does not contain spaces",
        is_hard=True,
    )


def check_max_repeated(password: str, policy: Policy) -> RuleResult:
    # password is not persisted
    limit = policy.max_repeated_chars
    # Single-pass run-length scan: compare each character to its predecessor.
    # current_run tracks the active streak; max_run records the longest seen.
    max_run = 1
    current_run = 1
    for i in range(1, len(password)):
        if password[i] == password[i - 1]:
            current_run += 1
            max_run = max(max_run, current_run)
        else:
            current_run = 1

    passed = max_run <= limit
    return RuleResult(
        name="max_repeated",
        passed=passed,
        message=f"No character repeated more than {limit} times in a row",
        is_hard=True,
    )


def check_common_passwords(password: str, policy: Policy) -> RuleResult:
    # password is not persisted
    if not policy.disallow_common:
        return RuleResult(
            name="common", passed=True,
            message="Common password check (disabled by policy)", is_hard=False
        )
    passed = password.lower() not in _COMMON_PASSWORDS
    return RuleResult(
        name="common",
        passed=passed,
        message="Not a commonly used password",
        is_hard=True,
    )


def check_sequences(password: str, policy: Policy) -> RuleResult:
    # password is not persisted
    if not policy.disallow_sequences:
        return RuleResult(
            name="sequences", passed=True,
            message="Sequence check (disabled by policy)", is_hard=False
        )
    min_len = policy.min_sequence_length
    # Case-insensitive: compare lowercase password against lowercase sequence table
    pw_lower = password.lower()
    # Sliding-window approach: for each known sequence, extract every consecutive
    # chunk of length min_len and check whether it appears anywhere in the password
    for seq in _SEQUENCES:
        for start in range(len(seq) - min_len + 1):
            chunk = seq[start: start + min_len]
            if chunk in pw_lower:
                return RuleResult(
                    name="sequences",
                    passed=False,
                    message=f"No predictable sequences (e.g. abc, 123, qwerty)",
                    is_hard=True,
                )
    return RuleResult(
        name="sequences",
        passed=True,
        message="No predictable sequences",
        is_hard=True,
    )


def check_unique_chars(password: str, policy: Policy) -> RuleResult:
    # password is not persisted — soft/bonus rule only
    unique_count = len(set(password))
    passed = unique_count >= policy.min_unique_chars
    return RuleResult(
        name="unique_chars",
        passed=passed,
        message=f"At least {policy.min_unique_chars} unique characters",
        is_hard=False,  # contributes to score but not a hard gate
    )


# ---------------------------------------------------------------------------
# Ordered list of all rules; checker.py iterates this
# ---------------------------------------------------------------------------

# Order matters: checker.py iterates this list in sequence, and the UI
# displays rules in the same order via _DISPLAY_RULES in app.py
ALL_RULES = [
    check_min_length,
    check_max_length,
    check_uppercase,
    check_lowercase,
    check_digit,
    check_special,
    check_no_spaces,
    check_max_repeated,
    check_common_passwords,
    check_sequences,
    check_unique_chars,  # Soft rule only — contributes to score but never causes Not Compliant
]
