"""
Tests for password checker and individual rules.
Passwords used in tests are fictional examples only — never stored or logged.
"""
import pytest

from passinggrade.checker import (
    check,
    TIER_GREAT,
    TIER_GOOD,
    TIER_OK,
    TIER_NOT_COMPLIANT,
)
from passinggrade.config import Policy, ScoringConfig


def default_policy() -> Policy:
    """Return the hardcoded default policy for testing."""
    return Policy()


def strict_scoring() -> ScoringConfig:
    """Scoring that makes it easy to hit tier boundaries in tests."""
    return ScoringConfig(
        length_bonus_per_char_over_min=2,
        max_length_bonus=20,
        all_complexity_bonus=10,
        unique_chars_bonus_per_char=1,
        max_unique_chars_bonus=10,
    )


# ---------------------------------------------------------------------------
# Empty / trivial inputs
# ---------------------------------------------------------------------------

def test_empty_password_is_not_compliant():
    result = check("", default_policy())
    assert result.tier == TIER_NOT_COMPLIANT


def test_single_char_is_not_compliant():
    result = check("a", default_policy())
    assert result.tier == TIER_NOT_COMPLIANT


# ---------------------------------------------------------------------------
# Hard rule failures → Not Compliant
# ---------------------------------------------------------------------------

def test_too_short():
    policy = Policy(min_length=12)
    result = check("Short1!Aa", policy)
    assert result.tier == TIER_NOT_COMPLIANT
    rule = next(r for r in result.rules if r.name == "min_length")
    assert not rule.passed


def test_too_long():
    policy = Policy(max_length=10)
    result = check("A" * 11 + "b1!", policy)
    assert result.tier == TIER_NOT_COMPLIANT


def test_missing_uppercase():
    policy = Policy(require_uppercase=True, min_length=4)
    result = check("abcd1!", policy)
    assert result.tier == TIER_NOT_COMPLIANT
    rule = next(r for r in result.rules if r.name == "uppercase")
    assert not rule.passed


def test_missing_lowercase():
    policy = Policy(require_lowercase=True, min_length=4)
    result = check("ABCD1!", policy)
    assert result.tier == TIER_NOT_COMPLIANT
    rule = next(r for r in result.rules if r.name == "lowercase")
    assert not rule.passed


def test_missing_digit():
    policy = Policy(require_digit=True, min_length=4)
    result = check("Abcdef!", policy)
    assert result.tier == TIER_NOT_COMPLIANT
    rule = next(r for r in result.rules if r.name == "digit")
    assert not rule.passed


def test_missing_special():
    policy = Policy(require_special=True, min_length=4)
    result = check("Abcdef1", policy)
    assert result.tier == TIER_NOT_COMPLIANT
    rule = next(r for r in result.rules if r.name == "special")
    assert not rule.passed


def test_disallowed_space():
    policy = Policy(disallow_spaces=True, min_length=4)
    result = check("Ab 1!", policy)
    assert result.tier == TIER_NOT_COMPLIANT


def test_too_many_repeated_chars():
    policy = Policy(max_repeated_chars=3, min_length=4)
    result = check("Aaaa1!Bb", policy)
    assert result.tier == TIER_NOT_COMPLIANT


def test_common_password_blocked():
    policy = Policy(disallow_common=True, min_length=4,
                    require_uppercase=False, require_lowercase=True,
                    require_digit=False, require_special=False,
                    max_repeated_chars=99, disallow_sequences=False)
    result = check("password", policy)
    assert result.tier == TIER_NOT_COMPLIANT
    rule = next(r for r in result.rules if r.name == "common")
    assert not rule.passed


def test_sequence_blocked():
    policy = Policy(disallow_sequences=True, min_sequence_length=4, min_length=4,
                    require_uppercase=False, require_digit=False, require_special=False,
                    max_repeated_chars=99, disallow_common=False)
    result = check("abcdef!X", policy)
    assert result.tier == TIER_NOT_COMPLIANT
    rule = next(r for r in result.rules if r.name == "sequences")
    assert not rule.passed


def test_keyboard_sequence_blocked():
    policy = Policy(disallow_sequences=True, min_sequence_length=4, min_length=4,
                    require_uppercase=False, require_digit=False, require_special=False,
                    max_repeated_chars=99, disallow_common=False)
    result = check("qwerty!X", policy)
    assert result.tier == TIER_NOT_COMPLIANT


# ---------------------------------------------------------------------------
# Rules disabled by policy → should not cause failure
# ---------------------------------------------------------------------------

def test_uppercase_not_required():
    policy = Policy(require_uppercase=False, min_length=4,
                    require_digit=False, require_special=False,
                    disallow_common=False, disallow_sequences=False, max_repeated_chars=99)
    result = check("abcdabcd", policy)
    rule = next(r for r in result.rules if r.name == "uppercase")
    assert rule.passed


def test_spaces_allowed_when_not_disallowed():
    policy = Policy(disallow_spaces=False, min_length=4,
                    require_uppercase=False, require_digit=False, require_special=False,
                    disallow_common=False, disallow_sequences=False, max_repeated_chars=99)
    result = check("abcd efgh", policy)
    rule = next(r for r in result.rules if r.name == "no_spaces")
    assert rule.passed


# ---------------------------------------------------------------------------
# Tier boundary tests
# ---------------------------------------------------------------------------

def _make_policy_for_scoring() -> Policy:
    """Policy that allows precise control over scoring."""
    return Policy(
        min_length=8,
        max_length=128,
        require_uppercase=True,
        require_lowercase=True,
        require_digit=True,
        require_special=True,
        disallow_spaces=False,
        max_repeated_chars=99,
        disallow_common=False,
        disallow_sequences=False,
        min_unique_chars=4,
        scoring=ScoringConfig(
            length_bonus_per_char_over_min=2,
            max_length_bonus=20,
            all_complexity_bonus=10,
            unique_chars_bonus_per_char=1,
            max_unique_chars_bonus=10,
        ),
    )


def test_tier_ok_at_base_score():
    """Password meeting exactly the minimum requirements should score 50 (Ok)."""
    policy = _make_policy_for_scoring()
    # 8 chars, all 4 classes, 8 unique → base 50 + 0 length bonus + 10 complexity + 4 unique = 64 → Ok
    result = check("Aa1!Bb2@", policy)
    assert result.tier == TIER_OK
    assert result.score < 70


def test_tier_good_with_extra_length():
    """Adding chars to push score into 70–89 range gives Good."""
    policy = _make_policy_for_scoring()
    # 8 base + 10 extra = 18 chars → length bonus = 10*2 = 20 (capped at 20)
    # base 50 + 20 length + 10 complexity + unique bonus → ≥ 70
    pw = "Aa1!Bb2@CcDdEeFfGg"  # 18 chars, all classes, many unique
    result = check(pw, policy)
    assert result.tier in (TIER_GOOD, TIER_GREAT)


def test_tier_not_compliant_has_zero_score():
    result = check("short", default_policy())
    assert result.score == 0
    assert result.tier == TIER_NOT_COMPLIANT


def test_compliant_password_has_positive_score():
    result = check("Tr0ub4dor&3!", default_policy())
    assert result.score > 0
    assert result.tier != TIER_NOT_COMPLIANT


# ---------------------------------------------------------------------------
# Result properties
# ---------------------------------------------------------------------------

def test_result_label_not_compliant():
    result = check("", default_policy())
    assert result.label == "Not Compliant"


def test_result_is_compliant_flag():
    bad = check("", default_policy())
    assert not bad.is_compliant

    good = check("Tr0ub4dor&3!XYZ", default_policy())
    assert good.is_compliant


def test_result_color_is_string():
    result = check("Tr0ub4dor&3!", default_policy())
    assert result.color.startswith("#")


# ---------------------------------------------------------------------------
# Unicode safety
# ---------------------------------------------------------------------------

def test_unicode_password_counted_correctly():
    """len() on a Unicode password must count characters, not bytes."""
    policy = Policy(min_length=4, require_uppercase=False, require_lowercase=False,
                    require_digit=False, require_special=False,
                    disallow_common=False, disallow_sequences=False, max_repeated_chars=99)
    # 4 emoji characters — each is multiple bytes but should count as 4 chars
    result = check("🔒🔑🛡️🔐", policy)
    rule = next(r for r in result.rules if r.name == "min_length")
    assert rule.passed
