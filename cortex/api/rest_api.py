import functools

import urlpath
from flask import Flask, request, Response, abort
import json
import mimetypes

from cortex.utils.user_storage import UserStorage

EXPOSED_SCHEMES = ('file',)


def get_api(app_name, database, db_res_encoder=json.dumps):
    app = Flask(app_name)
    def _get_uri(thing, schemes=EXPOSED_SCHEMES):
        if not isinstance(thing, (bytes, str, urlpath.URL)):
            return None
        candidate = urlpath.URL(thing)
        return candidate if  candidate.scheme in schemes else None

    def _serve_resource(uri):
        with UserStorage.open(uri, 'rb') as stream:
            data = stream.read()

        return Response(data, mimetype=mimetypes.guess_type(uri))



    def uri_exposer(f):
        """
        decorator that checks if the return value is a uri of a supported scheme, if it is,
        returns a data url that consumes said data
        :param f: function  to check
        :return: decorator
        """
        @functools.wraps(f)
        def decorator(*args, **kwargs):
            maybe_uri = f(*args, **kwargs)
            thing = _get_uri(maybe_uri)
            if not thing:
                return maybe_uri
            return str(urlpath.URL(request.base_url) / 'data')
        return decorator

    def uri_server(f=None, / , handler=None, on_no_url=None):
        """
        decorator checks if the functions return value is a uri. if it is, reads it and returns the data.
        function  to check
        :return: decorator
        """
        if f is None and handler is None:
            raise ValueError("decorator not called properly. either no handler or no decoratee")

        if (f is not None and handler is None) or f is None:
            return lambda x: uri_server(x, handler=f, on_no_url=(on_no_url or (lambda: abort(404))))

        @functools.wraps(f)
        def decorator(*args, **kwargs):
            maybe_uri = f(*args, **kwargs)
            thing = _get_uri(maybe_uri)
            if not thing:
                return maybe_uri
            return handler(thing)
        return decorator

    def with_encoder(f):
        @functools.wraps(f)
        def deco(*args, **kwargs):
            return db_res_encoder(f(*args, **kwargs))
        return deco

    @app.route('/users')
    @with_encoder
    def get_users():
        return database.get_users()

    @app.route("/users/<id>")
    @with_encoder
    def get_user(id):
        return database.get_user_info(int(id)) or database.get_user(id)

    @app.route("/users/<id>/snapshots")
    @with_encoder
    def get_user_snapshots(id):
        return database.get_snapshots(id)

    @app.route("/users/<user_id>/snapshots/<snapshot>")
    @with_encoder
    def get_user_snapshot(user_id, snapshot):
        return list(database.get_snapshot(user_id, snapshot).keys())

    @app.route("/users/<user_id>/snapshots/<snapshot>/<result>")
    @with_encoder
    @uri_exposer
    def get_user_snapshot_result(user_id, snapshot, result):
        return database.get_snapshot(user_id, snapshot)[result]

    @app.route("/users/<user_id>/snapshots/<snapshot>/<result>/data")
    @uri_server(handler=_serve_resource)
    def get_user_snapshot_result_data(user_id, snapshot, result):
        return database.get_snapshot(user_id, snapshot)[result]

    return app
