"""
Result card widget — colored tier badge shown above the rule checklist.
"""
from __future__ import annotations

import customtkinter as ctk

from passinggrade.checker import TIER_COLORS, TIER_LABELS, TIER_DESCRIPTIONS, TIER_NOT_COMPLIANT


class ResultCard(ctk.CTkFrame):
    """Displays the compliance tier as a colored banner with a short description."""

    _EMPTY_COLOR = "#3a3a3a"

    def __init__(self, master: ctk.CTk | ctk.CTkFrame, **kwargs):
        super().__init__(master, corner_radius=10, **kwargs)

        self._tier_label = ctk.CTkLabel(
            self,
            text="",
            font=ctk.CTkFont(size=22, weight="bold"),
            text_color="#FFFFFF",
        )
        self._tier_label.pack(pady=(14, 2), padx=20)

        self._desc_label = ctk.CTkLabel(
            self,
            text="",
            font=ctk.CTkFont(size=13),
            text_color="#FFFFFF",
            wraplength=380,
        )
        self._desc_label.pack(pady=(0, 14), padx=20)

        self.show_empty()

    def show_empty(self) -> None:
        """Reset to a neutral state — shown before the user types anything."""
        self.configure(fg_color=self._EMPTY_COLOR)
        self._tier_label.configure(text="")
        self._desc_label.configure(text="Enter a password above to check compliance")

    def update_tier(self, tier: str) -> None:
        # Colors, labels, and descriptions all come from the TIER_* dicts in checker.py
        # so the card always stays in sync with the scoring logic
        color = TIER_COLORS[tier]
        self.configure(fg_color=color)
        self._tier_label.configure(text=TIER_LABELS[tier])
        self._desc_label.configure(text=TIER_DESCRIPTIONS[tier])
