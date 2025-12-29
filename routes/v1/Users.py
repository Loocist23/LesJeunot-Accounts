from cryptography.fernet import Fernet, InvalidToken
from flask import jsonify, request
from flask_jwt_extended import (
    create_access_token,
    create_refresh_token,
    get_jwt_identity,
    jwt_required,
)
from dotenv import load_dotenv
from hashlib import sha256
from http import HTTPStatus
from os import getenv
from uuid import uuid4

from sqlalchemy import select

from database import get_session
from models import User
from modules.Hasher import Hasher
from modules.RESTful_Builder import Builder


load_dotenv(".env")
_key = getenv("KEY")
if not _key:
    raise RuntimeError("Environment variable KEY must be set for encryption.")
KEY = _key

HASHER = Hasher()


def send(code: int, response: dict | None = None):
    payload = {"status": code}
    if response is not None:
        payload["data"] = response
    return jsonify(payload), code


def abort(code: int, message: str):
    return (
        jsonify(
            {"status": code, "error": HTTPStatus(code).phrase, "message": message}
        ),
        code,
    )


def uuid() -> str:
    return uuid4().hex


def checkKey() -> None:
    k = KEY.encode("utf-8")
    try:
        Fernet(k)
    except ValueError as exc:
        raise KeyError(
            "The key is not in a valid format. (32 Bytes URL-Safe Encoded Base64)"
        ) from exc


def _get_cipher() -> Fernet:
    checkKey()
    return Fernet(KEY.encode("utf-8"))


def encrypt(message: str) -> str:
    cipher = _get_cipher()
    return cipher.encrypt(message.encode("utf-8")).decode("utf-8")


def decrypt(message: str) -> str | None:
    cipher = _get_cipher()
    try:
        return cipher.decrypt(message.encode("utf-8")).decode("utf-8")
    except InvalidToken:
        return None


@jwt_required()
def getMe():
    identity = get_jwt_identity()

    with get_session() as session:
        user = session.get(User, identity)
        if user is None:
            return abort(404, "User not found.")

        return send(
            200,
            {
                "lastname": decrypt(user.lastname),
                "firstname": decrypt(user.firstname),
                "age": decrypt(user.age),
                "email": decrypt(user.email),
                "role": user.role,
            },
        )


def create():
    lastname = request.json.get("lastname")
    firstname = request.json.get("firstname")
    age = request.json.get("age")
    email = request.json.get("email")
    password = request.json.get("password")

    data = {
        "lastname": lastname,
        "firstname": firstname,
        "age": age,
        "email": email,
        "password": password,
    }
    missing = [key for key, value in data.items() if value is None]
    if missing:
        return abort(400, f"Missing value(s): [{', '.join(missing)}]")

    email_clean = email.strip()  # type: ignore[union-attr]
    role = "admin" if email_clean.endswith("@shadoweb.fr") else "user"
    email_hash = sha256(email_clean.lower().encode("utf-8")).hexdigest()

    with get_session() as session:
        existing = session.scalar(
            select(User.uuid).where(User.email_hash == email_hash)
        )
        if existing:
            return abort(409, "Account already exists.")

        user = User(
            uuid=uuid(),
            lastname=encrypt(lastname),  # type: ignore[arg-type]
            firstname=encrypt(firstname),  # type: ignore[arg-type]
            age=encrypt(age),  # type: ignore[arg-type]
            email=encrypt(email_clean),
            email_hash=email_hash,
            password=HASHER.hash(password),  # type: ignore[arg-type]
            role=role,
        )
        session.add(user)

    return send(201, {"message": "User successfully created."})


@jwt_required()
def modify():
    identity = get_jwt_identity()

    lastname = request.json.get("lastname")
    firstname = request.json.get("firstname")
    age = request.json.get("age")
    email = request.json.get("email")
    password = request.json.get("password")

    updates: dict[str, str] = {}
    if lastname is not None:
        updates["lastname"] = encrypt(lastname)
    if firstname is not None:
        updates["firstname"] = encrypt(firstname)
    if age is not None:
        updates["age"] = encrypt(age)
    if email is not None:
        email_clean = email.strip()
        updates["email_hash"] = sha256(
            email_clean.lower().encode("utf-8")
        ).hexdigest()
        updates["email"] = encrypt(email_clean)
        updates["role"] = "admin" if email_clean.endswith("@shadoweb.fr") else "user"
    if password is not None:
        updates["password"] = HASHER.hash(password)

    if not updates:
        return abort(400, "At least one field is required.")

    with get_session() as session:
        user = session.get(User, identity)
        if user is None:
            return abort(404, "User not found.")

        for field, value in updates.items():
            setattr(user, field, value)

    return send(200, {"message": "User successfully modified."})


@jwt_required()
def delete():
    identity = get_jwt_identity()

    with get_session() as session:
        user = session.get(User, identity)
        if user is None:
            return abort(404, "User not found.")
        session.delete(user)

    return send(200, {"message": "User successfully deleted."})


def login():
    email = request.json.get("email")
    password = request.json.get("password")

    data = {"email": email, "password": password}
    missing = [key for key, value in data.items() if value is None]
    if missing:
        return abort(400, f"Missing value(s): [{', '.join(missing)}]")

    email_clean = email.strip()  # type: ignore[union-attr]
    email_hash = sha256(email_clean.lower().encode("utf-8")).hexdigest()

    with get_session() as session:
        user = session.scalar(select(User).where(User.email_hash == email_hash))
        if user is None:
            return abort(401, "Email or password invalid.")

        decrypted_email = decrypt(user.email)
        if decrypted_email != email_clean:
            return abort(401, "Email or password invalid.")

        password_valid, new_password = HASHER.verify_and_rehash(
            user.password, password  # type: ignore[arg-type]
        )
        if not password_valid:
            return abort(401, "Email or password invalid.")

        if new_password != user.password:
            user.password = new_password

        identity = user.uuid

    access = create_access_token(identity=identity, fresh=True)
    refresh = create_refresh_token(identity=identity)

    return send(
        200,
        {
            "message": "User successfully logged in.",
            "token": {"access": access, "refresh": refresh},
        },
    )


@jwt_required(refresh=True)
def refresh():
    identity = get_jwt_identity()

    access = create_access_token(identity=identity, fresh=False)

    return send(200, {"token": {"access": access}})


bp = Builder("v1-users").bind(
    login=login,
    refresh=refresh,
    getMe=getMe,
    create=create,
    modify=modify,
    delete=delete,
).bp
