def auth_request():
    api_key = request.headers.get('X-APIKEY')

    if api_key is None or api_key not in exchange.accounts:
        raise Error('Cannot find account with public key: {}'.format(api_key))
    account = exchange.accounts[api_key]

    # payload = request.headers.get('X-PAYLOAD')
    # signature = request.headers.get('X-SIGNATURE')
    # if payload is not None:
    #     internal_signature = hmac.new(str.encode(account.private_key), payload, hashlib.sha384).hexdigest()
    #     if internal_signature != signature:
    #         raise Error('Wrong encoding.')
    #     payload = base64.b64decode(payload)

    return account

def handle_request(f):
    @wraps(f)
    def _inner(*args, **kwargs):
        account = auth_request()
        kwargs['account'] = account
        # kwargs['payload'] = payload
        return f(*args, **kwargs)
    return _inner
