class Orderbook():
    def __init__(self, pair, engine_type="fifo"):
        self.pair = pair
        self.engine_type = engine_type
        self.engine = None

        self.ticker = {}

        self.bids = {}
        self.asks = {}
        self.stop_bids = {}
        self.stop_asks = {}
        self.pending_orders = {}


    # Stats & Asks/Bids ------------------------------------------------------------------------------------------->

    def get_asks(self):
        return NotImplemented

    def get_bids(self):
        return NotImplemented

    def get_trades(self):
        return NotImplemented

    def get_stats(self):
        return NotImplemented

    @property
    def market_price(self):
        raise NotImplemented

    # Ticker & Asks/Bids ----------------------------------------------------------------------------------------------->

    def tick(self):
        self.open_price = 0
        self.close_price = 0
        self.last_price = 0
        self.mid_price = 0
        self.low_price = 0
        self.high_price = 0
        self.lowest_ask = 0
        self.lowest_ask_size = 0
        self.highest_ask = 0
        self.highest_ask_size = 0
        self.lowest_bid = 0
        self.lowest_bid_size = 0
        self.highest_bid = 0
        self.highest_bid_size = 0
        self.total_ask_depth = 0
        self.total_bid_depth = 0
        self.day_volume = 0
        self.week_volume = 0
        self.month_volume = 0
        self.volume_weighted_average_price = 0
        self.volume_base = 0
        self.volume_quote = 0
        self.number_of_trades = 0

    def get_ticker(self):
        return NotImplemented


    # Ordering Functionality ------------------------------------------------------------------------------------------>

    def new_order(self, order):
        matched = False
        if order.open_qty < order.pair.min_order_size:
            return NotImplemented
        elif order.open_qty is not None:
            return NotImplemented
        else:
            if order.stop_price is not None:
                self._add_stop_order(order)
            else:
                matched = self._add_order(order)
                if order.is_ioc and not order.is_filled:
                    self.cancel_order(order)

            while not len(self.pending_orders) == 0:
                self._add_pending_orders()

            self._publish()
        return matched

    def _add_order(self, order):
        matched = False
        deferred_aons = []

        if order.is_buy:
            matched = self._match_order(order, self.asks, deferred_aons)
        else:
            matched = self._match_order(order, self.bids, deferred_aons)

        if not order.is_filled and not order.is_ioc:
            if order.is_buy:
                self._insert(order, self.bids)
                if self._check_deferred_aons(deferred_aons):
                    matched = True
            else:
                self._insert(order, self.asks)
                if self._check_deferred_aons(deferred_aons):
                    matched = True
        return matched

    def _add_stop_order(self,order):
        stopped = order.stop_price < self.market_price
        if stopped:
            if order.is_buy:
                self._insert(order, self.bids)
            else:
                self._insert(order, self.asks)


    def cancel_order(self, order):
        if self._find_on_market(order):
            if order.is_buy:
                self._erase(order, self.bids)
            else:
                self._erase(order, self.asks)
            self._publish()
        else:
            return NotImplemented

    def replace_order(self, order, new_order):
        matched = False
        if self._find_on_market(order):
            size_delta = order.open_qty - new_order.open_qty


        else:
            return NotImplemented

    def _find_on_market(self, order):
        raise NotImplemented

    def _publish(self):
        return NotImplemented

    def _insert(self, order, queue):
        return NotImplemented

    def _erase(self, order, queue):
        return NotImplemented

    # Matching Functionality ------------------------------------------------------------------------------------------>

    def _check_stop_orders(self):
        raise NotImplemented

    def _check_deferred_aons(self, deferred_aons):
        raise NotImplemented

    def _add_pending_orders(self):
        raise NotImplemented


    # Matching Engines ------------------------------------------------------------------------------------------------>

    def _match_order(self, order, queue, deferred_aons):
        matched = False
        deferred_qty = 0
        deferred_matches = []
        if not order.is_filled:
            for current_order in queue:

                # todo check if current order matches order price
                if not order.is_post_only:
                    if not order.is_aon:
                        if current_order.is_aon:
                            if current_order.open_qty <= order.open_qty:
                                trade = self._create_trade(order, current_order)
                                if trade.qty > 0:
                                    matched = True
                                    self._erase(current_order, queue)
                                    order.open_qty -= trade.qty
                            else:
                                self._push_back(deferred_aons, current_order)
                        else:
                            trade = self._create_trade(order, current_order)
                            if trade.qty > 0:
                                matched = True
                                if current_order.is_filled:
                                    self._erase(current_order, queue)
                                order.open_qty -= trade.qty
                    else:
                        if current_order.is_aon:
                            # if the inbound order can satisfy the
                            # current order's AON condition
                            if current_order.open_qty <= order.open_qty:
                                # if the the matched quantity can satisfy
                                # the inbound order's AON condition
                                if order.open_qty <= current_order.open_qty + deferred_qty:
                                    max_qty = order.open_qty - current_order.open_qty
                                    traded = self._try_create_deferred_trades()
                                    if max_qty == traded:
                                        order.open_qty -= max_qty
                                        trade = self._create_trade(order, current_order)
                                        if trade.qty > 0:
                                            order.open_qty -= trade.qty
                                            matched = True
                                            self._erase(queue, current_order)
                                else:
                                    deferred_qty += current_order.open_qty
                                    self._push_back(deferred_aons, queue)
                            else:
                                self._push_back(deferred_aons, current_order)
                        else:
                            if order.open_qty <= current_order.open_qty + deferred_qty:
                                traded = self._try_create_deferred_trades()
                                if order.qty <= current_order.open_qty + traded:
                                    trade = self._create_trade(order, current_order)
                                    traded += trade.qty
                                    if traded > 0:
                                        order.open_qty -= traded
                                        matched = True
                                    if current_order.is_filled:
                                        self._erase(current_order, queue)
                            else:
                                deferred_qty += current_order.open_qty
                                self._push_back(deferred_matches, current_order)
                else:
                    self.cancel_order(order)
        return matched

    def negotiate(self, b, s):
        if b.is_market and s.is_limit:
            print("o.lastPrice = s.price()")
        elif b.is_limit and s.is_market:
            print("o.lastPrice = b.price()")
        elif b.is_limit and s.is_limit:
            print("o.lastPrice = s.price()")
        else:
            print("o.lastPrice")

    def _create_trade(self, inbound, current):
        return NotImplemented

    def _try_create_deferred_trades(self, inbound, deferred_matches, max_qty, min_qty, current_orders):
        traded = 0


        return traded

    def _push_back(self, queue, order):
        return NotImplemented


    # ProRata