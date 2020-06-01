import base64
import json

import urlpath

class Consumer:
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
        return self._request('users')
    
    def get_user(self, user_id):
        return self._request('users', user_id)

    def get_snapshots(self, user_id):
        return self._request('users', user_id, 'snapshots')
    
    def get_snapshot(self, user_id, snapshot_id_or_timestamp):
        return self._request('users', user_id, 'snapshots', snapshot_id_or_timestamp)

    def get_result(self, user_id, snapshot_id_or_timestamp, result):
        return self._request('users', user_id, 'snapshots', snapshot_id_or_timestamp, result)

    def get_result_data(self, user_id, snapshot_id_or_timestamp, result):
        return self._request('users', user_id, 'snapshots', snapshot_id_or_timestamp, result, 'data')

    @property
    def host(self):
        return self.url.hostname

    @property
    def port(self):
        return self.url.port
