
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
    with app.app_context():
        db.create_all() 
    
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
    def make_db_g():
        g.db = db

    # app.run(debug=1)
    return app

# if __name__ == "__main__":
#     app = Flask(__name__)
#     app.url_map.strict_slashes = False

#     app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
#     app.config["SQLALCHEMY_DATABASE_URI"] = settings.SQLALCHEMY_DATABASE_URI
#     db.init_app(app)
#     with app.app_context():
#         db.create_all() 
    
#     app.register_blueprint(
#         auth_bp, url_prefix=f"/api"
#     )
#     app.register_blueprint(
#         note_bp, url_prefix=f"/api"
#     )

#     @app.errorhandler(404)
#     def resource_not_found(e):  
#         return flask.make_response(jsonify(error=str(e)), 404)

#     @app.before_request
#     def make_db_g():
#         g.db = db

#     app.run(debug=1)