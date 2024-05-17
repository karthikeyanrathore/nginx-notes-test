from flask_restful import Resource
from flask import g, jsonify, make_response, request
import apps.models as models
import jwt
import functools
from jwt.exceptions import InvalidSignatureError, DecodeError
from datetime import (
    datetime,
    timezone,
    timedelta
)
from jwt import ExpiredSignatureError

from apps.settings import JWT_SECRET_KEY

def response(status_code, message):
    if status_code != 200:
        return make_response(jsonify({"error": f"{message}"}), status_code)
    return make_response(jsonify({"data": message}), 200)


def is_token_valid(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            accesstoken = request.headers.get("Authorization")[7:]
            jwt.decode(accesstoken, JWT_SECRET_KEY, algorithms=["HS256"])
        except InvalidSignatureError:
            return response(401, "Invalid Access token.")
        except TypeError:
            return response(401, "Please provide access token in headers.")
        except DecodeError:
            return response(401, "JWT exception raised. Please input valid access token.")
        except ExpiredSignatureError:
            return response(401, "Your Access token has expired. Please login again.")
        return func(*args, **kwargs)
    return wrapper

def get_username_from_token():
    accesstoken = request.headers.get("Authorization")[7:]
    return jwt.decode(accesstoken, JWT_SECRET_KEY, algorithms=["HS256"])["username"]

class RegisterAuth(Resource):
    def post(self):
        request_data = request.get_json()
        if not request_data:
            return response(404, "Please help to provide JSON inputs")
        username = request_data["username"]
        password = request_data["password"]
        if g.db.session.query(models.Auth).filter_by(name=username).one_or_none():
            return response(403, "Username already exists. Please help to choose different username.")
        authdata = models.Auth(name=username, password=password)
        g.db.session.add(authdata)
        g.db.session.commit()
        # TODO: add access token
        return response(200, "success")

class LoginAuth(Resource):
    def post(self):
        request_data = request.get_json()
        username = request_data["username"]
        password = request_data["password"]
        auth = g.db.session.query(models.Auth).filter_by(name=username).one_or_none()
        if not auth:
            return response(401, "Username does not exists. Please first signup.")
        if auth.password != password:
            return response(401, "Incorrect password.")
        # TODO: add access token
        auth_jwt = {
            "username": username,
            "exp": datetime.now(tz=timezone.utc) + timedelta(hours=2)
        }
        access_token = jwt.encode(auth_jwt, JWT_SECRET_KEY, algorithm="HS256")
        ret = auth.serialize()
        ret["access_token"] = access_token
        return response(200, ret)

class Notes(Resource):
    @is_token_valid
    def get(self):
        # notes = (g.db.session.query(Auth).one_or_none())
        # print(notes)
        # print(notes.serialize())
        username = get_username_from_token()
        auth = g.db.session.query(models.Auth).filter_by(name=username).one_or_none()
        if not auth:
            return response(200, (
                "weird error", 
                "access token is valid but for some reason username does not exists in database.",
                "Please don't run docker-compose down -v again and again. it removes data from database",
            ))
        ret = []
        for note in auth.notes:
            ret.append({"message": note.message, "note_id": note.id})
        return response(200, {"notes" : ret})
    
    @is_token_valid
    def post(self):
        request_data = request.get_json()
        note_message = request_data["note"]
        username = get_username_from_token()
        authdata = g.db.session.query(models.Auth).filter_by(name=username).one()
        note = models.Notes(message=str(note_message), authenticated_user=authdata)
        g.db.session.add(note)
        g.db.session.commit()
        return response(200, "Successfully created a note.")

class Note(Resource):
    @is_token_valid
    def get(self, id):
        note = g.db.session.query(models.Notes).filter_by(id=id).one_or_none()
        if not note:
            return response(404, "Note not found.")
        return response(200, {"note": note.message})
    
    @is_token_valid
    def put(self, id):
        request_data = request.get_json()
        note_message = request_data["note"]
        note = g.db.session.query(models.Notes).filter_by(id=id).one_or_none()
        if not note:
            return response(404, "Note not found.")
        note.message = str(note_message)
        g.db.session.commit()
        return response(200, "Note updated.")
    
    @is_token_valid
    def delete(self, id):
        note = g.db.session.query(models.Notes).filter_by(id=id).delete()
        g.db.session.commit()
        return response(200, "Note deleted.")


class ShareNote(Resource):
    @is_token_valid
    def post(self, id):
        request_data = request.get_json()
        another_username = request_data["another_username"]
        another_user = g.db.session.query(models.Auth).filter_by(name=another_username).one_or_none()
        if not another_user:
            return response(404, "username not found. Please input valid username to share note with.")
        note = g.db.session.query(models.Notes).filter_by(id=id).one_or_none()
        if not note:
            return response(404, "Note not found.")
        print(f"Ok - Sharing <note:{note.id}> with {another_user.name}")
        write_notesdb = models.Notes
        note = write_notesdb(
            message=note.message,
            authenticated_user=another_user
        )
        g.db.session.add(note)
        g.db.session.commit()
        return response(200, f"Successfully shared note with user: {another_user.name}.")


class SearchNote(Resource):
    @is_token_valid
    def get(self):
        searchmsg = request.args.get("q")
        notes = models.Notes.query.filter(models.Notes.__ts_vector__.match(searchmsg)).all()
        if not notes:
            return response(404, "Note not found.")
        
        # print(note, flush=True)
        ret = []
        if isinstance(notes, list):
            for note in notes:
                ret.append(note.serialize())
        else:
            ret = note.serialize()
        return response(200, {"note": ret})
    
class RawNote(Resource):
    def get(self, id):
        note = g.db.session.query(models.Notes).filter_by(id=id).one_or_none()
        if not note:
            return response(404, "Note not found.")
        return response(200, {"note": note.message})
    