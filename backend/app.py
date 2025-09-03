from __future__ import annotations
from flask import Flask, jsonify, redirect, request, make_response, url_for
from dotenv import load_dotenv
import os
import workos
from functools import wraps
from workos import WorkOSClient

load_dotenv()

# Read env vars
workos = WorkOSClient(
    api_key=os.getenv("WORKOS_API_KEY"), client_id=os.getenv("WORKOS_CLIENT_ID")
)

cookie_password = os.getenv("WORKOS_COOKIE_PASSWORD")
FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:5173")


def create_app() -> Flask:
    app = Flask(__name__)

    def with_auth(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            session = workos.user_management.load_sealed_session(
                sealed_session=request.cookies.get("wos_session"),
                cookie_password=cookie_password,
            )
            auth_response = session.authenticate()
            if auth_response.authenticated:
                return f(*args, **kwargs)

            if (
                auth_response.authenticated is False
                and auth_response.reason == "no_session_cookie_provided"
            ):
                return make_response(redirect("/login"))

            # If no session, attempt a refresh
            try:
                print("Refreshing session")
                result = session.refresh()
                if result.authenticated is False:
                    return make_response(redirect("/login"))

                response = make_response(redirect(request.url))
                response.set_cookie(
                    "wos_session",
                    result.sealed_session,
                    secure=True,
                    httponly=True,
                    samesite="lax",
                )
                return response
            except Exception as e:
                print("Error refreshing session", e)
                response = make_response(redirect("/login"))
                response.delete_cookie("wos_session")
                return response

        return decorated_function

    @app.route("/login")
    def login():
        authorization_url = workos.user_management.get_authorization_url(
            provider="authkit", redirect_uri=os.getenv("WORKOS_REDIRECT_URI")
        )

        return redirect(authorization_url)

    @app.route("/callback")
    def callback():
        code = request.args.get("code")

        try:
            auth_response = workos.user_management.authenticate_with_code(
                code=code,
                session={"seal_session": True, "cookie_password": cookie_password},
            )

            # Use the information in auth_response for further business logic.

            response = make_response(redirect(FRONTEND_URL))
            # store the session in a cookie
            response.set_cookie(
                "wos_session",
                auth_response.sealed_session,
                secure=True,
                httponly=True,
                samesite="lax",
            )
            return response

        except Exception as e:
            print("Error authenticating with code", e)
            return redirect(url_for("/login"))

    @app.route("/dashboard")
    @with_auth
    def dashboard():
        print("IN DASHBOARD")
        session = workos.user_management.load_sealed_session(
            sealed_session=request.cookies.get("wos_session"),
            cookie_password=cookie_password,
        )

        response = session.authenticate()
        if not response.authenticated:
            return jsonify({"authenticated": False}), 401
        else:
            current_user = response.user
            print(f"User {current_user.first_name} is logged in")
            return jsonify(
                {
                    "authenticated": True,
                    "user": {
                        "id": getattr(current_user, "id", None),
                        "email": getattr(current_user, "email", None),
                        "first_name": getattr(current_user, "first_name", None),
                        "last_name": getattr(current_user, "last_name", None),
                        "email_verified": getattr(current_user, "email_verified", None),
                        "profile_photo_url": getattr(current_user, "profile_photo_url", None),
                    },
                }
            )

    @app.route("/logout")
    def logout():
        session = workos.user_management.load_sealed_session(
            sealed_session=request.cookies.get("wos_session"),
            cookie_password=cookie_password,
        )
        url = session.get_logout_url()

        # After log out has succeeded, the user will be redirected to your
        # app homepage which is configured in the WorkOS dashboard
        response = make_response(redirect(url))
        response.delete_cookie("wos_session")

        return response

    @app.get("/api/me")
    def me():
        session = workos.user_management.load_sealed_session(
            sealed_session=request.cookies.get("wos_session"),
            cookie_password=cookie_password,
        )
        result = session.authenticate()
        if not result.authenticated:
            return jsonify({"authenticated": False}), 401

        user = result.user
        return jsonify({
            "authenticated": True,
            "user": {
                "id": getattr(user, "id", None),
                "email": getattr(user, "email", None),
                "first_name": getattr(user, "first_name", None),
                "last_name": getattr(user, "last_name", None),
                "email_verified": getattr(user, "email_verified", None),
                "profile_photo_url": getattr(user, "profile_photo_url", None),
            }
        })
        
    @app.get("/health")
    def health():
        return jsonify(status="ok")

    @app.get("/api/hello")
    def hello():
        return jsonify(message="Hello from Flask 👋")

    return app


# Allows `flask --app app run` and also `python app.py`
if __name__ == "__main__":
    app = create_app()
    # debug=True enables auto-reload; host makes it reachable for a future frontend
    app.run(debug=True, host="127.0.0.1", port=5000)
