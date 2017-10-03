import json
import os
import unittest
import tempfile

import pytest
from mock import patch

import exchange.server
from    exchange.test.client import Client

import requests
import six.moves.urllib.parse as urlparse
import os
import time

from threading import Thread
import logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)



host = '127.0.0.1'
port = '8080'
def get_remote_base():
    return 'http://{host}:{port}'.format(host=host, port=port)

def setup_background_server():
    def start_server(app):
        app.run(threaded=True, host=host, port=port)

    global server_thread
    server_thread = Thread(target=start_server,
                       args=(server.app))
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

needs_api_key = pytest.mark.skipif(os.environ.get('OPENAI_GYM_API_KEY') is None, reason="needs OPENAI_GYM_API_KEY")

# Tests ===============================================================================================================>

@with_server
def test_new_account():
    client = Client(get_remote_base())
    account_key, account_private = client.new_account()
    assert account_key in client.list_all_accounts()
    client.destroy_account(account_key)
    assert account_key not in client.list_all_accounts()





if __name__ == "__main__":
    unittest.main()