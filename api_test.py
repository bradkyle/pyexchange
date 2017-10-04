import base64
import hashlib
import hmac
import json

import requests
import six.moves.urllib.parse as urlparse
import os
import time
import pytest
from threading import Thread
import server
import client as exchange_client
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
                       args=(server.app,))
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
def test_create_list_destroy_account():
    client = exchange_client.Client(get_remote_base())
    account_key, account_private = client.new_account()
    assert account_key in client.list_all_accounts()
    client.destroy_account(account_key)
    assert account_key not in client.list_all_accounts()


@with_server
def test_auth_request():
    client = exchange_client.Client(get_remote_base())
    account_key, account_private = client.new_account()

    payload = {'test': "test"}

    payload_encoded = str.encode(json.dumps(payload))
    b64 = base64.b64encode(payload_encoded)

    signature = hmac.new(str.encode(account_private), b64, hashlib.sha384).hexdigest()

    client.add_header('X-APIKEY', account_key)
    client.add_header('X-PAYLOAD', b64)
    client.add_header('X-SIGNATURE', signature)

    payload_out = client.authenticate(payload)
    payload_out = json.loads(payload_out)

    print(payload['test'])
    print("-------------------------------")
    print(payload_out['test'])

    assert payload['test'] == payload_out['test']


@with_server
def test_bad_auth_request_token():
    with pytest.raises(Exception):
        client = exchange_client.Client(get_remote_base())
        account_key, account_private = client.new_account()

        payload = {'test': "test"}

        payload_encoded = str.encode(json.dumps(payload))
        b64 = base64.b64encode(payload_encoded)

        signature = hmac.new(str.encode("bad"), b64, hashlib.sha384).hexdigest()

        client.add_header('X-APIKEY', account_key)
        client.add_header('X-PAYLOAD', b64)
        client.add_header('X-SIGNATURE', signature)

        payload_out = client.authenticate(payload)
        payload_out = json.loads(payload_out)

        print(payload['test'])
        print("-------------------------------")
        print(payload_out['test'])

        assert payload['test'] != payload_out['test']