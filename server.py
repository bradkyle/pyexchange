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
from .error import Error, InvalidUsage
from .account.account import Account
from .exchange import Exchange
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

settings = exchange.settings

settings["public_rate_limit"] = ""
settings["private_rate_limit"] = ""
settings["default_initial_balance"] = 10000.00
settings["default_initial_status"] = "ACTIVE"


def auth_request():
    api_key = request.headers.get('X-APIKEY')
    payload = request.headers.get('X-PAYLOAD')
    signature = request.headers.get('X-SIGNATURE')

    if api_key is None or api_key not in exchange.accounts:
        raise Error('Cannot find account with public key: {}'.format(api_key))
    account = exchange.accounts[api_key]

    internal_signature = hmac.new(str.encode(account.private_key), payload, hashlib.sha384).hexdigest()
    if internal_signature != signature:
        raise Error('Wrong encoding.')

    payload = base64.b64decode(payload)

    return account, payload

def handle_request(f):
    @wraps(f)
    def _inner(*args, **kwargs):
        if auth_request():
            return
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

# @app.errorhandler(InvalidUsage)
# def handle_invalid_usage(error):
#     response = jsonify(error.to_dict())
#     response.status_code = error.status_code
#     return response


# Endpoints ===========================================================================================================>

# New Account Endpoint ------------------------------------------------------------------------------------------------>

@app.route('/v1/account/new', methods=['POST'])
def new_account():
    status = get_optional_param(request.get_json(), 'status', settings["default_initial_balance"])
    balances = get_optional_param(request.get_json(), 'starting_balances', settings["default_initial_status"])
    account_key = str(uuid.uuid4().hex)[:8]
    account_private = str(uuid.uuid4().hex)[:10]
    exchange.accounts[account_key] = Account(account_key, account_private, balances, status)
    return jsonify(account_key=account_key, account_private=account_private)


# Public Endpoints ---------------------------------------------------------------------------------------------------->

@app.route('/v1/lendbook/<asset_symbol>', methods=['GET'])
@limiter.limit(settings["public_rate_limit"])
def get_lendbook(asset_symbol):
    lendbook = exchange.return_lendbook(asset_symbol)
    return jsonify(asks=lendbook.asks(), bids=lendbook.bids())

@app.route('/v1/lendbook/all', methods=['GET'])
@limiter.limit(settings["public_rate_limit"])
def get_all_lendbooks():
    raise NotImplemented

@app.route('/v1/lends/<asset_symbol>', methods=['GET'])
@limiter.limit(settings["public_rate_limit"])
def get_lends(asset_symbol):
    lendbook = exchange.return_lendbook(asset_symbol)
    return jsonify(lends=lendbook.lends())

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
    return

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
def new_order(payload):
    symbol = get_required_param(payload, 'symbol')
    amount = get_required_param(payload, 'amount')
    price = get_required_param(payload, 'price')
    side = get_required_param(payload, 'side')

@app.route('/v1/order/new/multi', methods=['POST'])
@limiter.limit(settings["private_rate_limit"])
@handle_request
def multiple_new_orders(payload):
    raise NotImplemented

@app.route('/v1/order/cancel', methods=['POST'])
@limiter.limit(settings["private_rate_limit"])
@handle_request
def cancel_order(payload):
     return

@app.route('/v1/order/cancel/multi', methods=['POST'])
@limiter.limit(settings["private_rate_limit"])
@handle_request
def cancel_multiple_orders(payload):
     return

@app.route('/v1/order/<order_id>/cancel/session', methods=['POST'])
@limiter.limit(settings["private_rate_limit"])
@handle_request
def cancel_session_orders(payload):
    raise NotImplemented

@app.route('/v1/order/cancel/all', methods=['POST'])
@limiter.limit(settings["private_rate_limit"])
@handle_request
def cancel_all_orders(payload):
    return

@app.route('/v1/order/<order_id>/replace', methods=['POST'])
@limiter.limit(settings["private_rate_limit"])
@handle_request
def replace_order(payload):
    return

@app.route('/v1/order/cancel/session', methods=['POST'])
@limiter.limit(settings["private_rate_limit"])
@handle_request
def get_order_status(payload):
    return

@app.route('/v1/orders/active', methods=['POST'])
@limiter.limit(settings["private_rate_limit"])
@handle_request
def get_active_orders(payload):
    return

@app.route('/v1/orders', methods=['POST'])
@limiter.limit(settings["private_rate_limit"])
@handle_request
def get_order_history(payload):
    return

# Offering Endpoints -------------------------------------------------------------------------------------------------->

@app.route('/v1/offer/new', methods=['POST'])
@limiter.limit(settings["private_rate_limit"])
@handle_request
def new_offer():
    return

@app.route('/v1/offer/cancel', methods=['POST'])
@limiter.limit(settings["private_rate_limit"])
@handle_request
def cancel_offer():
    return

@app.route('/v1/offer/<offer_id>', methods=['POST'])
@limiter.limit(settings["private_rate_limit"])
@handle_request
def get_offer_status():
    return

@app.route('/v1/offer/all', methods=['POST'])
@limiter.limit(settings["private_rate_limit"])
@handle_request
def get_offer_history():
    return

# Positioning Endpoints ----------------------------------------------------------------------------------------------->

@app.route('/v1/position/all', methods=['POST'])
@limiter.limit(settings["private_rate_limit"])
@handle_request
def get_active_positions():
    return

@app.route('/v1/position/claim', methods=['POST'])
@limiter.limit(settings["private_rate_limit"])
@handle_request
def claim_positions():
    return

# Account Management Endpoints ---------------------------------------------------------------------------------------->

@app.route('/v1/account', methods=['POST'])
@limiter.limit(settings["private_rate_limit"])
@handle_request
def get_account_info():
    return

@app.route('/v1/account/fees', methods=['POST'])
@limiter.limit(settings["private_rate_limit"])
@handle_request
def get_account_fees():
    return

@app.route('/v1/account/summary', methods=['POST'])
@limiter.limit(settings["private_rate_limit"])
@handle_request
def get_account_summary():
    return

@app.route('/v1/account/margin', methods=['POST'])
@limiter.limit(settings["private_rate_limit"])
@handle_request
def get_margin_info():
    return

@app.route('/v1/account/balances', methods=['POST'])
@limiter.limit(settings["private_rate_limit"])
@handle_request
def get_balances():
    return

@app.route('/v1/account/balances/history', methods=['POST'])
@limiter.limit(settings["private_rate_limit"])
@handle_request
def get_balance_history():
    return

@app.route('/v1/account/depowith/history', methods=['POST'])
@limiter.limit(settings["private_rate_limit"])
@handle_request
def get_deposit_withdrawal_history():
    return

@app.route('/v1/account/deposit/history', methods=['POST'])
@limiter.limit(settings["private_rate_limit"])
@handle_request
def get_deposit_history():
    return

@app.route('/v1/account/withdraw/history', methods=['POST'])
@limiter.limit(settings["private_rate_limit"])
@handle_request
def get_withdrawal_history():
    return

@app.route('/v1/account/transfer/history', methods=['POST'])
@limiter.limit(settings["private_rate_limit"])
@handle_request
def get_transfer_history():
    return

@app.route('/v1/account/transfer', methods=['POST'])
@limiter.limit(settings["private_rate_limit"])
@handle_request
def transfer():
    return

@app.route('/v1/account/withdraw', methods=['POST'])
@limiter.limit(settings["private_rate_limit"])
@handle_request
def withdraw():
    return

@app.route('/v1/account/deposit', methods=['POST'])
@limiter.limit(settings["private_rate_limit"])
@handle_request
def deposit():
    return

@app.route('/v1/account/trades', methods=['POST'])
@limiter.limit(settings["private_rate_limit"])
@handle_request
def get_past_trades():
    return

@app.route('/v1/account/margin/trades', methods=['POST'])
@limiter.limit(settings["private_rate_limit"])
@handle_request
def get_margin_trades():
    return

@app.route('/v1/account/margin/active', methods=['POST'])
@limiter.limit(settings["private_rate_limit"])
@handle_request
def get_active_margin():
    return

@app.route('/v1/account/margin/inactive', methods=['POST'])
@limiter.limit(settings["private_rate_limit"])
@handle_request
def get_inactive_margin():
    return

@app.route('/v1/account/margin/close', methods=['POST'])
@limiter.limit(settings["private_rate_limit"])
@handle_request
def close_margin():
    return
