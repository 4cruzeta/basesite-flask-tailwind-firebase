#!/bin/bash

# Activate the virtual environment
source .venv/bin/activate

# CRITICAL: EXPORT PROJECT ID
# This ensures the application knows which GCP project to use for accessing secrets.
export GOOGLE_CLOUD_PROJECT=edcat-site

# The Tailwind CSS watch process is now handled by the onStart hook in .idx/dev.nix
# to avoid redundancy and potential version conflicts.

# Change to the application directory so that Python can find the modules
cd edcat_root

# Start the Flask server
echo "Starting Flask server..."
python main.py
