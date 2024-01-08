
from flask import Flask, jsonify, g
from apps.views import auth_bp, note_bp
from apps.database import db
import flask

import apps.settings as settings

def create_app():
    app = Flask(__name__)
    app.url_map.strict_slashes = False

    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["SQLALCHEMY_DATABASE_URI"] = settings.SQLALCHEMY_DATABASE_URI
    db.init_app(app)
    # with app.app_context():
    #     # if not database_exists(settings.SQLALCHEMY_DATABASE_URI)
    #     from sqlalchemy import create_engine
    #     import sqlalchemy
    #     engine = create_engine(settings.SQLALCHEMY_DATABASE_URI)
    #     sqlconnect = engine.connect()
    #     assert isinstance(sqlconnect, sqlalchemy.engine.Connection)
    #     is_authtable_present = engine.dialect.has_table(sqlconnect, "auth")
    #     # is_notestable_present = sqlalchemy.engine.dialect.has_table(
    #     #     settings.SQLALCHEMY_DATABASE_URI, 
    #     #     "auth",
    #     # )
    #     if not is_authtable_present:
    #         print("Table not present in database, creating tables...", flush=True)
    #         # db.create_all()
    #     else:
    #         print("Tabes already created.", flush=True)
    
    app.register_blueprint(
        auth_bp, url_prefix=f"/api"
    )
    app.register_blueprint(
        note_bp, url_prefix=f"/api"
    )
    @app.errorhandler(404)
    def resource_not_found(e):  
        return flask.make_response(jsonify(error=str(e)), 404)

    @app.before_request
    def init_db():
        with app.app_context():
            db.create_all()
            db.session.commit()
        g.db = db

    @app.after_request
    def log_request(response):
        import socket
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM); s.connect(("8.8.8.8", 80)); ip_address = s.getsockname()[0]
        print (f"Ok - [LOG] CONTAINER IP: {ip_address}")
        print (f"Ok - [LOG] status code: {response.status_code}")
        return response
    # app.run(debug=1)
    return app
