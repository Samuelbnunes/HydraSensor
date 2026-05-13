from flask import Blueprint, request

from routes.helpers import json_data, json_error
from services.auth_service import authenticate_user, create_user

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/v1/auth/login", methods=["POST"])
def login():
    payload = request.get_json(silent=True) or {}

    username = str(payload.get("username") or "").strip()
    password = str(payload.get("password") or "")

    if not username or not password:
        return json_error(
            "INVALID_INPUT",
            "Usuario e senha sao obrigatorios.",
            status=400
        )

    user = authenticate_user(username, password)

    if user is None:
        return json_error(
            "INVALID_CREDENTIALS",
            "Usuario ou senha invalidos.",
            status=401
        )

    return json_data({
        "user": user,
        "token": "admin-demo-token"
    })


@auth_bp.route("/v1/auth/register", methods=["POST"])
def register():
    payload = request.get_json(silent=True) or {}

    username = str(payload.get("username") or "").strip()
    password = str(payload.get("password") or "")

    if not username or not password:
        return json_error(
            "INVALID_INPUT",
            "Usuario e senha sao obrigatorios.",
            status=400
        )

    try:
        user = create_user(username, password)
        return json_data({
            "message": "Usuario criado com sucesso.",
            "user": user
        }, status=201)
    except ValueError as e:
        return json_error("USER_EXISTS", str(e), status=409)
    except Exception as e:
        return json_error("INTERNAL_ERROR", str(e), status=500)
