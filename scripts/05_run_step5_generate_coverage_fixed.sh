#!/usr/bin/env bash
set -euo pipefail

# Fixed version: Use main .venv for pip installs
SCRIPT_DIR="$1"
MAIN_DIR="$2"
repo_name="$3"
STEP_OUT="$MAIN_DIR/claude_outputs/step5_output.json"
PIPELINE_DIR="$MAIN_DIR/.pipeline"
MARKER="$PIPELINE_DIR/05_step5_done"
mkdir -p "$PIPELINE_DIR"

STEP5_PROMPT="$SCRIPT_DIR/prompts/step5_prompt.md"

echo "05: step 5 generating coverage reports -> $STEP_OUT" >&2

if [[ -f "$MARKER" ]]; then
  echo "05: step 5 already done (marker exists)" >&2
  exit 0
fi

# Use main .venv for pip installations
MAIN_VENV="$(dirname "$MAIN_DIR")/.venv"
if [[ ! -d "$MAIN_VENV" ]]; then
  echo "Error: Main venv not found at $MAIN_VENV" >&2
  exit 1
fi

source "$MAIN_VENV/bin/activate"

# Define directories
TOOLS_DIR="$MAIN_DIR/src/tools"
TESTS_DIR="$MAIN_DIR/tests/code"

# Install formatting tools in main venv
echo "05: Installing/verifying black and isort..." >&2
pip install -q black isort pytest pytest-cov coverage pylint || {
  echo "Error: Failed to install tools" >&2
  exit 1
}

# Format code with black and isort before analysis
if [[ -d "$TOOLS_DIR" ]]; then
  mapfile -t PY_FILES < <(find "$TOOLS_DIR" -maxdepth 1 -name "*.py" -type f 2>/dev/null)
  if [[ ${#PY_FILES[@]} -gt 0 ]]; then
    echo "05: Running black on src/tools/*.py..." >&2
    black "${PY_FILES[@]}" 2>&1 | sed 's/^/  /' >&2 || true
    
    echo "05: Running isort on src/tools/*.py..." >&2
    isort "${PY_FILES[@]}" 2>&1 | sed 's/^/  /' >&2 || true
    
    echo "05: Code formatting complete" >&2
  fi
fi

# Create output directories
mkdir -p "$MAIN_DIR/reports/coverage"
mkdir -p "$MAIN_DIR/reports/quality/pylint"

# Run pytest with coverage
if [[ -d "$TESTS_DIR" ]] && [[ -n "$(find "$TESTS_DIR" -name "*_test.py" -type f 2>/dev/null)" ]]; then
  echo "05: Cleaning Python cache files..." >&2
  find "$MAIN_DIR" -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
  find "$MAIN_DIR" -type f -name "*.pyc" -delete 2>/dev/null || true
  
  echo "05: Running pytest with coverage..." >&2
  cd "$MAIN_DIR"
  pytest "$TESTS_DIR" \
    --cache-clear \
    --import-mode=importlib \
    --cov="$TOOLS_DIR" \
    --cov-report=xml:"$MAIN_DIR/reports/coverage/coverage.xml" \
    --cov-report=json:"$MAIN_DIR/reports/coverage/coverage.json" \
    --cov-report=html:"$MAIN_DIR/reports/coverage/htmlcov" \
    --cov-report=term \
    -v > "$MAIN_DIR/reports/coverage/pytest_output.txt" 2>&1 || true
  
  coverage report > "$MAIN_DIR/reports/coverage/coverage_summary.txt" 2>&1 || true
else
  echo "05: Warning: No test files found, skipping coverage analysis" >&2
  touch "$MAIN_DIR/reports/coverage/coverage_summary.txt"
fi

# Run pylint on tool files
if [[ -d "$TOOLS_DIR" ]]; then
  mapfile -t PY_FILES < <(find "$TOOLS_DIR" -maxdepth 1 -name "*.py" -type f 2>/dev/null)
  if [[ ${#PY_FILES[@]} -gt 0 ]]; then
    echo "05: Running pylint on src/tools/*.py..." >&2
    cd "$MAIN_DIR"
    
    pylint "${PY_FILES[@]}" \
      --output-format=text \
      --reports=yes \
      --score=yes \
      > "$MAIN_DIR/reports/quality/pylint/pylint_report.txt" 2>&1 || true
    
    grep "Your code has been rated" "$MAIN_DIR/reports/quality/pylint/pylint_report.txt" \
      > "$MAIN_DIR/reports/quality/pylint/pylint_scores.txt" 2>&1 || true
  fi
fi

echo "05: Coverage and pylint analysis complete, generating reports..." >&2

# Export repo_name for envsubst
export github_repo_name="$repo_name"

# Run Claude agent
envsubst < "$STEP5_PROMPT" | claude --model claude-sonnet-4-20250514 \
  --verbose --output-format stream-json \
  --dangerously-skip-permissions -p - > "$STEP_OUT"

touch "$MARKER"
