# Secure Web Application - Assignment 4

## Overview
This project implements a secure web application that allows users to authenticate using Microsoft Entra ID (Azure Active Directory) and interact with Microsoft Graph APIs. Users can securely log in, view their profile, edit non-sensitive fields (such as phone numbers), and browse a list of users from the directory.

The application is built with Flask and deployed on an Ubuntu virtual machine with HTTPS enabled via a Let's Encrypt TLS certificate.

## Requirements
- Python 3.10+ (Recommended version: Python 3.10 or higher).  
  You can download Python from [here](https://www.python.org/downloads/).

You can check your version using:
`py --version`

## Libraries
The application requires the following Python libraries:
- Flask
- requests
- msal
- python-dotenv

They are listed in requirements.txt.
To install them, run:
`pip install -r requirements.txt`


## Project Structure
```
src/                  # Contains all source code (Flask application)
│
├── templates/         # HTML templates (index.html, profile.html, users.html, etc.)
├── static/            # Static files (CSS)
├── .env               # Environment variables (client ID, tenant ID, secret key, etc.)
├── app.py             # Main Flask application
├── requirements.txt   # Python dependencies
```

## Usage Instructions
### Local Development 
To run the application locally:

- Open a terminal
- Navigate into the project folder:
`cd src/`

- Set the Flask app environment variable:
`$env:FLASK_APP="app.py"`

- Run Flask using:
`py -m flask run`

- Open your browser and go to:
`http://127.0.0.1:8000`

### Important: Make sure your .env file is present and contains valid Azure credentials.

## Important Notes

### Environment File:
The .env file is critical and contains secrets like:
- CLIENT_ID
- CLIENT_SECRET
- TENANT_ID
- SECRET_KEY

### Microsoft Graph API Scopes:
The app uses:
- User.Read
- User.ReadWrite
- User.ReadBasic.All It does not explicitly request openid, profile, or email scopes because MSAL automatically handles the basic OpenID needs.

### Limitations:
When editing the profile, fields like givenName, surname, and userPrincipalName (user ID) cannot be modified by regular users. This restriction comes from Microsoft Graph API permissions and policies.
