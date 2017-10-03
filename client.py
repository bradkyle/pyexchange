import requests
import six.moves.urllib.parse as urlparse
import json
import os
import base64
import hmac
import hashlib
import logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

from exchange.error import ServerError

class Client(object):
    """
    Exchange client interfaces with the exchange server
    """
    def __init__(self, remote_base):
        self.remote_base = remote_base
        self.session = requests.Session()
        self.session.headers.update({'Content-type': 'application/json'})

    def _parse_server_error_or_raise_for_status(self, resp):
        j = {}
        try:
            j = resp.json()
        except:
            # Most likely json parse failed because of network error, not server error (server
            # sends its errors in json). Don't let parse exception go up, but rather raise default
            # error.
            resp.raise_for_status()
        if resp.status_code != 200 and "message" in j:  # descriptive message from server side
            raise ServerError(message=j["message"], status_code=resp.status_code)
        resp.raise_for_status()
        return j

    def _set_headers(self, payload, api_secret, api_key):
        payload = str.encode(json.dumps(payload))
        b64 = base64.b64encode(payload)

        # sign the requests
        signature = hmac.new(str.encode(api_secret), b64, hashlib.sha384).hexdigest()

        headers = {
            'Content-Type': 'text/plain',
            'X-APIKEY': api_key,
            'X-PAYLOAD': b64,
            'X-SIGNATURE': signature
        }
        return headers

    def _post_request(self, route, data):
        url = urlparse.urljoin(self.remote_base, route)
        logger.info("POST {}\n{}".format(url, json.dumps(data)))
        resp = self.session.post(urlparse.urljoin(self.remote_base, route),
                                 data=json.dumps(data))
        return self._parse_server_error_or_raise_for_status(resp)

    def _get_request(self, route):
        url = urlparse.urljoin(self.remote_base, route)
        logger.info("GET {}".format(url))
        resp = self.session.get(url)
        return self._parse_server_error_or_raise_for_status(resp)

    def new_account(self, status=None, starting_balances=None):
        route = '/v1/account/new'
        data = {
            'status': status,
            'starting_balances': starting_balances,
        }
        resp = self._post_request(route, data)
        account_key = resp['account_key']
        account_private = resp['account_private']
        return account_key, account_private

    def list_all_accounts(self):
        route = '/v1/accounts/'
        resp = self._get_request(route)
        all_envs = resp['all_accounts']
        return all_envs

    def destroy_account(self, account_key):
        route = '/v1/account/{}/destroy/'.format(account_key)
        self._post_request(route, None)

if __name__ == '__main__':
    remote_base = 'http://127.0.0.1:8080'
    client = Client(remote_base)

