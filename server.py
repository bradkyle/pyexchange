import argparse
import base64
import hashlib
import hmac
import json
import uuid
from flask import Flask, request, jsonify
from functools import wraps
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from werkzeug.contrib.cache import SimpleCache
from error import Error, InvalidUsage
from exchange.exchange import Exchange
import logging
logger = logging.getLogger('werkzeug')
logger.setLevel(logging.ERROR)



# App Setup & Utilities ===============================================================================================>

app = Flask(__name__)
app.config['JSONIFY_PRETTYPRINT_REGULAR'] = False

limiter = Limiter(
    app,
    key_func=get_remote_address
)

cache = SimpleCache()

exchange = Exchange()

settings = {}

settings["public_rate_limit"] = ""
settings["private_rate_limit"] = ""
settings["default_initial_balance"] = 10000.00
settings["default_initial_status"] = "ACTIVE"


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

        print (request.url + " : " + str(request.remote_addr))

        api_key = request.headers.get('X-APIKEY')

        if api_key is None:
            raise Error('no api key provided')

        if api_key not in exchange.accounts:
             raise Error('Cannot find account with public key: {}'.format(api_key))

        account = exchange.accounts[api_key]

        payload = request.headers.get('X-PAYLOAD')
        signature = request.headers.get('X-SIGNATURE')

        if payload is not None:
                internal_signature = hmac.new(str.encode(account.private_key), str.encode(payload), hashlib.sha384).hexdigest()
                if internal_signature != signature:
                    raise Error('Wrong encoding.')
                payload = base64.b64decode(payload)

        kwargs['payload'] = payload
        kwargs['account'] = account

        return f(*args, **kwargs)
    return _inner

def get_required_param(json, param):
    if json is None:
        logger.info("Request is not a valid json")
        raise InvalidUsage("Request is not a valid json")
    value = json.get(param, None)
    if (value is None) or (value == '') or (value == []):
        logger.info("A required request parameter '{}' had value {}".format(param, value))
        raise InvalidUsage("A required request parameter '{}' was not provided".format(param))
    return value

def get_optional_param(json, param, default):
    if json is None:
        logger.info("Request is not a valid json")
        raise InvalidUsage("Request is not a valid json")
    value = json.get(param, None)
    if (value is None) or (value == '') or (value == []):
        logger.info(
            "An optional request parameter '{}' had value {} and was replaced with default value {}".format(param,
                                                                                                            value,
                                                                                                            default))
        value = default
    return value

def get_required_value(dict, key):
    return NotImplemented

def get_optional_value(dict, key, default):
    return NotImplemented

# @app.errorhandler(InvalidUsage)
# def handle_invalid_usage(error):
#     response = jsonify(error.to_dict())
#     response.status_code = error.status_code
#     return response


# Endpoints ===========================================================================================================>

# New Account Endpoint ------------------------------------------------------------------------------------------------>

@app.route('/v1/account/new', methods=['POST'])
def new_account():
    balances = get_optional_param(request.get_json(), 'starting_balances', settings["default_initial_balance"])
    status = get_optional_param(request.get_json(), 'status', settings["default_initial_status"])
    account_key, account_private = exchange.new_account(status, balances)
    return jsonify(account_key=account_key, account_private=account_private)

@app.route('/v1/accounts', methods=['GET'])
def get_all_accounts():
    all_accounts = exchange.return_all_accounts()
    return jsonify(all_accounts=all_accounts)

@app.route('/v1/account/<account_key>/destroy', methods=['POST'])
def destroy_account(account_key):
    exchange.destroy_account(account_key)
    return('', 204)

# Public Endpoints ---------------------------------------------------------------------------------------------------->

@app.route('/v1/offerbook/<asset_symbol>', methods=['GET'])
@limiter.limit(settings["public_rate_limit"])
def get_offerbook(asset_symbol):
    offerbook = exchange.return_offerbook(asset_symbol)
    return jsonify(asks=offerbook.asks(), bids=offerbook.bids())

@app.route('/v1/offerbook/all', methods=['GET'])
@limiter.limit(settings["public_rate_limit"])
def get_all_offerbooks():
    offerbooks = exchange.return_offerbooks()
    return jsonify(offerbooks=offerbooks)

@app.route('/v1/lends/<asset_symbol>', methods=['GET'])
@limiter.limit(settings["public_rate_limit"])
def get_lends(asset_symbol):
    offerbook = exchange.return_offerbook(asset_symbol)
    return jsonify(lends=offerbook.lends())

@app.route('/v1/lends/all', methods=['GET'])
@limiter.limit(settings["public_rate_limit"])
def get_all_lends():
    return

@app.route('/v1/orderbook/<symbol>', methods=['GET'])
@limiter.limit(settings["public_rate_limit"])
def get_orderbook(symbol):
    orderbook = exchange.return_orderbook(symbol)
    return jsonify(asks=orderbook.asks(), bids=orderbook.bids())

@app.route('/v1/orderbook/all', methods=['GET'])
@limiter.limit(settings["public_rate_limit"])
def get_all_orderbooks():
    orderbooks = exchange.return_orderbooks()
    return jsonify(orderbooks=orderbooks)

@app.route('/v1/trades/<symbol>', methods=['GET'])
@limiter.limit(settings["public_rate_limit"])
def get_trades(symbol):
    orderbook = exchange.return_orderbook(symbol)
    return jsonify(trades=orderbook.trades())

@app.route('/v1/trades/all', methods=['GET'])
@limiter.limit(settings["public_rate_limit"])
def get_all_trades():
    return

@app.route('/v1/stats/<symbol>', methods=['GET'])
@limiter.limit(settings["public_rate_limit"])
def get_stats(symbol):
    orderbook = exchange.return_orderbook(symbol)
    return jsonify(stats=orderbook.stats())

@app.route('/v1/stats/all', methods=['GET'])
@limiter.limit(settings["public_rate_limit"])
def get_all_stats():
    return

@app.route('/v1/ticker/<symbol>', methods=['GET'])
@limiter.limit(settings["public_rate_limit"])
def get_ticker(symbol):
    orderbook = exchange.return_orderbook(symbol)
    return jsonify(ticker=orderbook.tick())

@app.route('/v1/ticker/all', methods=['GET'])
@limiter.limit(settings["public_rate_limit"])
def get_all_tickers():
    return

@app.route('/v1/asset/<asset_symbol>', methods=['GET'])
@limiter.limit(settings["public_rate_limit"])
def get_asset(asset_symbol):
    asset = exchange.return_asset(asset_symbol)
    return jsonify(ticker=asset.details())

@app.route('/v1/asset/all', methods=['GET'])
@limiter.limit(settings["public_rate_limit"])
def get_all_assets():
    return

@app.route('/v1/pair/<symbol>', methods=['GET'])
@limiter.limit(settings["public_rate_limit"])
def get_pair(symbol):
    pair = exchange.return_pair(symbol)
    return jsonify(pair=pair.low_detail())

@app.route('/v1/pair/all', methods=['GET'])
@limiter.limit(settings["public_rate_limit"])
def get_all_pairs():
    return

@app.route('/v1/pair/<symbol>/detailed', methods=['GET'])
@limiter.limit(settings["public_rate_limit"])
def get_detailed_pair(symbol):
    pair = exchange.return_pair(symbol)
    return jsonify(pair=pair.high_detail())

@app.route('/v1/pair/all/detailed', methods=['GET'])
@limiter.limit(settings["public_rate_limit"])
def get_all_detailed_pairs(self):
    return

# Ordering Endpoints -------------------------------------------------------------------------------------------------->
@app.route('/v1/order/new', methods=['POST'])
@limiter.limit(settings["private_rate_limit"])
@handle_request
def new_order(payload, account):
    symbol = get_required_param(payload, 'symbol')
    price = get_required_param(payload, 'price')
    amount = get_required_param(payload, 'amount')
    side = get_required_param(payload, 'side')
    kind = get_required_param(payload, 'kind')
    is_hidden = get_optional_param(payload, 'is_hidden', False)
    is_postonly = get_optional_param(payload, 'is_postonly', False)
    use_all_available = get_optional_param(payload, 'use_all_available', False)
    ocorder = get_optional_param(payload, 'ocorder', False)
    buy_price_oco = get_optional_param(payload, 'ocorder', False)
    sell_price_oco = get_optional_param(payload, 'ocorder', False)

    order = exchange.new_order(account, symbol,price, amount, side, kind, is_hidden, is_postonly, use_all_available, ocorder, buy_price_oco, sell_price_oco)

    return jsonify(order.order_id)

@app.route('/v1/order/new/multi', methods=['POST'])
@limiter.limit(settings["private_rate_limit"])
@handle_request
def multiple_new_orders(payload, account):
    orders = get_required_param(payload, 'orders')
    order_ids = []
    for order in orders:
        symbol = get_required_value(order, 'symbol')
        price = get_required_value(order, 'price')
        amount = get_required_value(order, 'amount')
        side = get_required_value(order, 'side')
        kind = get_required_value(order, 'kind')
        is_hidden = get_optional_value(order, 'is_hidden', False)
        is_postonly = get_optional_value(order, 'is_postonly', False)
        use_all_available = get_optional_value(order, 'use_all_available', False)

        order = exchange.new_order(account, symbol, price, amount, side, kind, is_hidden, is_postonly, use_all_available)

        order_ids.append(order.order_id)

    return jsonify(order_ids=order_ids)

@app.route('/v1/order/cancel', methods=['POST'])
@limiter.limit(settings["private_rate_limit"])
@handle_request
def cancel_order(payload, account):
    order_id = get_required_param(payload, 'order_id')
    order = exchange.cancel_order(account, order_id)
    return jsonify(order_status=order.status())

@app.route('/v1/order/cancel/multi', methods=['POST'])
@limiter.limit(settings["private_rate_limit"])
@handle_request
def cancel_multiple_orders(payload, account):
    order_ids = get_required_param(payload, 'order_ids')
    order_statuses = []
    for order_id in order_ids:
        order = exchange.cancel_order(account,order_id)
        order_statuses.append(order.status())
    return jsonify(order_ids=order_ids)

@app.route('/v1/order/<order_id>/cancel/session', methods=['POST'])
@limiter.limit(settings["private_rate_limit"])
@handle_request
def cancel_session_orders(payload, account):
    raise NotImplemented

@app.route('/v1/order/cancel/all', methods=['POST'])
@limiter.limit(settings["private_rate_limit"])
@handle_request
def cancel_all_orders(payload, account):
    return

@app.route('/v1/order/<order_id>/replace', methods=['POST'])
@limiter.limit(settings["private_rate_limit"])
@handle_request
def replace_order(payload, account):
    return

@app.route('/v1/order/cancel/session', methods=['POST'])
@limiter.limit(settings["private_rate_limit"])
@handle_request
def get_order_status(payload, account):
    return

@app.route('/v1/orders/active', methods=['POST'])
@limiter.limit(settings["private_rate_limit"])
@handle_request
def get_active_orders(payload, account):
    return

@app.route('/v1/orders', methods=['POST'])
@limiter.limit(settings["private_rate_limit"])
@handle_request
def get_order_history(payload, account):
    return

# Offering Endpoints -------------------------------------------------------------------------------------------------->

@app.route('/v1/offer/new', methods=['POST'])
@limiter.limit(settings["private_rate_limit"])
@handle_request
def new_offer(payload, account):
    return

@app.route('/v1/offer/cancel', methods=['POST'])
@limiter.limit(settings["private_rate_limit"])
@handle_request
def cancel_offer(payload, account):
    return

@app.route('/v1/offer/<offer_id>', methods=['POST'])
@limiter.limit(settings["private_rate_limit"])
@handle_request
def get_offer_status(payload, account):
    return

@app.route('/v1/offer/all', methods=['POST'])
@limiter.limit(settings["private_rate_limit"])
@handle_request
def get_offer_history(payload, account):
    return

# Positioning Endpoints ----------------------------------------------------------------------------------------------->

@app.route('/v1/position/all', methods=['POST'])
@limiter.limit(settings["private_rate_limit"])
@handle_request
def get_active_positions(payload, account):
    return

@app.route('/v1/position/claim', methods=['POST'])
@limiter.limit(settings["private_rate_limit"])
@handle_request
def claim_positions(payload, account):
    return

# Account Management Endpoints ---------------------------------------------------------------------------------------->

@app.route('/v1/account', methods=['POST'])
@limiter.limit(settings["private_rate_limit"])
@handle_request
def get_account_info(payload, account):
    return

@app.route('/v1/account/fees', methods=['POST'])
@limiter.limit(settings["private_rate_limit"])
@handle_request
def get_account_fees(payload, account):
    return

@app.route('/v1/account/summary', methods=['POST'])
@limiter.limit(settings["private_rate_limit"])
@handle_request
def get_account_summary(payload, account):
    return

@app.route('/v1/account/margin', methods=['POST'])
@limiter.limit(settings["private_rate_limit"])
@handle_request
def get_margin_info(payload, account):
    return

@app.route('/v1/account/balances', methods=['POST'])
@limiter.limit(settings["private_rate_limit"])
@handle_request
def get_balances(payload, account):
    return

@app.route('/v1/account/balances/history', methods=['POST'])
@limiter.limit(settings["private_rate_limit"])
@handle_request
def get_balance_history(payload, account):
    return

@app.route('/v1/account/depowith/history', methods=['POST'])
@limiter.limit(settings["private_rate_limit"])
@handle_request
def get_deposit_withdrawal_history(payload, account):
    return

@app.route('/v1/account/deposit/history', methods=['POST'])
@limiter.limit(settings["private_rate_limit"])
@handle_request
def get_deposit_history(payload, account):
    return

@app.route('/v1/account/withdraw/history', methods=['POST'])
@limiter.limit(settings["private_rate_limit"])
@handle_request
def get_withdrawal_history(payload, account):
    return

@app.route('/v1/account/transfer/history', methods=['POST'])
@limiter.limit(settings["private_rate_limit"])
@handle_request
def get_transfer_history(payload, account):
    return

@app.route('/v1/account/transfer', methods=['POST'])
@limiter.limit(settings["private_rate_limit"])
@handle_request
def transfer(payload, account):
    return

@app.route('/v1/account/withdraw', methods=['POST'])
@limiter.limit(settings["private_rate_limit"])
@handle_request
def withdraw(payload, account):
    return

@app.route('/v1/account/deposit', methods=['POST'])
@limiter.limit(settings["private_rate_limit"])
@handle_request
def deposit(payload, account):
    return

@app.route('/v1/account/trades', methods=['POST'])
@limiter.limit(settings["private_rate_limit"])
@handle_request
def get_past_trades(payload, account):
    return

@app.route('/v1/account/margin/trades', methods=['POST'])
@limiter.limit(settings["private_rate_limit"])
@handle_request
def get_margin_trades(payload, account):
    return

@app.route('/v1/account/margin/active', methods=['POST'])
@limiter.limit(settings["private_rate_limit"])
@handle_request
def get_active_margin(payload, account):
    return

@app.route('/v1/account/margin/inactive', methods=['POST'])
@limiter.limit(settings["private_rate_limit"])
@handle_request
def get_inactive_margin(payload, account):
    return

@app.route('/v1/account/margin/close', methods=['POST'])
@limiter.limit(settings["private_rate_limit"])
@handle_request
def close_margin(payload, account):
    return

# Utilities and Debug =================================================================================================>

@app.route('/v1/shutdown/', methods=['POST'])
def shutdown():
    """
    Request a server shutdown - currently used by the
    integration tests to repeatedly create and destroy
    fresh copies of the server running in a separate thread
    """
    f = request.environ.get('werkzeug.server.shutdown')
    f()
    return 'Server shutting down'

@app.route('/v1/authenticate', methods=['POST'])
@handle_request
def authenticate(payload, account):
    """
    Authenticate request - currently used by the
    integration tests to test functionality of
    request handler and the the authentication
    therin
    """

    return jsonify(test_response=payload.decode('utf-8'))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Start pyexchange API server')
    parser.add_argument('-l', '--listen', help='interface to listen to', default='127.0.0.1')
    parser.add_argument('-p', '--port', default=5000, type=int, help='port to bind to')

    args = parser.parse_args()
    print('Server starting at: ' + 'http://{}:{}'.format(args.listen, args.port))
    app.run(host=args.listen, port=args.port)
