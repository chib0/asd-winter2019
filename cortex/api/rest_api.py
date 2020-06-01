import functools

import urlpath
from flask import Flask, request, Response, abort
from flask_cors import CORS
import json
import mimetypes

from cortex.utils.filesystem.user_storage import UserStorage
from cortex.utils.images import DepthImage

EXPOSED_SCHEMES = ('file',)

def _default_adapters():
    #TODO: change to suffix, that would require file saving change too
    return {lambda uri: uri.path.endswith('depth'): lambda data: DepthImage.from_bson_data(data).bson()}

def get_api(app_name, database, db_res_encoder=json.dumps, data_adapters=None):
    """
    returns an API implementation that can be `run(host, port`).
    :param app_name: name the app will receive
    :param database: the database implementation to use
    :param db_res_encoder: the encoder for database return values
    :param data_adapters: a (lambda uri: Bool => adapter) map, that will handle specific backend file uris differently
    :return:
    """
    app = Flask(app_name)
    CORS(app)
    data_adapters = data_adapters or _default_adapters()
    def _get_uri(thing, schemes=EXPOSED_SCHEMES):
        if not isinstance(thing, (bytes, str, urlpath.URL)):
            return None
        candidate = urlpath.URL(thing)
        return candidate if  candidate.scheme in schemes else None

    def _serve_resource(uri):
        with UserStorage.open(uri, 'rb') as stream:
            data = stream.read()
        for checker, adapter in data_adapters.items():
            if checker(uri):
                data = adapter(data)
                break
        guessed_type, _ = mimetypes.guess_type(str(uri))
        return Response(data, mimetype=guessed_type)


    def with_encoder(f):
        @functools.wraps(f)
        def deco(*args, **kwargs):
            return db_res_encoder(f(*args, **kwargs))
        return deco

    @app.route('/users')
    @with_encoder
    def get_users():
        return database.get_users(names=True)

    @app.route("/users/<id>")
    @with_encoder
    def get_user(id):
        return database.get_user_info(int(id)) or database.get_user(id)

    @app.route("/users/<id>/snapshots/")
    @app.route("/users/<id>/snapshots")
    @with_encoder
    def get_user_snapshots(id):
        return database.get_snapshots(id)

    def _get_snapshot(user_id, snapshot):
        sn = database.get_snapshot(user_id, snapshot)
        if not sn:
            abort(404)
        return sn

    @app.route("/users/<user_id>/snapshots/<snapshot>")
    @with_encoder
    def get_user_snapshot(user_id, snapshot):
        return list(_get_snapshot(user_id, snapshot).keys())

    @app.route("/users/<user_id>/snapshots/<snapshot>/<result>/")
    @app.route("/users/<user_id>/snapshots/<snapshot>/<result>")
    @with_encoder
    def get_user_snapshot_result(user_id, snapshot, result):

        maybe_uri = _get_snapshot(user_id, snapshot).get(result,None)
        if  maybe_uri is None:
            abort(404)
        thing = _get_uri(maybe_uri)
        if not thing:
            return maybe_uri
        return str(urlpath.URL(request.base_url) / 'data')


    @app.route("/users/<user_id>/snapshots/<snapshot>/<result>/data")
    def get_user_snapshot_result_data(user_id, snapshot, result):
        maybe_uri = _get_snapshot(user_id, snapshot)[result]
        thing = _get_uri(maybe_uri)
        if not thing:
            return maybe_uri
        return _serve_resource(thing)


    @app.route("/users/<user_id>/locations")
    @with_encoder
    def get_user_feelings(user_id):
        return database.get_user_locations(user_id)


    @app.route("/users/<user_id>/feelings")
    @with_encoder
    def get_user_locations(user_id):
        return database.get_user_feelings(user_id)


    return app

