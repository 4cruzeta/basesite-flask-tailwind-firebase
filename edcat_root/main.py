
import os
import sys

# This is a crucial step to ensure the application can be run as a script.
# It adds the parent directory (the project root) to Python's path,
# allowing it to find the 'edcat_root' package.
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from edcat_root import create_app

# Create the Flask app using the application factory
app = create_app()

# --- Main Execution ---
if __name__ == '__main__':
    # The PORT environment variable is set by Cloud Run and other hosting environments.
    # Default to 8080 for local development.
    port = int(os.environ.get('PORT', 8080))
    
    # When running locally, debug=True is fine. 
    # For production (like Cloud Run), a proper WSGI server like Gunicorn is used,
    # and debug mode should be disabled for security and performance.
    app.run(debug=True, host='0.0.0.0', port=port)
