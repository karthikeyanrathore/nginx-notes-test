
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
    app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {'pool_size': 10}
    # app.config["SQLALCHEMY_ECHO"] = True
    db.init_app(app)
    
    with app.app_context():
        print("Ok - [LOG] creating tables...")
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
    def flaskg_db():
        g.db = db

    @app.after_request
    def log_request(response):
        import socket
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM); s.connect(("8.8.8.8", 80)); ip_address = s.getsockname()[0]
        print (f"Ok - [LOG] CONTAINER IP: {ip_address}")
        print (f"Ok - [LOG] status code: {response.status_code}")
        return response
    # app.run(debug=1)
    from uwsgidecorators import postfork, uwsgi
    @postfork
    def fork_caller():
        # Each worker process should handle there own db connection pool.
        # If worker's share db connection pool then it may lead to concurrency issues.
        # Thankfully sqlalchemy pooled connections are not shared to forked processes.
        # https://docs.sqlalchemy.org/en/13/core/pooling.html#using-connection-pools-with-multiprocessing-or-os-fork
        # https://stackoverflow.com/a/15939406
        print("Ok - [LOG] worker %d spinning flask app" % uwsgi.worker_id())

    return app
