import time

from authlib.integrations.flask_oauth2 import current_token
from flask import Blueprint, request, redirect, jsonify, render_template
from flask_login import LoginManager, login_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash, gen_salt

from models import Client, User, db
from oauth import auth_server, require_oauth

bp = Blueprint('auth', __name__)

login_manager = LoginManager()
login_manager.login_view = "auth.login"


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)


@bp.route('/init_data', methods=['GET', 'POST'])
def init_data():
    user = User.query.filter_by(email="john@gmail.com").first()
    if not user:
        user = User()
        user.name = "John Doe"
        user.email = "john@gmail.com"
        user.password = generate_password_hash("12345")

        db.session.add(user)
        db.session.commit()

    client = Client.query.filter_by(client_id="client_123").first()
    if not client:
        client = Client()
        client.client_id = "client_123"
        client.client_secret = gen_salt(48)
        client.client_id_issued_at = time.time()
        client.client_secret_expires_at = 0  # never expires
        client.set_client_metadata({
            "redirect_uris": ["http://127.0.0.1:5000/login/callback"],
            "response_types": ["code", "token"],
            "scope": "profile",
            "grant_types": ["authorization_code"],
            "client_name": "My Example Client",
            "token_endpoint_auth_method": "client_secret_basic",
            "logo_uri": "https://cdn.freebiesupply.com/logos/large/2x/united-states-of-america-logo-png-transparent.png",
        })
        db.session.add(client)
        db.session.commit()

    return jsonify({
        'user_email': user.email,
        'user_password': '12345',
        'client_id': client.client_id,
        'client_secret': client.client_secret,
    })


@bp.route('/oauth/authorize', methods=['GET', 'POST'])
@login_required
def authorize():
    if request.method == 'GET':
        grant = auth_server.get_consent_grant(end_user=current_user)
        return render_template('authorize.html', client=grant.client)
    else:  # POST
        if 'approve' in request.form:
            grant_user = current_user
            return auth_server.create_authorization_response(grant_user=grant_user)
        else:
            return redirect('http://127.0.0.1:5000')


@bp.route('/oauth/token', methods=['POST'])
def issue_token():
    return auth_server.create_token_response()


@bp.route('/oauth/userinfo')
@require_oauth('profile')
def userinfo():
    user = User.query.get(current_token.user_id)
    return jsonify({
        'name': user.name,
        'email': user.email
    })


@bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = User.query.filter_by(email=email).first()
        if user and check_password_hash(user.password, password):
            login_user(user)
            return redirect(request.args.get('next') or '/')
        return 'Invalid credentials', 401
    return render_template('login.html')
