"""
Helper script to set up Google OAuth credentials.
Run this script after getting your credentials from Google Cloud Console.
"""
import os
from pathlib import Path
from dotenv import load_dotenv

def setup_oauth_credentials():
    """Set up Google OAuth credentials interactively"""
    print("\n=== Google OAuth2 Setup ===\n")
    print("Before continuing, make sure you have:")
    print("1. Created a project in Google Cloud Console")
    print("2. Enabled Google+ API")
    print("3. Created OAuth 2.0 credentials")
    print("4. Added these authorized redirect URIs:")
    print("   - http://localhost:8000/api/social/complete/")
    print("   - http://localhost:8000/complete/google-oauth2/")
    print("   - https://localhost:8000/api/social/complete/")
    print("   - https://localhost:8000/complete/google-oauth2/\n")

    client_id = input("Enter your Google OAuth2 Client ID: ").strip()
    client_secret = input("Enter your Google OAuth2 Client Secret: ").strip()

    # Load existing .env file or create new one
    env_path = Path('.env')
    if env_path.exists():
        load_dotenv()
        existing_vars = {}
        with open(env_path) as f:
            for line in f:
                if '=' in line:
                    key, value = line.strip().split('=', 1)
                    existing_vars[key] = value
    else:
        existing_vars = {}

    # Update with new OAuth credentials
    existing_vars['GOOGLE_OAUTH2_KEY'] = client_id
    existing_vars['GOOGLE_OAUTH2_SECRET'] = client_secret

    # Ensure other required variables exist
    if 'DJANGO_SECRET_KEY' not in existing_vars:
        import secrets
        existing_vars['DJANGO_SECRET_KEY'] = secrets.token_urlsafe(50)
    
    if 'DEBUG' not in existing_vars:
        existing_vars['DEBUG'] = 'True'

    # Write to .env file
    with open(env_path, 'w') as f:
        for key, value in existing_vars.items():
            f.write(f"{key}={value}\n")

    print("\nCredentials have been saved to .env file")
    print("\nNext steps:")
    print("1. Run migrations: python manage.py migrate")
    print("2. Start the server: python manage.py runserver_plus --cert-file cert.pem --key-file key.pem")
    print("3. Visit https://localhost:8000/login/ to test Google OAuth login")

if __name__ == '__main__':
    setup_oauth_credentials()
