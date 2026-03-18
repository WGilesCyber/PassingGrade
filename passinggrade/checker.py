"""
Password compliance checker.

Passwords are never stored, logged, or transmitted by this tool.
check() is a pure function: it receives a password, evaluates it, and
returns a Result. Nothing is written to disk, network, or logs.
"""
from __future__ import annotations

from dataclasses import dataclass, field

from passinggrade.config import Policy
from passinggrade.rules import ALL_RULES, RuleResult

TIER_GREAT = "great"
TIER_GOOD = "good"
TIER_OK = "ok"
TIER_NOT_COMPLIANT = "not_compliant"

TIER_LABELS = {
    TIER_GREAT: "Great",
    TIER_GOOD: "Good",
    TIER_OK: "Ok",
    TIER_NOT_COMPLIANT: "Not Compliant",
}

TIER_DESCRIPTIONS = {
    TIER_GREAT: "Your password exceeds all requirements.",
    TIER_GOOD: "Your password meets all requirements.",
    TIER_OK: "Your password meets the minimum requirements.",
    TIER_NOT_COMPLIANT: "Your password does not meet the requirements.",
}

TIER_COLORS = {
    TIER_GREAT: "#1B5E20",
    TIER_GOOD: "#0D47A1",
    TIER_OK: "#E65100",
    TIER_NOT_COMPLIANT: "#B71C1C",
}


@dataclass
class Result:
    tier: str
    score: int
    rules: list[RuleResult] = field(default_factory=list)

    @property
    def label(self) -> str:
        return TIER_LABELS[self.tier]

    @property
    def description(self) -> str:
        return TIER_DESCRIPTIONS[self.tier]

    @property
    def color(self) -> str:
        return TIER_COLORS[self.tier]

    @property
    def is_compliant(self) -> bool:
        return self.tier != TIER_NOT_COMPLIANT


def check(password: str, policy: Policy) -> Result:
    """
    Evaluate a password against the given policy.

    password is not persisted — it is evaluated in memory and discarded.
    Returns a Result containing the compliance tier, score, and per-rule results.
    """
    if not password:
        return Result(tier=TIER_NOT_COMPLIANT, score=0, rules=[])

    rule_results: list[RuleResult] = [rule_fn(password, policy) for rule_fn in ALL_RULES]

    # --- Hard gate: any required rule failure → Not Compliant ---
    for r in rule_results:
        if r.is_hard and not r.passed:
            return Result(tier=TIER_NOT_COMPLIANT, score=0, rules=rule_results)

    # --- Scoring for passing passwords ---
    score = 50  # base score for meeting all hard requirements

    s = policy.scoring
    length = len(password)
    length_over = max(0, length - policy.min_length)
    length_bonus = min(length_over * s.length_bonus_per_char_over_min, s.max_length_bonus)
    score += length_bonus

    # Bonus if all four complexity classes are present (even if only 3 required)
    has_upper = any(c.isupper() for c in password)
    has_lower = any(c.islower() for c in password)
    has_digit = any(c.isdigit() for c in password)
    special_set = set(policy.special_chars)
    has_special = any(c in special_set for c in password)
    if has_upper and has_lower and has_digit and has_special:
        score += s.all_complexity_bonus

    # Bonus for unique character count beyond minimum
    unique_count = len(set(password))
    unique_over = max(0, unique_count - policy.min_unique_chars)
    unique_bonus = min(unique_over * s.unique_chars_bonus_per_char, s.max_unique_chars_bonus)
    score += unique_bonus

    # --- Map score to tier ---
    if score >= 90:
        tier = TIER_GREAT
    elif score >= 70:
        tier = TIER_GOOD
    else:
        tier = TIER_OK

    return Result(tier=tier, score=score, rules=rule_results)
