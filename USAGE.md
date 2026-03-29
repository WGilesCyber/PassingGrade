# PassingGrade — User Guide

---

## Part 1: For End Users

### What is PassingGrade?

PassingGrade is a tool that checks whether a password meets your organization's security requirements. Type a password and it instantly tells you whether it passes — and exactly which requirements it meets or misses. The tool runs entirely on your computer and never sends your password anywhere. It is safe to use with real passwords.

---

### Getting Started

1. Open **PassingGrade.exe** by double-clicking it (or double-click **PassingGrade.vbs** if running from source).
2. The window opens immediately. No installation, no login required.
3. You will see the password entry field at the top of the window.

The name of your organization's password policy is shown in the top-right corner of the window (for example, "My Org Password Policy").

---

### Using the App

**Step 1 — Enter your password**

Click inside the password field and type or paste your password. The dots (•) are normal — they keep your password hidden while you type. The result area will be blank until you begin typing.

**Step 2 — Read the result**

As you type, the colored banner below the password field updates instantly. It shows one of four ratings (see the next section). Clear the field and the banner resets to blank.

**Step 3 — Check the requirements list**

Below the banner is a list of requirements. Each one shows a checkmark (✓) if your password passes that requirement, or an X (✗) if it does not.

**Step 4 — Use Show / Hide if needed**

Click the **Show** button next to the password field to reveal what you typed, in case you want to verify it. Click **Hide** to mask it again.

**Step 5 — Switch between light and dark mode**

Click the **☀** button in the top-right area of the window to switch to light mode. Click **🌙** to switch back to dark mode.

You do not need to click any submit button — the result updates automatically with every character you type.

---

### Understanding Your Result

| Result | Color | What it means |
|---|---|---|
| **Great** | Dark green | Your password exceeds all requirements. It is strong and will be accepted. |
| **Good** | Dark blue | Your password meets all requirements. It will be accepted. |
| **Ok** | Amber/orange | Your password just meets the minimum requirements. It will be accepted, but consider making it stronger. |
| **Not Compliant** | Dark red | Your password does not meet one or more requirements. It will not be accepted. Check the list below to see what needs to be fixed. |

If your result is **Not Compliant**, look at the requirements list for any items marked with ✗ — those are the specific things you need to fix.

---

### The Requirements Checklist

Each row in the requirements list corresponds to one rule from your organization's policy.

- **✓ (green)** — Your password passes this requirement.
- **✗ (red)** — Your password fails this requirement. Fix this to improve your result.

### Common requirements explained

| Requirement | What it means |
|---|---|
| At least N characters | Your password must be at least that many characters long. |
| No more than N characters | Your password cannot exceed the maximum length. |
| Contains an uppercase letter | At least one capital letter (A–Z) must be included. |
| Contains a lowercase letter | At least one small letter (a–z) must be included. |
| Contains a number | At least one digit (0–9) must be included. |
| Contains a special character | At least one symbol such as !, @, #, $, % must be included. |
| No character repeated more than N times in a row | You cannot use the same character back-to-back too many times (for example, "aaaa" would fail if the limit is 3). |
| Not a commonly used password | Your password cannot be one of the widely known weak passwords such as "password123" or "letmein". |
| No predictable sequences | Your password cannot contain runs like "abcd", "1234", or "qwerty". |
| Does not contain spaces | Spaces are not allowed (only if your organization requires this). |

---

### Privacy & Security

PassingGrade is designed so that your password never leaves your device.

- **Your password is never saved to disk.** It exists only in the app's memory while the window is open.
- **Your password is never logged.** No file, event log, or debug trace captures what you type.
- **The tool makes no network connections.** It works completely offline. Nothing is sent to any server, cloud service, or website.
- **When you close the window, your password is gone.** There is no history, no cache, no way to recover it afterward.
- **Pasting a password is safe.** If you paste from your clipboard, the tool only receives the text — it does not access, read, or clear your clipboard.

---

### Common Questions

**Can I paste my password instead of typing it?**
Yes. Click inside the password field and paste normally (Ctrl+V). The result updates immediately.

**Does this tool send my password to anyone?**
No. PassingGrade has no internet connection and no telemetry of any kind. It checks your password locally, on your own computer only.

**Why does the result area start blank?**
The tool only shows a result once you begin typing. This avoids showing a misleading "Not Compliant" before you have entered anything. Clear the field and the result resets to blank.

**My password looks complex, but it still says Not Compliant. Why?**
The most common reasons are:
- The password is on the list of commonly known weak passwords (even complex-looking ones sometimes appear on these lists).
- The password contains a predictable sequence — for example, "P@ssword123" contains "assword" and "123" which are recognizable patterns.
- One of the required character types is missing.

Check the ✗ items in the requirements list for the specific reason.

**How do I know what my organization requires?**
The requirements list in the app shows exactly what your organization's policy requires. The policy name is displayed in the top-right corner of the window.

**Is it safe to check my actual password with this tool?**
Yes. The tool is offline, stores nothing, and logs nothing. However, as a general security habit, it is still good practice to use a similar-but-not-identical password for testing, then make your real password based on what you learn.

---

### Error Messages

**"Policy Load Warning" dialog**

This dialog appears if there is a problem reading your organization's policy file. It will show:
- The file path that could not be loaded
- A description of the error
- A note that the built-in default policy is being used instead

Click **OK** to dismiss it. The tool will open normally using default rules. If this message appears every time you launch the app, let your IT department know.

---
---

## Part 2: For Administrators

This section covers deploying PassingGrade to your organization and configuring the password policy that end users are checked against.

---

### Deploying the Application

**Standalone executable (recommended)**

Build or obtain `PassingGrade.exe`. Distribute it to users along with:

- `policy\policy.json` — your organization's custom policy file (see below); if omitted, built-in defaults are used

Users do not need Python, .NET, or any other runtime. The `.exe` is fully self-contained. Double-click it to launch — no console window, no installer.

**Running from Python source (developer / IT use)**

```bash
pip install -r requirements.txt
python main.py
```

Or double-click `PassingGrade.vbs` — launches silently with no console window.

**Loading a policy at a specific path**

```
PassingGrade.exe --policy "C:\Policies\company_policy.json"
python main.py --policy "C:\Policies\company_policy.json"
```

---

### Policy File Location

The tool searches for `policy/policy.json` in this priority order:

1. Path given with the `--policy` flag on the command line
2. `policy\policy.json` in the same folder as `PassingGrade.exe`
3. `policy\policy.json` in the current working directory
4. Built-in NIST-aligned defaults (used silently if no file is found)

**Recommended deployment layout:**
```
PassingGrade.exe
policy\
    policy.json        ← your organization's rules go here
```

No recompilation is required to change the policy. Edit `policy.json` and re-distribute or update in place.

---

### Policy File Reference

Create `policy/policy.json` using this structure:

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

#### Rules fields

| Field | Type | Description |
|---|---|---|
| `policy_name` | string | Displayed in the app header so users know which policy is active |
| `min_length` | integer (1–1000) | Minimum number of characters required |
| `max_length` | integer (≥ min_length, ≤ 10000) | Maximum number of characters allowed |
| `require_uppercase` | true/false | Require at least one uppercase letter (A–Z) |
| `require_lowercase` | true/false | Require at least one lowercase letter (a–z) |
| `require_digit` | true/false | Require at least one digit (0–9) |
| `require_special` | true/false | Require at least one character from `special_chars` |
| `special_chars` | string (non-empty) | The set of characters that count as "special" |
| `disallow_spaces` | true/false | Block passwords that contain spaces |
| `max_repeated_chars` | integer (1–100) | Max allowed consecutive identical characters (e.g. `3` blocks `aaaa`) |
| `disallow_common` | true/false | Block passwords found on the built-in common-password list |
| `disallow_sequences` | true/false | Block predictable character runs (abc, 123, qwerty, etc.) |
| `min_sequence_length` | integer (2–20) | How many characters in a row constitute a "sequence" |
| `min_unique_chars` | integer (0–128) | Minimum number of distinct characters (soft rule — affects score tier only) |

#### Scoring fields

Scoring controls which passing passwords are rated **Great**, **Good**, or **Ok**. All failing passwords are always **Not Compliant** regardless of score.

| Field | Description |
|---|---|
| `length_bonus_per_char_over_min` | Points added per character beyond the minimum length |
| `max_length_bonus` | Cap on length bonus points |
| `all_complexity_bonus` | Bonus points when all four complexity classes are present |
| `unique_chars_bonus_per_char` | Points per unique character beyond `min_unique_chars` |
| `max_unique_chars_bonus` | Cap on unique character bonus points |

**Tier thresholds (not configurable):** Great = 90+, Good = 70–89, Ok = 50–69.

---

### Hard Rules vs. Soft Rules

**Hard rules** (any failure → Not Compliant):
`min_length`, `max_length`, `require_uppercase`, `require_lowercase`, `require_digit`, `require_special`, `disallow_spaces`, `max_repeated_chars`, `disallow_common`, `disallow_sequences`

**Soft rules** (affect score tier only, never block):
`min_unique_chars`

Setting a hard rule's flag to `false` disables that check entirely — the requirement will not appear in the user's checklist.

---

### What Happens if the Policy File is Invalid

If `policy.json` contains a JSON syntax error or an invalid field value (wrong type, out-of-bounds number, empty string where one isn't allowed), the tool will:

1. Show a **"Policy Load Warning"** dialog describing the exact problem and the file path
2. Fall back to the built-in default policy
3. Open normally — users can still check passwords

The dialog tells users to contact IT if it keeps appearing. Validate your `policy.json` before distributing by running the app once and checking for the warning.

**Common validation errors and fixes:**

| Error | Fix |
|---|---|
| `'min_length' must be an integer` | Remove quotes — use `12`, not `"12"` |
| `'min_length' must not be greater than 'max_length'` | Ensure `min_length < max_length` |
| `'require_uppercase' must be true or false` | Use `true`/`false` (no quotes), not `"yes"` |
| `'special_chars' must not be empty` | Provide at least one special character |
| `'min_sequence_length' must be between 2 and 20` | Use a value in that range |

---

### Building the Standalone Executable

Requires Python 3.11+ and pip on the build machine only. End users need nothing.

```powershell
pip install -r requirements.txt
powershell -ExecutionPolicy Bypass -File build/build_windows.ps1
```
Output: `dist/PassingGrade.exe`

The build uses `PassingGrade.spec` (committed to the repository) to ensure a consistent, reproducible output. The `policy/policy.json` and `assets/common_passwords.txt` files are bundled into the executable automatically.
