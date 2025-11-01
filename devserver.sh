#!/bin/bash

# Activate the virtual environment
source .venv/bin/activate

# Run Tailwind in watch mode in the background
echo "Starting Tailwind CSS in watch mode..."
npx tailwindcss -i edcat_root/static/css/input.css -o edcat_root/static/css/output.css --watch &

# Start the Flask server
echo "Starting Flask server..."
python -m edcat_root.main
