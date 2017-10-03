import json
import os
import unittest
import tempfile
from mock import patch

from .server import app

import requests
import six.moves.urllib.parse as urlparse
import os
import time

from threading import Thread
import logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)



host = '127.0.0.1'
port = '5000'
def get_remote_base():
    return 'http://{host}:{port}'.format(host=host, port=port)

def setup_background_server():
    def start_server(app):
        app.run(threaded=True, host=host, port=port)

    global server_thread
    server_thread = Thread(target=start_server,
                       args=(app))
    server_thread.daemon = True
    server_thread.start()
    time.sleep(0.25) # give it a moment to settle
    logger.info('Server setup complete')

def teardown_background_server():
    route = '/v1/shutdown/'
    headers = {'Content-type': 'application/json'}
    requests.post(urlparse.urljoin(get_remote_base(), route),
                  headers=headers)
    server_thread.join() # wait until teardown happens
    logger.info('Server teardown complete')

def with_server(fn):
    fn.setup = setup_background_server
    fn.teardown = teardown_background_server
    return fn


# Tests ===============================================================================================================>

@with_server
def test_new_account(self, data='{}'):
    response = self.app.post('/v1/account/new', data=data, content_type='application/json')
    self.assertEqual(response.status_code, 200)
    response = json.loads(response.get_data())
    account_key = response['account_key']
    print(account_key)
    print(self.exchange.accounts[account_key].private_key)
    self.assertTrue(account_key in self.exchange.accounts)


class MainTest(unittest.TestCase):
    """Test case for the exchange methods."""

    def setUp(self):
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False
        app.config['DEBUG'] = False

        self.exchange = Exchange()

        self.settings = self.exchange.settings
        self.settings["public_rate_limit"] = ""
        self.settings["private_rate_limit"] = ""
        self.settings["default_initial_balance"] = 10000.00
        self.settings["default_initial_status"] = "ACTIVE"

        self.app = app.test_client()




    def test_auth_request(self):
        return

    def tearDown(self):
        return NotImplemented

if __name__ == "__main__":
    unittest.main()