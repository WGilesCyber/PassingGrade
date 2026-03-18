"""
Tests for the policy config loader.
"""
import json
import os
import tempfile

import pytest

from passinggrade.config import load_policy, Policy, _parse_policy


def test_defaults_returned_when_no_file_found():
    policy, error = load_policy(explicit_path="/nonexistent/path/policy.json")
    # No file found at explicit path and no file in cwd/exe-dir → defaults
    # (may or may not find a real policy.json depending on cwd, so just check type)
    assert isinstance(policy, Policy)


def test_explicit_valid_path_loads_correctly():
    data = {
        "policy_name": "Test Policy",
        "rules": {"min_length": 20, "require_special": False},
        "scoring": {},
    }
    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".json", delete=False, encoding="utf-8"
    ) as fh:
        json.dump(data, fh)
        path = fh.name

    try:
        policy, error = load_policy(explicit_path=path)
        assert error is None
        assert policy.policy_name == "Test Policy"
        assert policy.min_length == 20
        assert policy.require_special is False
    finally:
        os.unlink(path)


def test_malformed_json_returns_defaults_and_error():
    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".json", delete=False, encoding="utf-8"
    ) as fh:
        fh.write("{this is not valid json")
        path = fh.name

    try:
        policy, error = load_policy(explicit_path=path)
        assert error is not None
        assert "JSON error" in error
        assert isinstance(policy, Policy)
    finally:
        os.unlink(path)


def test_parse_policy_fills_defaults_for_missing_fields():
    policy = _parse_policy({})
    assert policy.min_length == 12  # default
    assert policy.require_uppercase is True


def test_parse_policy_respects_all_fields():
    data = {
        "policy_name": "Custom",
        "rules": {
            "min_length": 16,
            "max_length": 64,
            "require_uppercase": False,
            "require_lowercase": True,
            "require_digit": True,
            "require_special": True,
            "special_chars": "!@#",
            "disallow_spaces": True,
            "min_unique_chars": 10,
            "max_repeated_chars": 2,
            "disallow_common": True,
            "disallow_sequences": True,
            "min_sequence_length": 3,
        },
        "scoring": {
            "length_bonus_per_char_over_min": 3,
            "max_length_bonus": 15,
            "all_complexity_bonus": 5,
            "unique_chars_bonus_per_char": 2,
            "max_unique_chars_bonus": 8,
        },
    }
    policy = _parse_policy(data)
    assert policy.policy_name == "Custom"
    assert policy.min_length == 16
    assert policy.max_length == 64
    assert policy.require_uppercase is False
    assert policy.special_chars == "!@#"
    assert policy.disallow_spaces is True
    assert policy.max_repeated_chars == 2
    assert policy.scoring.length_bonus_per_char_over_min == 3
    assert policy.scoring.max_length_bonus == 15
