# PassingGrade
Offline, zero-install password compliance checker for organizations. Windows only.

---

## What it does
Users enter their password and immediately see whether it meets their organization's policy, rated as:

| Rating | Meaning |
|---|---|
| **Great** | Exceeds all requirements |
| **Good** | Meets all requirements |
| **Ok** | Meets the minimum requirements |
| **Not Compliant** | Does not meet the requirements |

A per-rule checklist shows exactly which requirements pass or fail in real time. The result area is blank on launch and only updates once the user starts typing. The window is resizable and includes a light/dark mode toggle.

See [USAGE.md](USAGE.md) for the full end-user and administrator guide.

---

## Privacy guarantee
**No passwords are ever saved, logged, or transmitted.**

- Passwords exist only in memory while the window is open.
- The tool makes no network connections of any kind.
- When you close the window, the password is gone.
- The source code is auditable — look for `# password is not persisted` comments throughout.

---

## Running from source

**Requirements:** Python 3.11+

```bash
pip install -r requirements.txt
python main.py
```

Or double-click **`PassingGrade.vbs`** — silent launcher, no console window.

To use a custom policy file:
```bash
python main.py --policy C:\path\to\your\policy.json
```

---

## Building a standalone executable (no Python required)

```powershell
pip install -r requirements.txt
powershell -ExecutionPolicy Bypass -File build/build_windows.ps1
```
Output: `dist/PassingGrade.exe` — double-click to run, no install needed.

---

## Configuring the password policy

Admins can customize the policy by placing a `policy/policy.json` file next to the executable. No recompilation needed.

**Config search order:**
1. `--policy <path>` flag (command line)
2. `policy\policy.json` next to the executable
3. `policy\policy.json` in the current working directory
4. Built-in NIST-aligned defaults (if no file is found)

**Example `policy/policy.json`:**
```json
{
  "policy_name": "My Org Password Policy",
  "rules": {
    "min_length": 12,
    "max_length": 128,
    "require_uppercase": true,
    "require_lowercase": true,
    "require_digit": true,
    "require_special": true,
    "special_chars": "!@#$%^&*()_+-=[]{}|;':\",./<>?",
    "disallow_spaces": false,
    "min_unique_chars": 8,
    "max_repeated_chars": 3,
    "disallow_common": true,
    "disallow_sequences": true,
    "min_sequence_length": 4
  },
  "scoring": {
    "length_bonus_per_char_over_min": 2,
    "max_length_bonus": 20,
    "all_complexity_bonus": 10,
    "unique_chars_bonus_per_char": 1,
    "max_unique_chars_bonus": 10
  }
}
```

| Field | Description |
|---|---|
| `min_length` / `max_length` | Character length bounds |
| `require_uppercase/lowercase/digit/special` | Toggle each complexity class on/off |
| `special_chars` | The set of characters that count as "special" |
| `disallow_spaces` | Block passwords containing spaces |
| `max_repeated_chars` | Max consecutive identical characters (e.g. `3` blocks `aaaa`) |
| `disallow_common` | Block passwords on the built-in common-password list |
| `disallow_sequences` | Block predictable runs (abc, 123, qwerty…) |
| `min_sequence_length` | How long a sequence must be to trigger the block |
| `scoring.*` | Controls point bonuses that differentiate Great/Good/Ok |

---

## Running tests

```bash
pip install -r requirements-dev.txt
pytest tests/
```

---

## Project structure

```
PassingGrade/
├── main.py                    # Entry point
├── PassingGrade.vbs           # Silent double-click launcher (no console window)
├── PassingGrade.spec          # PyInstaller build spec
├── passinggrade/
│   ├── checker.py             # check() — core evaluator
│   ├── rules.py               # Individual rule functions (pure, no side effects)
│   ├── config.py              # Policy loader + validation
│   └── ui/
│       ├── app.py             # Main window (resizable, light/dark toggle)
│       └── result_card.py     # Tier badge widget
├── policy/
│   └── policy.json            # Admin-editable policy (shipped with exe)
├── assets/
│   └── common_passwords.txt   # Bundled common-password list
├── tests/
│   ├── test_checker.py
│   └── test_config.py
└── build/
    └── build_windows.ps1
```

---

## License
MIT — Copyright 2026 WGilesCyber
