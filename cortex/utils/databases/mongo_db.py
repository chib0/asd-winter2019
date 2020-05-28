import functools

import pymongo
import urlpath

from cortex import configuration

SCHEME = 'mongodb'

def _as_list(f):
    @functools.wraps(f)
    def deco(*args, **kwargs):
        return list(f(*args, **kwargs))
    return deco

class MongoDB:
    def __init__(self, client, url=None):
        self.url = url
        self.client = client

    @classmethod
    def connect(cls, url):
        return cls(pymongo.MongoClient(host=url.hostname, port=url.port), url)

    def update_snapshot(self, user, timestamp, data):
        self.snapshots.find_one_and_update({"user": user, "timestamp": timestamp}, {"$set": data}, upsert=True)

    @_as_list
    def get_snapshots(self, user):
        return self.snapshots.find({"user": user}, projection={"_id":1, "timestamp":1})

    def get_snapshot(self, user, id=None, timestamp=None):
        if not (id or timestamp): return None
        query = {"user": user}
        if id:
            query['_id'] = id
        else:
            query['timestamp'] = int(timestamp)


        return self.snapshots.find_one(query, projection={"_id": 0, 'user': 0})

    def maybe_create_user(self, _id, user_info):
        if self.users.find_one({'id': int(_id)}):
            return
        self.users.insert_one({'id': int(_id), 'info': user_info})

    @_as_list
    def get_users(self):
        return self.users.find(projection={'id': 1, "_id": 0})

    def get_user_info(self, _id):
        return self.users.find_one({'id': int(_id)})['info']

    @property
    def db(self):
        return self.client.tests_cortex if configuration.testing else self.client.cortex

    @property
    def snapshots(self):
        return self.db.get_collection('snapshots')

    @property
    def users(self):
        return self.db.get_collection("users")

def get_database(url):
    url = urlpath.URL(url)
    if url.scheme != SCHEME:
        return None

    return MongoDB.connect(url.with_scheme(''))
