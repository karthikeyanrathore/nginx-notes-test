from apps.resources import (
    RegisterAuth,
    LoginAuth,
    Notes,
    Note,
    ShareNote,
    SearchNote,
)

from flask import Blueprint
from flask_restful import Api

auth_bp = Blueprint("auth", __name__)
note_bp = Blueprint("notes", __name__)

auth_api = Api(auth_bp)
note_api = Api(note_bp)

auth_api.add_resource(RegisterAuth, "/auth/signup")
auth_api.add_resource(LoginAuth, "/auth/login")

note_api.add_resource(Notes, "/notes")
note_api.add_resource(Note, "/notes/<int:id>")
note_api.add_resource(ShareNote, "/notes/<int:id>/share")
note_api.add_resource(SearchNote, "/search")
