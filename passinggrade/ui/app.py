"""
Main application window.

Passwords typed into the entry field are never written to disk, logged,
or transmitted. They exist only in memory for the duration of the session.
"""
from __future__ import annotations

import tkinter as tk

import customtkinter as ctk

from passinggrade.checker import check, TIER_NOT_COMPLIANT
from passinggrade.config import Policy
from passinggrade.ui.result_card import ResultCard

# Rule names shown in the checklist, in display order.
# "unique_chars" is intentionally absent: it is a soft/bonus-only rule that
# affects score but is never a hard requirement, so showing it as a pass/fail
# item would be misleading to users.
# Rules disabled by policy are hidden at render time (see _update_rule_rows).
_DISPLAY_RULES = [
    "min_length",
    "max_length",
    "uppercase",
    "lowercase",
    "digit",
    "special",
    "no_spaces",
    "max_repeated",
    "common",
    "sequences",
]

_CHECK_MARK = "✓"
_CROSS_MARK = "✗"
_COLOR_PASS = "#2E7D32"
_COLOR_FAIL = "#B71C1C"
_COLOR_NEUTRAL = "#888888"


class PassingGradeApp(ctk.CTk):
    def __init__(self, policy: Policy):
        super().__init__()

        self._policy = policy
        self._show_password = False  # Tracks whether the entry field shows plain text or bullets

        # Window setup
        self._appearance_mode = "dark"
        self.title("PassingGrade")
        self.resizable(True, True)
        self.minsize(480, 520)
        self.geometry("480x620")
        ctk.set_appearance_mode(self._appearance_mode)
        ctk.set_default_color_theme("blue")

        self._build_ui()

    # ------------------------------------------------------------------
    # UI construction
    # ------------------------------------------------------------------

    def _build_ui(self) -> None:
        # --- Header ---
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.pack(fill="x", padx=20, pady=(18, 0))

        ctk.CTkLabel(
            header_frame,
            text="PassingGrade",
            font=ctk.CTkFont(family="Segoe UI", size=22, weight="bold"),
            anchor="w",
        ).pack(side="left")

        ctk.CTkLabel(
            header_frame,
            text=self._policy.policy_name,
            font=ctk.CTkFont(family="Segoe UI", size=12),
            text_color="#888888",
            anchor="e",
        ).pack(side="right")

        self._mode_btn = ctk.CTkButton(
            header_frame,
            text="☀",
            width=32,
            height=28,
            font=ctk.CTkFont(family="Segoe UI", size=16),
            fg_color="transparent",
            hover_color="#555555",  # updated per-mode in _toggle_mode
            border_width=1,
            border_color="#888888",  # visible outline in both light and dark mode
            command=self._toggle_mode,
        )
        self._mode_btn.pack(side="right", padx=(0, 8))

        ctk.CTkFrame(self, height=1, fg_color="#444444").pack(fill="x", padx=20, pady=(8, 0))

        # --- Password entry ---
        ctk.CTkLabel(
            self,
            text="Enter your password:",
            font=ctk.CTkFont(family="Segoe UI", size=14),
            anchor="w",
        ).pack(fill="x", padx=20, pady=(14, 4))

        entry_frame = ctk.CTkFrame(self, fg_color="transparent")
        entry_frame.pack(fill="x", padx=20, pady=(0, 14))

        # password is not persisted — StringVar holds it only in memory
        self._password_var = tk.StringVar()
        self._password_var.trace_add("write", self._on_password_change)

        self._entry = ctk.CTkEntry(
            entry_frame,
            textvariable=self._password_var,
            show="•",
            font=ctk.CTkFont(family="Segoe UI", size=15),
            height=40,
            placeholder_text="Type or paste your password…",
        )
        self._entry.pack(side="left", fill="x", expand=True)

        self._toggle_btn = ctk.CTkButton(
            entry_frame,
            text="Show",
            width=64,
            height=40,
            command=self._toggle_visibility,
            fg_color="#3a3a3a",
            hover_color="#555555",
            font=ctk.CTkFont(family="Segoe UI", size=13),
        )
        self._toggle_btn.pack(side="right", padx=(8, 0))

        # --- Result card ---
        self._result_card = ResultCard(self)
        self._result_card.pack(fill="x", padx=20, pady=(0, 14))

        # --- Rule checklist ---
        ctk.CTkLabel(
            self,
            text="Requirements:",
            font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold"),
            anchor="w",
        ).pack(fill="x", padx=20, pady=(0, 6))

        self._rules_frame = ctk.CTkScrollableFrame(
            self, fg_color="transparent", height=200
        )
        self._rules_frame.pack(fill="both", expand=True, padx=20, pady=(0, 16))

        # Rule row widgets, keyed by rule name
        self._rule_rows: dict[str, ctk.CTkLabel] = {}
        self._build_rule_rows()

        # Start with a neutral blank state — no result shown until user types
        self._result_card.show_empty()

    def _build_rule_rows(self) -> None:
        """Pre-create one label row per visible rule."""
        for name in _DISPLAY_RULES:
            lbl = ctk.CTkLabel(
                self._rules_frame,
                text="",
                font=ctk.CTkFont(family="Segoe UI", size=13),
                anchor="w",
            )
            lbl.pack(fill="x", pady=1)
            self._rule_rows[name] = lbl

    # ------------------------------------------------------------------
    # Event handlers
    # ------------------------------------------------------------------

    def _toggle_mode(self) -> None:
        self._appearance_mode = "light" if self._appearance_mode == "dark" else "dark"
        ctk.set_appearance_mode(self._appearance_mode)
        self._mode_btn.configure(text="☀" if self._appearance_mode == "dark" else "☾")
        # Use contrasting hover and text colors so the icon is visible in both modes
        hover = "#555555" if self._appearance_mode == "dark" else "#CCCCCC"
        text_color = "white" if self._appearance_mode == "dark" else "#333333"
        self._mode_btn.configure(hover_color=hover, text_color=text_color)

    def _toggle_visibility(self) -> None:
        self._show_password = not self._show_password
        self._entry.configure(show="" if self._show_password else "•")
        self._toggle_btn.configure(text="Hide" if self._show_password else "Show")

    def _on_password_change(self, *_) -> None:
        # password is not persisted — retrieved from StringVar for evaluation only
        password = self._password_var.get()
        self._evaluate(password)

    # ------------------------------------------------------------------
    # Evaluation and UI update
    # ------------------------------------------------------------------

    def _evaluate(self, password: str) -> None:
        # password is not persisted
        if not password:
            self._result_card.show_empty()
            self._clear_rule_rows()
            return
        result = check(password, self._policy)
        self._result_card.update_tier(result.tier)
        self._update_rule_rows(result.rules)

    def _clear_rule_rows(self) -> None:
        for lbl in self._rule_rows.values():
            lbl.configure(text="", text_color=_COLOR_NEUTRAL)

    def _update_rule_rows(self, rule_results) -> None:
        # Build a dict for fast lookup
        by_name = {r.name: r for r in rule_results}

        for name, lbl in self._rule_rows.items():
            r = by_name.get(name)
            if r is None:
                lbl.configure(text="", text_color=_COLOR_NEUTRAL)
                continue

            # Hide rules that are not required by policy and aren't hard gates
            if not r.is_hard and r.passed and "not required" in r.message:
                lbl.configure(text="", text_color=_COLOR_NEUTRAL)
                continue

            mark = _CHECK_MARK if r.passed else _CROSS_MARK
            color = _COLOR_PASS if r.passed else _COLOR_FAIL
            lbl.configure(text=f"  {mark}  {r.message}", text_color=color)


def show_error_dialog(message: str) -> None:
    """Display a modal error dialog for policy loading problems."""
    root = ctk.CTk()
    root.withdraw()
    dialog = ctk.CTkToplevel(root)
    dialog.title("Policy Load Warning")
    dialog.geometry("420x200")
    dialog.resizable(False, False)
    dialog.grab_set()

    ctk.CTkLabel(
        dialog,
        text=message,
        wraplength=380,
        font=ctk.CTkFont(family="Segoe UI", size=13),
        justify="left",
    ).pack(padx=20, pady=(20, 10))

    ctk.CTkButton(dialog, text="OK", command=dialog.destroy).pack(pady=(0, 16))
    dialog.wait_window()
    root.destroy()
