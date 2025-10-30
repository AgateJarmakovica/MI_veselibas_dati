#!/usr/bin/env bash
set -e
echo " Setting up healthdq-ai environment..."

# System updates (quiet mode)
sudo apt-get update -y && sudo apt-get upgrade -y

# Optional system packages
if [ -f packages.txt ]; then
  echo " Installing system packages..."
  xargs -a packages.txt sudo apt-get install -y
fi

# Python dependencies
if [ -f requirements.txt ]; then
  echo " Installing Python dependencies..."
  pip install --no-cache-dir -r requirements.txt
fi

# Ensure Streamlit is present
pip install --no-cache-dir streamlit watchdog

echo " Environment setup complete!"
