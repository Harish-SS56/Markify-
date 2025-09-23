from app import app

# This is required for Vercel deployment
application = app

if __name__ == "__main__":
    app.run()
