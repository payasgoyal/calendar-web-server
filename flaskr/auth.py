import functools
import pathlib
import os
import requests
from sqlite3 import IntegrityError
from flask_cors import CORS
from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for, abort, jsonify
)
from werkzeug.security import check_password_hash, generate_password_hash

from google.oauth2 import id_token
from google_auth_oauthlib.flow import Flow
from pip._vendor import cachecontrol
import google.auth.transport.requests

import hashlib
from dotenv.main import load_dotenv

from flaskr.db import get_db

load_dotenv(dotenv_path='../.env')

#initiating blueprint instance
bp = Blueprint('auth', __name__, url_prefix='/auth')

GOOGLE_CLIENT_ID = os.getenv('GOOGLE_CLIENT_ID')
GOOGLE_CLIENT_SECRET = os.getenv('GOOGLE_CLIENT_SECRET')
GOOGLE_PROJECT_ID = os.getenv('GOOGLE_PROJECT_ID')
REDIRECT_URI = os.getenv('REDIRECT_URI')

flow = Flow.from_client_config(
     client_config={
        "web": {
            "client_id": GOOGLE_CLIENT_ID,
            "client_secret": GOOGLE_CLIENT_SECRET,
            "project_id": GOOGLE_PROJECT_ID,
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
            "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
        }
    },
    scopes=["https://www.googleapis.com/auth/userinfo.profile", "https://www.googleapis.com/auth/userinfo.email", "openid"],
    redirect_uri="http:127.0.0.1:5000/auth/callback"
)

@bp.route('/google', methods=('GET', 'POST'))
def googleLogin():
    authorization_url, state = flow.authorization_url()
    session['state'] = state
    return redirect(authorization_url)


@bp.before_app_request
def load_logged_in_user():
    user_id = session.get('user_id')

    if user_id is None:
        g.user = None
    else:
        g.user = get_db().execute(
            'SELECT * FROM user WHERE id = ?', (user_id,)
        ).fetchone()


# decorator
def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for('auth.login'))

        return view(**kwargs)

    return wrapped_view

@bp.route('/register', methods=('GET', 'POST'))
def register():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        db = get_db()
        error = None

        if not name:
            error = 'Name is required.'
        elif not email:
            error = 'Email is required.'
        elif not password:
            error = 'Password is required.'
        elif db.execute('SELECT id FROM user WHERE email = ?', (email,)).fetchone() is not None:
            error = 'Email {} is already in use.'.format(email)

        if error is None:
            try:
                db.execute(
                    'INSERT INTO user (name, password, email, provider) VALUES (?, ?, ?, ?)',
                    (name, generate_password_hash(password), email, 'direct_register')
                )
                db.commit() # save the changes 
                return redirect(url_for('auth.login'))
            except IntegrityError:
                error = f"Email {email} is already in use."
            finally:
                db.rollback()

        flash(error)

    return render_template('auth/register.html')

@bp.route('/login', methods=('GET', 'POST'))
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        db = get_db()
        error = None
        user = db.execute(
            'SELECT * FROM user WHERE email = ?', (email,)
        ).fetchone()

        if user is None:
            error = 'Incorrect email/password'
        elif not check_password_hash(user['password'], password):
            error = 'Incorrect email/password.'

        if error is None:
            session.clear()
            session['user_id'] = user['id']
            return redirect(url_for('calendar_helper.show_cal'))

        flash(error)

    return render_template('auth/login.html')

@bp.route("/callback")
def callback():
    flow.fetch_token(authorization_response=request.url)

    if not session["state"] == request.args["state"]:
        abort(500)  # State does not match!

    credentials = flow.credentials
    request_session = requests.session()
    cached_session = cachecontrol.CacheControl(request_session)
    token_request = google.auth.transport.requests.Request(session=cached_session)

    id_info = id_token.verify_oauth2_token(
        id_token=credentials._id_token,
        request=token_request,
        audience=GOOGLE_CLIENT_ID
    )

    email = id_info.get("email")
    name = id_info.get("name")
    google_id = id_info.get('sub')
    google_id = id_info.get('sub')

    db = get_db()
    cursor = db.cursor()

    user = cursor.execute('SELECT * FROM user WHERE email = ? OR google_id = ?', (email, google_id)).fetchone()

    if user is None:
        # Insert new user with NULL password for OAuth users
        cursor.execute("INSERT INTO user (name, email, google_id, provider) VALUES (?,?,?,?)", (name, email, google_id, 'google' ))
        db.commit()
        user_id = cursor.lastrowid

    else:
        user_id = user[0]


    session["google_id"] = id_info.get("sub")
    session["name"] = id_info.get("name")
    session['email'] = id_info.get("email")
    session['user_id'] = user_id
    return redirect("/cal")

@bp.route("/logout")
def logout():
    session.clear()
    return redirect(url_for('auth.login'))