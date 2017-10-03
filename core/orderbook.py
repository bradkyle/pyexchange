from collections import deque
from .engine import *
from .ticker import Ticker

class OrderQuantityTooSmall(Exception):pass
class OrderNotFound(Exception):pass
class OrderAlreadyFilled(Exception):pass


class OrderRegistry():
    def __init__(self):
        self.orders = {}

    def make(self, order):
        class Tracker():
            def __init__(self):
                raise NotImplementedError

    def find(self, order_id):
        return NotImplementedError



orderRegistry = OrderRegistry()

def get_order(order_id):
    raise NotImplementedError

def find_order():
    raise NotImplementedError

def new_order(symbol, amount, price, side, **kwargs):
    raise NotImplementedError

def cancel_order(order_id):
    raise NotImplementedError

def cancel_multiple_orders(order_ids):
    raise NotImplementedError

def replace_order(old_order_id , symbol, amount, price, side, **kwargs):
    raise NotImplementedError


class Orderbook(object):


    def __init__(self, pair, engine_type="fifo"):
        self.pair = pair

        self.engine_type = engine_type
        self.bids = Queue()
        self.asks = Queue()
        self.stop_bids = Queue()
        self.stop_asks = Queue()
        self.pending_orders = Queue()

        self.ticker = Ticker()

    def get_orderbook(self):
        return NotImplementedError


    def new_order(self, _order):
        rmatched = False

        #todo should this be 0 ?
        if _order.quantity < _order.pair.min_order_size:
            self._reject(_order, OrderQuantityTooSmall)
            return

        else:
            if _order.stop_price != 0.0:
                self._add_stop_order(_order)
            else:
                self._accept()
                matched = self._add_order(_order)
                if _order.is_ioc and not _order.is_filled:
                    self.cancel_order(_order)

            while not self.pending_orders.empty:
                self._add_pending_orders()

            self._update()
        return matched


    def cancel_order(self, order):

        if self._find_on_market(order):
            if order.is_buy:
                self.bids.erase(order)
                found = True
            else:
                self.asks.erase(order)
                found = True

            self._update()
        else:
            self._cancel_reject(order, OrderNotFound)

    def replace(self, order, size_delta, new_price):
        matched = False
        change_price = (order.price != new_price)

        if self._find_on_market(order):

            # If there is not enough open quantity for the size reduction
            if size_delta < 0.0 and (order.open_qty < -size_delta):
                size_delta = -order.open_qty
                if size_delta == 0.0:
                    self._replace_reject(order,OrderAlreadyFilled)
                    return False

            new_open_qty = order.open_qty + size_delta

            # If the size change will close the order
            if not new_open_qty:
                self.cancel_order(order)
            else:
                self.cancel_order(order)
                matched = self._add_order(order)

            while not self.pending_orders.empty:
                self._add_pending_orders()

            self._update()

        else:
            self._replace_reject(order,OrderNotFound)

        return matched

    def _add_order(self, order):
        matched = False
        deferred_aons = []

        if order.is_buy:
            matched = self._match_order(order, self.asks, deferred_aons)
        else:
            matched = self._match_order(order, self.asks, deferred_aons)

        if not order.is_filled and not order.is_ioc:
            if order.is_buy:
                self.bids.insert(order)
                if self._check_deferred_aons(deferred_aons, self.asks, self.bids):
                    matched = True
            else:
                self.asks.insert(order)
                if self._check_deferred_aons(deferred_aons, self.asks, self.bids):
                    matched = True

        return matched

    def _add_stop_order(self, order):
        # if the market price is a better deal then the stop price,
        # it's not time to panic
        stopped = order.stop_price < self.market_price
        if stopped:
            if order.is_buy:
                self.stop_bids.insert(order)
            else:
                self.stop_asks.insert(order)
        return stopped

    def _add_trailing_stop_order(self):
        return NotImplemented

    def _match_order(self, order, current_orders, deferred_aons):
        self.engine.match_order(order, current_orders, deferred_aons)

    def _check_stop_orders(self, price, stop_queue):
        for stop_order in stop_queue:
            if price > stop_order.stop_price:
                stop_queue.erase(stop_order)
            else:
                break

    def _check_deferred_aons(self, aons, asks, bids):
        result = False
        for aon_order in aons:
            matched = self._match_order(aon_order, asks, bids)
            result += matched
            if aon_order.is_filled:
                #todo erase from queue
                raise NotImplementedError

    def _add_pending_orders(self):
        for order in self.pending_orders.queue:
            return self._add_order(order)

    #todo this will be used for fast searches
    def _find_on_market(self, order):
        return NotImplementedError

    def _update(self):
        return NotImplemented

    def _reject(self, order, error):
        return NotImplemented

    def _cancel_reject(self, order, error):
        return NotImplemented

    def _replace_reject(self, order, error):
        return NotImplemented

    def _accept(self):
        return NotImplemented

    @property
    def engine(self):
        if self.engine_type == "fifo":
            return FifoMatchingEngine()
        if self.engine_type == "prorata":
            return ProRataMatchingEngine()
        else:
            return FifoMatchingEngine()

    @property
    def market_price(self):
        return NotImplemented



    def asks(self):
        return NotImplementedError

    def bids(self):
        return NotImplementedError

    def trades(self):
        return NotImplementedError

    def tick(self):
        return NotImplementedError

    def stats(self):
        return NotImplementedError



class Queue():
    def __init__(self):
        self.queue = deque()

    def insert(self, order):
        return NotImplemented

    def erase(self, order):
        return NotImplemented

    @property
    def empty(self):
        return NotImplemented


