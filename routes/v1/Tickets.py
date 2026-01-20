import json

from flask import jsonify, request
from flask_jwt_extended import get_jwt_identity, jwt_required
from http import HTTPStatus
from uuid import uuid4

from sqlalchemy import delete as sql_delete, select

from database import get_session
from models import Ticket
from modules.RESTful_Builder import Builder


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


def _serialize_showing(showing: dict | str) -> str:
    if isinstance(showing, str):
        return showing
    return json.dumps(showing, separators=(",", ":"))


def _deserialize_showing(showing: str | dict):
    if not isinstance(showing, str):
        return showing
    try:
        return json.loads(showing)
    except json.JSONDecodeError:
        return showing


@jwt_required()
def getAll():
    identity = get_jwt_identity()

    with get_session() as session:
        showings = session.scalars(
            select(Ticket.showing).where(Ticket.user_id == identity)
        ).all()
        showings = [_deserialize_showing(showing) for showing in showings]

    if not showings:
        return abort(404, "No tickets were found.")

    return send(200, {"showings": showings})


@jwt_required()
def getOne(id: str):
    identity = get_jwt_identity()

    with get_session() as session:
        ticket = session.scalar(
            select(Ticket).where(Ticket.uuid == id, Ticket.user_id == identity)
        )

    if ticket is None:
        return abort(404, f"The specified ticket was not found ({id}).")

    return send(200, {"showing": _deserialize_showing(ticket.showing)})


@jwt_required()
def create():
    identity = get_jwt_identity()

    showing = request.json.get("showing")
    if showing is None:
        return abort(400, "Missing value: showing")
    if not isinstance(showing, (dict, str)):
        return abort(400, "Invalid value: showing")

    ticket = Ticket(
        uuid=uuid(),
        showing=_serialize_showing(showing),
        user_id=identity,
    )
    ticket_uuid = ticket.uuid
    with get_session() as session:
        session.add(ticket)

    return send(201, {"message": "Ticket successfully created.", "uuid": ticket_uuid})


@jwt_required()
def delete(id: str | None = None):
    identity = get_jwt_identity()

    with get_session() as session:
        if id is not None:
            result = session.execute(
                sql_delete(Ticket).where(
                    Ticket.uuid == id,
                    Ticket.user_id == identity,
                )
            )
            if result.rowcount == 0:
                return abort(404, f"Ticket {id} not found.")
        else:
            session.execute(
                sql_delete(Ticket).where(
                    Ticket.user_id == identity,
                )
            )

    plural = "s" if id is None else ""
    return send(200, {"message": f"Ticket{plural} successfully deleted."})


bp = Builder("v1-tickets").bind(
    getAll=getAll,
    getOne=getOne,
    create=create,
    delete=delete,
).bp
