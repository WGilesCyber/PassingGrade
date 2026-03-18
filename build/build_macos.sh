#!/usr/bin/env bash
# PassingGrade — macOS build script
# Produces: dist/PassingGrade (single binary, no terminal window)
#
# Requirements (dev machine only):
#   pip install -r requirements.txt
#
# Usage:
#   cd <repo root>
#   bash build/build_macos.sh

set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

echo "Building PassingGrade for macOS..."

pyinstaller \
    --onefile \
    --windowed \
    --name PassingGrade \
    --add-data "assets/common_passwords.txt:assets" \
    --add-data "policy/policy.json:policy" \
    --clean \
    main.py

echo ""
echo "Build succeeded: dist/PassingGrade"
echo ""
echo "To distribute:"
echo "  Copy dist/PassingGrade to the target machine and make it executable:"
echo "    chmod +x PassingGrade && ./PassingGrade"
echo "  (Optional) Place a customized policy/policy.json next to the binary."
