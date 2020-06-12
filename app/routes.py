import json
from flask import render_template, flash, redirect, url_for, request
from app import app, Config, db
from flask_login import current_user, login_user
from app.models import User
import requests


@app.route('/')
@app.route('/index')
def index():
    if current_user.is_authenticated:
        return (
            "<p>Hello, {}! You're logged in! Email: {}</p>"
            "<div><p>Google Profile Picture:</p>"
            '<img src="{}" alt="Google profile pic"></img></div>'
            '<a class="button" href="/logout">Logout</a>'.format(
                current_user.name, current_user.email, current_user.profile_pic
            )
        )
    else:
        return '<a class="button" href="/login">Google Login</a>'


def get_google_provider_cfg():
    return requests.get(Config.GOOGLE_DISCOVERY_URL).json()


@app.route('/login', methods=['GET', 'POST'])
def login():
    # Find URL for Google Login
    google_provider_cfg = get_google_provider_cfg()
    authorization_endpoint = google_provider_cfg["authorization_endpoint"]

    # Use library to construct the request for Google login and provide
    # scopes that let you retrieve user's profile (and hopefully Calendar) from Google
    request_uri = User.client.prepare_request_uri(
        authorization_endpoint,
        redirect_uri=f'{request.base_url}/callback',
        scope=["openid", "email", "profile", "https://www.googleapis.com/auth/calendar.events"]
    )

    return redirect(request_uri)


@app.route("/login/callback")
def callback():
    # Get authorization code Google sent back to you
    code = request.args.get("code")

    # Find out what URL to hit to get tokens that allow you to ask for
    # things on behalf of a user
    google_provider_cfg = get_google_provider_cfg()
    token_endpoint = google_provider_cfg["token_endpoint"]

    token_url, headers, body = User.client.prepare_token_request(
        token_endpoint,
        authorization_response=request.url,
        redirect_url=request.base_url,
        code=code
    )

    token_response = requests.post(
        token_url,
        headers=headers,
        data=body,
        auth=(Config.GOOGLE_CLIENT_ID, Config.GOOGLE_CLIENT_SECRET)
    )

    User.client.parse_request_body_response(json.dumps(token_response.json()))

    # Now that you have tokens let's find and hit the URL
    # from Google that gives you the user's profile information,
    # including their Google profile image and email
    userinfo_endpoint = google_provider_cfg["userinfo_endpoint"]
    uri, headers, body = User.client.add_token(userinfo_endpoint)
    userinfo_response = requests.get(uri, headers=headers, data=body)

    # You want to make sure their email is verified.
    # The user authenticated with Google, authorized your
    # app, and now you've verified their email through Google!
    if userinfo_response.json().get("email_verified"):
        unique_id = userinfo_response.json()["sub"]
        users_email = userinfo_response.json()["email"]
        picture = userinfo_response.json()["picture"]
        users_name = userinfo_response.json()["given_name"]
    else:
        return "User email not available or not verified by Google.", 400

    # Create User in db with info from Google
    user = User(id=unique_id, name=users_name, email=users_email, profile_pic=picture)

    # Doesn't exist? Add to db
    if not User.query.filter_by(id=user.id).first():
        db.session.add(user)
        db.session.commit()

    # Log user in, begin session
    login_user(user)

    return redirect(url_for("index"))

    @app.route("/logout")
    @login_required
    def logout():
        logout_user()
        return redirect(url_for("index"))
