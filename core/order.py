import time

import itertools




class Order(object):



    def __init__(self,
                 order_id,
                 pair,
                 account,
                 quantity,
                 price,
                 kind,
                 side,
                 exec_option,
                 is_hidden = False,
                 is_post_only = False,
                 expires_at = None,
                 stop_price = 0.0,
                 trailing_stop = 0.0,
                 ):

        self.order_id = order_id
        self.pair = pair
        self.account = account
        self.quantity = quantity
        self.price = price
        self.kind = kind
        self.side = side
        self.exec_option = exec_option
        self.is_hidden = is_hidden
        self.is_post_only = is_post_only
        self.expires_at = expires_at
        self.time_closed = None
        self.time_filled = None
        self.time_stopped = None
        self.stop_price = stop_price
        self.stop_hit = False
        self.trailing_stop = trailing_stop
        self.open_price = price
        self.close_price = 0.0
        self.time_created = time.time()

    @property
    def index(self):
        return NotImplemented

    @property
    def is_filled(self):
        return NotImplemented

    @property
    def is_active(self):
        return NotImplemented

    @property
    def is_ioc(self):
        return NotImplemented

    @property
    def is_aon(self):
        return NotImplemented

    @property
    def is_stop(self):
        return NotImplemented

    @property
    def is_trailing_stop(self):
        return NotImplemented

    @property
    def is_closed(self):
        return NotImplemented

    @property
    def has_expired(self):
        return NotImplemented

    @property
    def base_asset(self):
        return NotImplemented

    @property
    def quote_asset(self):
        return NotImplemented

    @property
    def open_qty(self):
        return NotImplemented

    @property
    def is_buy(self):
        return NotImplemented

    @property
    def is_sell(self):
        return NotImplemented

