import requests
from flask import Flask, redirect, session, request, url_for, render_template
import msal
from functools import wraps
import os
from dotenv import load_dotenv


# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')

# Configuration parameters for Azure AD authentication
CLIENT_ID = os.environ.get('CLIENT_ID')
CLIENT_SECRET = os.environ.get('CLIENT_SECRET')
TENANT_ID = os.environ.get('TENANT_ID')

AUTHORITY = f"https://login.microsoftonline.com/{TENANT_ID}"
REDIRECT_PATH = "/getAToken" 
REDIRECT_URI = f"https://caker1170.x310.net{REDIRECT_PATH}" 
# Update as needed for local testing : REDIRECT_URI = f"http://localhost:5000{REDIRECT_PATH}" 

# Required scopes for Microsoft Graph API
SCOPE = ["User.Read", "User.ReadWrite", "User.ReadBasic.All"]

def _build_msal_app(cache=None):
    """
    Create a confidential client application instance for MSAL.

    Parameters:
    cache (SerializableTokenCache, optional): Token cache object.

    Returns:
    msal.ConfidentialClientApplication: Configured MSAL app.
    """
    return msal.ConfidentialClientApplication(
        CLIENT_ID, authority=AUTHORITY,
        client_credential=CLIENT_SECRET, token_cache=cache
    )


def login_required(f):
    """
    Decorator to require login for routes.
    Redirects to auth error page if user is not in session.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "user" not in session:
            return redirect(url_for("auth_error"))
        return f(*args, **kwargs)
    return decorated_function

@app.route("/")
def index():
    """
    Homepage route. Displays user info if logged in.
    """
    if "user" in session:
        return render_template("index.html", user=session["user"])
    else:
        return render_template("index.html", user=None)


@app.route("/login")
def login():
    """
    Initiates the login process via Microsoft identity platform.
    Redirects to Microsoft login page.
    """
    auth_url = _build_msal_app().get_authorization_request_url(
        scopes=SCOPE,
        redirect_uri=REDIRECT_URI
    )
    return redirect(auth_url)

@app.route("/getAToken")
def authorized():
    """
    Handles the redirect from Microsoft after authentication.
    Acquires token and saves user info in session.
    """
    if "error" in request.args:
        return f"Error: {request.args['error']}"

    if "code" not in request.args:
        return redirect(url_for("index"))

    code = request.args["code"]

    result = _build_msal_app().acquire_token_by_authorization_code(
        code,
        scopes=SCOPE,
        redirect_uri=REDIRECT_URI
    )

    if "error" in result:
        return f"Error: {result.get('error_description')}"

    # Save user claims and access token in session
    session["user"] = result.get("id_token_claims")
    session["access_token"] = result.get("access_token")

    return redirect(url_for("index"))


@app.route("/logout")
def logout():
    """
    Logs out the user by clearing the session and redirecting to Microsoft logout.
    """
    session.clear()
    return redirect(
        f"https://login.microsoftonline.com/common/oauth2/v2.0/logout"
        f"?post_logout_redirect_uri=https://caker1170.x310.net/"
    )


@app.route("/users")
@login_required
def users():
    """
    Fetches a list of users from Microsoft Graph API.
    Returns a HTML page with user data or error message.
    """
    if "user" not in session or "access_token" not in session:
        return redirect(url_for("index"))

    access_token = session["access_token"]

    # Call Microsoft Graph API to retrieve users
    graph_response = requests.get(
        'https://graph.microsoft.com/v1.0/users',
        headers={'Authorization': f'Bearer {access_token}'}
    )

    if graph_response.status_code != 200:
        return f"Error calling Graph API: {graph_response.text}"

    users = graph_response.json().get('value', [])

    return render_template("users.html", users=users)


@app.route("/edit_profile", methods=["GET", "POST"])
@login_required
def edit_profile():
    """
    Displays and allows editing of the current user's profile.
    On POST, updates user's mobile and business phone numbers via Microsoft Graph.
    """
    if "user" not in session or "access_token" not in session:
        return redirect(url_for("auth_error"))

    access_token = session["access_token"]
    result = None

    if request.method == "POST":
        # Get updated values from form
        new_phone = request.form.get("mobilePhone")
        new_business_phone = request.form.get("businessPhones")

        patch_data = {}
        if new_phone:
            patch_data["mobilePhone"] = new_phone
        if new_business_phone:
            patch_data["businessPhones"] = [new_business_phone]

        # Send PATCH request to update user profile
        if patch_data:  # Only send if there is something to patch
            patch_response = requests.patch(
                "https://graph.microsoft.com/v1.0/me",
                headers={
                    "Authorization": f"Bearer {access_token}",
                    "Content-Type": "application/json"
                },
                json=patch_data
            )
            result = patch_response

    # Always re-fetch the profile to update the form
    graph_response = requests.get(
        "https://graph.microsoft.com/v1.0/me",
        headers={"Authorization": f"Bearer {access_token}"}
    )
    if graph_response.status_code != 200:
        return f"Error fetching profile: {graph_response.text}"
    
    profile = graph_response.json()
    return render_template("profile.html", profile=profile, result=result)


@app.route("/auth_error")
def auth_error():
    """
    Renders the authentication error page.
    """
    return render_template("auth_error.html", result={
        "error": "Authentication Required",
        "error_description": "You must log in to access this page."
    })


if __name__ == "__main__":
    app.run()
