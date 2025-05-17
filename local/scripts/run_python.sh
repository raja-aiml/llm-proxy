#!/usr/bin/env bash
set -euo pipefail

# --- Configuration ---
export DISABLE_TELEMETRY="${DISABLE_TELEMETRY:-true}"

# --- Functions ---

# Returns the Git project root directory
function get_project_root() {
  git rev-parse --show-toplevel
}

# Changes to the root of the Git project, exits on failure
function change_to_project_root() {
  local root
  root=$(get_project_root)
  cd "$root" || {
    echo "❌ Failed to change to project root: $root"
    exit 1
  }
}

# Creates a virtual environment and installs dependencies using `uv` if not already created
function create_virtualenv_if_missing() {
  if [ ! -f .venv/bin/activate ]; then
    echo "⚙️  .venv not found — creating and syncing dependencies..."
    uv venv
    uv sync
  fi
}

# Activates the virtual environment in `.venv`
function activate_virtualenv() {
  # shellcheck disable=SC1091
  source .venv/bin/activate
}

# Ensures `pytest-cov` is installed, installs it if missing
function ensure_pytest_cov_installed() {
  if ! pytest --help | grep -q -- "--cov"; then
    echo "📦 pytest-cov plugin not found — installing..."
    source .venv/bin/activate || { echo "❌ Failed to activate virtualenv"; exit 1; }
    ./local/.venv/bin/pip install --upgrade pip
    ./local/.venv/bin/pip install pytest-cov
    ./local/.venv/bin/pip install --upgrade pytest-cov
    ./local/.venv/bin/pip install --upgrade pytest
    ./local/.venv/bin/pip install --upgrade pytest-asyncio
    ./local/.venv/bin/pip install --upgrade pytest-timeout
  else
    echo "✅ pytest-cov plugin is available"
  fi
}


# Executes the command passed to the script
function run_command() {
  exec "$@"
}

# Main orchestrator function for running the script logic
function main() {
  change_to_project_root
  create_virtualenv_if_missing
  activate_virtualenv
  ensure_pytest_cov_installed
  run_command "$@"
}

# Ensure the src/ directory is on PYTHONPATH so "llm_wrapper" can be imported
export PYTHONPATH="$(git rev-parse --show-toplevel)/src:${PYTHONPATH:-}"

# --- Script Entry Point ---
main "$@"