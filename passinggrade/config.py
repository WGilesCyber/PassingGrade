"""
Password policy configuration loader.

Passwords are never stored, logged, or transmitted by this tool.
Policy files contain only rules — never passwords or examples.
"""
from __future__ import annotations

import json
import os
import sys
from dataclasses import dataclass, field


@dataclass
class ScoringConfig:
    # Points added per character above min_length (capped at max_length_bonus)
    length_bonus_per_char_over_min: int = 2
    # Maximum total points that the length bonus can contribute
    max_length_bonus: int = 20
    # Bonus awarded when all four complexity classes are present (upper, lower, digit, special)
    all_complexity_bonus: int = 10
    # Points added per unique character above min_unique_chars (capped at max_unique_chars_bonus)
    unique_chars_bonus_per_char: int = 1
    # Maximum total points that the unique-character bonus can contribute
    max_unique_chars_bonus: int = 10


@dataclass
class Policy:
    policy_name: str = "Default Password Policy"
    # --- Hard rules (failure → Not Compliant regardless of score) ---
    min_length: int = 12           # Minimum accepted password length (characters, not bytes)
    max_length: int = 128          # Maximum accepted password length
    require_uppercase: bool = True  # At least one A-Z character required
    require_lowercase: bool = True  # At least one a-z character required
    require_digit: bool = True      # At least one 0-9 character required
    require_special: bool = True    # At least one character from special_chars required
    special_chars: str = "!@#$%^&*()_+-=[]{}|;':\",./<>?"  # Allowed special characters
    disallow_spaces: bool = False   # If True, spaces anywhere in the password are rejected
    max_repeated_chars: int = 3     # Longest run of the same character allowed (e.g. 3 → "aaa" ok, "aaaa" fails)
    disallow_common: bool = True    # If True, reject passwords found in the common-passwords list
    disallow_sequences: bool = True # If True, reject passwords containing keyboard/alpha/numeric sequences
    min_sequence_length: int = 4    # Minimum contiguous sequence length that triggers a sequence failure
    # --- Soft scoring (affects tier but never causes Not Compliant) ---
    min_unique_chars: int = 8       # Threshold for unique-character bonus; passwords below this still pass
    scoring: ScoringConfig = field(default_factory=ScoringConfig)


# ---------------------------------------------------------------------------
# Validation helpers
# ---------------------------------------------------------------------------

def _require_bool(name: str, value: object) -> bool:
    # JSON booleans arrive as Python bool; anything else is a mis-configured field
    if not isinstance(value, bool):
        raise ValueError(f"'{name}' must be true or false, got: {value!r}")
    return value


def _require_int(name: str, value: object, min_val: int, max_val: int) -> int:
    # Explicitly reject booleans: in Python, bool is a subclass of int, so
    # isinstance(True, int) is True — the extra check prevents accepting true/false
    # as numeric values (which would silently coerce to 1/0)
    if not isinstance(value, int) or isinstance(value, bool):
        raise ValueError(f"'{name}' must be an integer, got: {value!r}")
    if not (min_val <= value <= max_val):
        raise ValueError(
            f"'{name}' must be between {min_val} and {max_val}, got: {value}"
        )
    return value


def _validate_policy_data(rules: object, scoring: object) -> None:
    """
    Raise ValueError with a descriptive message if any policy field has an
    incorrect type or an out-of-bounds value.
    """
    if not isinstance(rules, dict):
        raise ValueError("'rules' must be a JSON object (dictionary)")
    if not isinstance(scoring, dict):
        raise ValueError("'scoring' must be a JSON object (dictionary)")

    # Integer bounds
    min_len = rules.get("min_length", 12)
    max_len = rules.get("max_length", 128)
    _require_int("min_length", min_len, 1, 1000)
    _require_int("max_length", max_len, 1, 10000)
    if min_len > max_len:
        raise ValueError(
            f"'min_length' ({min_len}) must not be greater than 'max_length' ({max_len})"
        )

    for name, default, lo, hi in [
        ("max_repeated_chars",  3,  1, 100),
        ("min_unique_chars",    8,  0, 128),
        ("min_sequence_length", 4,  2,  20),
    ]:
        val = rules.get(name, default)
        _require_int(name, val, lo, hi)

    # Boolean flags
    for flag in (
        "require_uppercase", "require_lowercase", "require_digit",
        "require_special", "disallow_spaces", "disallow_common",
        "disallow_sequences",
    ):
        val = rules.get(flag)
        if val is not None:
            _require_bool(flag, val)

    # special_chars
    sc = rules.get("special_chars")
    if sc is not None:
        if not isinstance(sc, str):
            raise ValueError(f"'special_chars' must be a string, got: {sc!r}")
        if len(sc) == 0:
            raise ValueError("'special_chars' must not be empty")

    # Scoring integers (non-negative)
    for name, default in [
        ("length_bonus_per_char_over_min", 2),
        ("max_length_bonus",               20),
        ("all_complexity_bonus",           10),
        ("unique_chars_bonus_per_char",     1),
        ("max_unique_chars_bonus",         10),
    ]:
        val = scoring.get(name, default)
        _require_int(name, val, 0, 10000)


# ---------------------------------------------------------------------------
# Parser
# ---------------------------------------------------------------------------

def _parse_policy(data: dict) -> Policy:
    rules = data.get("rules", {})
    scoring_data = data.get("scoring", {})

    # Validate before trusting any values
    _validate_policy_data(rules, scoring_data)

    scoring = ScoringConfig(
        length_bonus_per_char_over_min=scoring_data.get("length_bonus_per_char_over_min", 2),
        max_length_bonus=scoring_data.get("max_length_bonus", 20),
        all_complexity_bonus=scoring_data.get("all_complexity_bonus", 10),
        unique_chars_bonus_per_char=scoring_data.get("unique_chars_bonus_per_char", 1),
        max_unique_chars_bonus=scoring_data.get("max_unique_chars_bonus", 10),
    )

    return Policy(
        policy_name=data.get("policy_name", "Password Policy"),
        min_length=rules.get("min_length", 12),
        max_length=rules.get("max_length", 128),
        require_uppercase=rules.get("require_uppercase", True),
        require_lowercase=rules.get("require_lowercase", True),
        require_digit=rules.get("require_digit", True),
        require_special=rules.get("require_special", True),
        special_chars=rules.get("special_chars", "!@#$%^&*()_+-=[]{}|;':\",./<>?"),
        disallow_spaces=rules.get("disallow_spaces", False),
        max_repeated_chars=rules.get("max_repeated_chars", 3),
        disallow_common=rules.get("disallow_common", True),
        disallow_sequences=rules.get("disallow_sequences", True),
        min_sequence_length=rules.get("min_sequence_length", 4),
        min_unique_chars=rules.get("min_unique_chars", 8),
        scoring=scoring,
    )


# ---------------------------------------------------------------------------
# Loader
# ---------------------------------------------------------------------------

def _exe_dir() -> str:
    """Return the directory containing the running executable or script.

    PyInstaller sets sys.frozen = True and bundles everything into a single
    executable. In that case we want the directory of the .exe, not the
    unpacked temp directory (sys._MEIPASS). When running from source, we
    use the directory of the entry-point script (sys.argv[0]).
    """
    if getattr(sys, "frozen", False):
        # Running as a PyInstaller-packed executable
        return os.path.dirname(sys.executable)
    # Running as a normal Python script
    return os.path.dirname(os.path.abspath(sys.argv[0]))


def load_policy(explicit_path: str | None = None) -> tuple[Policy, str | None]:
    """
    Load the password policy from a JSON file.

    Search order:
      1. explicit_path (from --policy flag)
      2. policy/policy.json next to the executable
      3. policy/policy.json in the current working directory
      4. Hardcoded NIST-aligned defaults

    Returns (policy, error_message). error_message is None on success,
    or a string describing the problem (the caller shows a dialog and
    falls back to defaults).
    """
    candidates: list[str] = []

    if explicit_path:
        # Normalize to prevent directory traversal via relative path components
        candidates.append(os.path.normpath(os.path.abspath(explicit_path)))

    candidates.append(os.path.join(_exe_dir(), "policy", "policy.json"))
    candidates.append(os.path.join(os.getcwd(), "policy", "policy.json"))

    for path in candidates:
        if os.path.isfile(path):
            try:
                with open(path, "r", encoding="utf-8") as fh:
                    data = json.load(fh)
                return _parse_policy(data), None
            except json.JSONDecodeError as exc:
                return Policy(), (
                    f"Could not read policy file:\n{path}\n\n"
                    f"JSON error: {exc}\n\n"
                    "Using built-in default policy."
                )
            except ValueError as exc:
                return Policy(), (
                    f"Invalid policy file:\n{path}\n\n"
                    f"{exc}\n\n"
                    "Using built-in default policy."
                )
            except (OSError, IOError) as exc:
                return Policy(), (
                    f"Could not read policy file:\n{path}\n\n"
                    f"File error: {exc}\n\n"
                    "Using built-in default policy."
                )

    # No file found — silently use defaults
    return Policy(), None
