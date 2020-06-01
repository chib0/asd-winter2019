import base64
import json

import urlpath

class Consumer:
    """
    The basic class that formats, requests, and returns data from the rest endpoint.
    """
    def __init__(self, host, port):
        self.url = urlpath.URL().with_scheme('http').with_hostinfo(host, port)

    def _request(self, *path_parts):
        url =  self.url.joinpath(*map(str, path_parts))
        resp = url.get()
        if not resp.ok:
            return None
        try:
            return resp.json()
        except json.decoder.JSONDecodeError:
            return base64.encodebytes(resp.content)


    def get_users(self):
        """
        retrieves a list of users
        :return:
        """
        return self._request('users')
    
    def get_user(self, user_id):
        """
        retrieves user information for a user
        :param user_id:
        :return:
        """
        return self._request('users', user_id)

    def get_snapshots(self, user_id):
        """
        retrieves all user snapshot metadata
        :param user_id:
        :return:
        """
        return self._request('users', user_id, 'snapshots')
    
    def get_snapshot(self, user_id, snapshot_id_or_timestamp):
        """
        retrives the fields available in a specific snapshot
        :param user_id:
        :param snapshot_id_or_timestamp:
        :return:
        """
        return self._request('users', user_id, 'snapshots', snapshot_id_or_timestamp)

    def get_result(self, user_id, snapshot_id_or_timestamp, result):
        """
        retrives the actual value of a field in a user snapshot
        :param user_id:
        :param snapshot_id_or_timestamp:
        :param result:
        :return:
        """
        return self._request('users', user_id, 'snapshots', snapshot_id_or_timestamp, result.replace("-", "_"))

    def get_result_data(self, user_id, snapshot_id_or_timestamp, result):
        """
        retrieves the DATA of a result, if applicable (which is, if the result was a URL).
        :param user_id:
        :param snapshot_id_or_timestamp:
        :param result:
        :return:
        """
        return self._request('users', user_id, 'snapshots', snapshot_id_or_timestamp, result.replace("-", "_"), 'data')

    @property
    def host(self):
        return self.url.hostname

    @property
    def port(self):
        return self.url.port
