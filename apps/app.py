
from flask import Flask, jsonify, g
from apps.views import auth_bp, note_bp
from apps.database import db
import os
import flask
from sqlalchemy.pool import NullPool
from flask_cors import CORS


import apps.settings as settings

def create_app():
    app = Flask(__name__)
    # Ok, we are using uWSGI framework to run our FLASK app.
    # It's a middleware between nginx and flask server.
    
    # uWSGI framework
    # Ok, so from what i understood about uWSGI is that
    # it runs on pre-forking mode by default. In pre-forking mode
    # the main process (master) loads up the flask app and the workers
    # processes are then forked from this main process, by this the workers
    # have the same memory as the main process until they modify it. After
    # which if any worker modify the memory it follow "copy on write" mechanism.
    # Basically we use uWSGI with pre-fork mode to leverage memory sharing
    # between master and worker processes.
    # https://stackoverflow.com/a/54346101
    # https://www.geeksforgeeks.org/copy-on-write/
    # https://uwsgi-docs.readthedocs.io/en/latest/articles/TheArtOfGracefulReloading.html#preforking-vs-lazy-apps-vs-lazy
    # https://stackoverflow.com/questions/41734740/minimal-example-of-uwsgis-shared-memory


    # Ok i did some more research.
    # https://stackoverflow.com/questions/69396898/trying-to-figure-out-uwsgi-thread-workers-configuration
    # https://uwsgi-docs.readthedocs.io/en/latest/ThingsToKnow.html
    # https://www.reddit.com/r/Python/comments/4s40ge/understanding_uwsgi_threads_processes_and_gil/?rdt=36855
    # https://www.bloomberg.com/company/stories/configuring-uwsgi-production-deployment/

    app.url_map.strict_slashes = False
    
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["SQLALCHEMY_DATABASE_URI"] = settings.SQLALCHEMY_DATABASE_URI
    # sqlalchemy
    # Architecture: https://docs.sqlalchemy.org/en/20/core/engines.html#engine-configuration
    # is sqlalchemy thread safe?
    # First sqlalchemy creates an engine which is a single process.
    # and by default the connection pool size is set to 5. Now as we
    # are running workers in os.fork() environment where workers can 
    # execute sql query concurrently which might lead to race conditions or
    # data inconsistency.
    # sqlalchemy doc actually address this issue here: https://docs.sqlalchemy.org/en/20/core/pooling.html#using-connection-pools-with-multiprocessing-or-os-fork
    # Don't pool conenctions. create new DB connection for each new sql command.
    # This will slow down our app :( 
    # TODO: Understand how to integrate flask-sqlalchemy with uWSGI workers.
    # Adding NullPool for now.
    app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {"poolclass": NullPool}
    # app.config["SQLALCHEMY_ECHO"] = True
    db.init_app(app)
    # cors enabled for frontend.
    CORS(app)

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
        # print ("Ok - [LOG] worker %d is making request." % uwsgi.worker_id())
        # print (f"Ok - [LOG] DB connection pool: {db.engine.pool.status()}")
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
        pass
        # print("Ok - [LOG] worker %d is up!" % uwsgi.worker_id())

    if bool(settings.JWT_SECRET_KEY) is False:
        print("[WARNING] app JWT_SECRET_KEY is not set.")

    version = (float(os.environ.get('API_VERSION', 0)))
    if not bool(version):
        print("[ERROR] please pass API_VERSION environment to docker cmd.")
    else:
        print(f"Ok - [INFO] API_VERSION is set to: {version}")
    
    @app.route("/version")
    def app_version():
        msg = {"version": version}
        return msg
    return app


