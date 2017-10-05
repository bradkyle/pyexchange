import pytest
from .orderbook import Orderbook
from exchange.asset.asset import Pair, Asset

test_price_asset = Asset(symbol="BTC", name="Bitcoin", kind="crypto")
test_quantity_asset = Asset(symbol="USD", name="US Dollar", kind="fiat")
test_pair = Pair(symbol="USDBTC", price_asset=test_price_asset, quantity_asset=test_quantity_asset, min_order_size=0.00000001, min_order_inc=0.01, min_price_inc=0.00001)

def test_tick():
    return NotImplemented

def test_new_order():
    return NotImplemented

def test_add_order():
    return NotImplemented

def test_add_stop_order():
    return NotImplemented

def test_cancel_order():
    return NotImplemented

def test_replace_order():
    return NotImplemented