#!/bin/bash
export PATH="/usr/local/bin:/usr/bin:/bin:$PATH"
cd "$(dirname "$0")"
echo "$(date): deploying..."
python3 predict.py && npx wrangler pages deploy . --project-name wc2026-gto --branch main --commit-dirty=true
echo "$(date): done (exit $?)"
