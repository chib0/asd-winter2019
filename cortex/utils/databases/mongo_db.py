import contextlib
import functools

import pymongo
from bson import objectid, errors
import urlpath

from cortex import configuration
from cortex.utils import logging

SCHEME = 'mongodb'



def _as_jsonable_list(f):
    @functools.wraps(f)
    def deco(*args, **kwargs):
        res = list(f(*args, **kwargs))
        for i in res:
            for k, v in i.items():
                if isinstance(v, objectid.ObjectId):
                    i[k] = str(v)
        return res
    return deco

class MongoDB:
    def __init__(self, client, url=None):
        self.url = url
        self.client = client
        self._logger = logging.get_instance_logger(self)

    @classmethod
    def connect(cls, url):
        url = urlpath.URL(url)
        return cls(pymongo.MongoClient(host=url.hostname, port=url.port), url)

    def update_snapshot(self, user, timestamp, data):
        self.snapshots.find_one_and_update({"user": int(user), "timestamp": int(timestamp)}, {"$set": data},
                                           upsert=True)

    @_as_jsonable_list
    def get_snapshots(self, user):
        return self.snapshots.find({"user": int(user)}, projection={"_id":1, "timestamp":1})

    def get_snapshot(self, user, id_or_timestamp):
        query = {"user": int(user)}
        try:
            query['_id'] = objectid.ObjectId(id_or_timestamp)
        except errors.InvalidId as e:
            try:
                query['timestamp'] = int(id_or_timestamp)
            except Exception:
                self._logger.error(f"could not turn {id_or_timestamp} into snapshot identifier")
                return None
        self._logger.info(f"trying to get with {query}")
        return self.snapshots.find_one(query, projection={"_id": 0, 'user': 0})

    def maybe_create_user(self, _id, user_info):
        if self.users.find_one({'id': int(_id)}):
            return
        self.users.insert_one({'id': int(_id), 'info': user_info})

    @_as_jsonable_list
    def get_users(self,_ids=True, names=False):
        projection = {'_id':0}
        if _ids:
            projection['id'] = 1
        if names:
            projection['info.username'] = 1
        return self.users.find(projection=projection)

    def get_user_info(self, _id):
        return self.users.find_one({'id': int(_id)})['info']

# TODO: make the database able to load these dynamically instead, like plugins
    @_as_jsonable_list
    def get_user_locations(self, id, start=None, end=None):
        """
        gets the locatiosn of the user between the start and the end timestamps.
        TODO: make the start and end timestamps work
        :param id:
        :param start:
        :param end:
        :return:
        """
        return (i['pose']['translation'] for i in self.snapshots.find({'user': int(id)}, {'pose.translation': 1, '_id':0}))


    @_as_jsonable_list
    def get_user_feelings(self, id, start=None, end=None):
        """
        gets the locatiosn of the user between the start and the end timestamps.
        TODO: make the start and end timestamps work
        :param id:
        :param start:
        :param end:
        :return:
        """
        return (i for i in self.snapshots.find({'user': int(id)}, {'feelings': 1, 'timestamp':1, '_id':0}))

    @property
    def db(self):
        return self.client.tests_cortex if configuration.is_testing() else self.client.cortex

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
