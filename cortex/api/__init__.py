import json
import threading

from cortex.utils import databases
from . import rest_api

def run_server(host, port, cortex_database):
    server = rest_api.get_api('cortex.api', cortex_database, json.dumps)
    server.run(host,  int(port))

def run_api_server(host, port, database_url, threaded=False, daemon=True):
    """
    runs the api server bound on the given host addr, port and connected to the given database.
    if threaded is True, starts the server on a different thread
    :param daemon: whether or not to start the server as a daemon. defaults to True
    :param host: host to bind on. localhost of 0.0.0.0
    :param port: port to bind on
    :param database_url: the database url to connect to.
    :param threaded: whether or not to run the server on a different thread.
    :return: the created thread object if True, None otherwise.
    """
    db = databases.repository.get_database(database_url)
    if not db:
        raise Exception(f"could not get database implementation for url {database_url}")
    if not host in ['0.0.0.0', '127.0.0.1']:
        raise ValueError(f"""host {host} invalid, please choose {" or ".join(["0.0.0.0", "127.0.0.1"])}""")
    args = (host, port, db)
    if not threaded:
        run_server(*args)
    else:
        t = threading.Thread(target=run_server, args=args, daemon=daemon)
        t.start()
        return t
