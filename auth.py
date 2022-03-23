import functools
from flask import (Blueprint, current_app, g, redirect, 
        render_template, request, session, url_for)
import msal

bp = Blueprint('auth', __name__, url_prefix='/auth')

@bp.route("/")
def index():
    print('===== session(user) ======')
    print(session.get("user"))
    if not session.get("user"):
        #session["flow"] = _build_auth_code_flow(scopes=app_config.SCOPE)
        #auth_url=session["flow"]["auth_uri"]
        #return redirect(auth_url)
        return redirect(url_for("auth.login"))

    return session.get("user")
#return 'logged in'

@bp.route("/login")
def login():
    # Technically we could use empty list [] as scopes to do just sign in,
    # here we choose to also collect end user consent upfront
    print(current_app.config)
    session["flow"] = _build_auth_code_flow(scopes=current_app.config['SCOPE'])
    print('======')
    print(session["flow"]["auth_uri"])
    print('======')
    return redirect(session["flow"]["auth_uri"])

#return render_template("auth/login.html", auth_url=session["flow"]["auth_uri"], version=msal.__version__)

@bp.route("/logout")
def logout():
    session.clear()  # Wipe out user and its token cache from session
    return redirect(  # Also logout from your tenant's web session
        current_app.config['AUTHORITY'] + "/oauth2/v2.0/logout" +
        "?post_logout_redirect_uri=" + url_for("auth.index", _external=True))

@bp.route(current_app.config['REDIRECT_PATH'])  # Its absolute URL must match your app's redirect_uri set in AAD
def authorized():
    try:
        cache = _load_cache()
        result = _build_msal_app(cache=cache).acquire_token_by_auth_code_flow(
            session.get("flow", {}), request.args)
        if "error" in result:
            return render_template("auth/error.html", result=result)

        # extract token claims from ms-azure reponse
        id_token_claims = result.get("id_token_claims")
        if current_app.config['AZURE_DESIRED_ROLE'] not in id_token_claims['roles']:
            return f"Desired role \"{current_app.config['AZURE_DESIRED_ROLE']}\" not assigned to user"

        # autherization passed -> start session
        session["user"] = id_token_claims
        _save_cache(cache)
    except ValueError:  # Usually caused by CSRF
        pass  # Simply ignore them
    return redirect(url_for("demo.index"))
#return redirect(url_for("auth.index"))

@bp.before_app_request
def load_logged_in_user():
    print('==== assign user ====')
    g.user = session.get('user')

def login_required(view):
    '''Decorater to be used with any function that requires login'''
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        token = _get_token_from_cache(current_app.config['SCOPE'])
        if not token:
            return redirect(url_for("auth.login"))

        return view(**kwargs)

    return wrapped_view

def _build_msal_app(cache=None, authority=None):
    return msal.ConfidentialClientApplication(
        current_app.config['CLIENT_ID'], authority=authority or
        current_app.config['AUTHORITY'],
        client_credential=current_app.config['CLIENT_SECRET'], token_cache=cache)

def _build_auth_code_flow(authority=None, scopes=None):
    return _build_msal_app(authority=authority).initiate_auth_code_flow(
        scopes or [],
        redirect_uri=url_for("auth.authorized", _external=True))

def _load_cache():
    cache = msal.SerializableTokenCache()
    if session.get("token_cache"):
        cache.deserialize(session["token_cache"])
    return cache

def _save_cache(cache):
    if cache.has_state_changed:
        session["token_cache"] = cache.serialize()

def _get_token_from_cache(scope=None):
    cache = _load_cache()  # This web app maintains one cache per session
    cca = _build_msal_app(cache=cache)
    accounts = cca.get_accounts()
    if accounts:  # So all account(s) belong to the current signed-in user
        result = cca.acquire_token_silent(scope, account=accounts[0])
        _save_cache(cache)
        return result


