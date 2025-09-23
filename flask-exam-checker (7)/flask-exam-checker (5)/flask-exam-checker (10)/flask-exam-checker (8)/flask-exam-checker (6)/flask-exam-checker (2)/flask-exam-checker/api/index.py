import sys
import os

# Add the parent directory to the path so we can import app
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app

# This is the entry point for Vercel
def handler(request, context):
    return app

# For Vercel compatibility
application = app

if __name__ == "__main__":
    app.run(debug=False)
