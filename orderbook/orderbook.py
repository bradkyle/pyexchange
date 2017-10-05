import time

import itertools
from error import Error

class Orderbook():
    def __init__(self, pair, init_market_price, engine_type="fifo"):
        self.pair = pair
        self.engine_type = engine_type
        self.market_price = init_market_price
        self.max_trade_size = 0

        self.orders = {}
        self.trades = {}

        self.bids = {}
        self.asks = {}
        self.stop_bids = {}
        self.stop_asks = {}
        self.pending_orders = {}
        self.deferred_aons = []

        self._set_market_price(init_market_price)

    # Config ---------------------------------------------------------------------------------------------------------->

    @property
    def is_fifo(self):
        if self.engine_type == "fifo":
            return True
        return False

    @property
    def is_prorata(self):
        if self.engine_type == "prorata":
            return True
        return False

    @property
    def is_random(self):
        if self.engine_type == "random":
            return True
        return False

    # Stats & Asks/Bids ----------------------------------------------------------------------------------------------->

    def get_asks(self):
        return NotImplemented

    def get_bids(self):
        return NotImplemented

    def get_trades(self):
        return NotImplemented

    def get_stats(self):
        return NotImplemented

    # Ticker & Asks/Bids ----------------------------------------------------------------------------------------------->

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

            if order.order_id in self.orders:
                raise Error('Cannot add another order with id: {}'.format(order.order_id))

            self.orders[order.order_id] = order

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
        if order.is_buy:
            matched = self._match_order(order, self.asks)
        else:
            matched = self._match_order(order, self.bids)

        if not order.is_filled and not order.is_ioc:
            if order.is_buy:
                self._insert(order, self.stop_bids)
                if self._check_deferred_aons(self.bids):
                    matched = True
            else:
                self._insert(order, self.stop_asks)
                if self._check_deferred_aons(self.asks):
                    matched = True
        return matched

    def _add_stop_order(self,order):
        stopped = order.stop_price < self.market_price
        if stopped:
            if order.is_buy:
                self._insert(order, self.bids)
            else:
                self._insert(order, self.asks)

    def cancel_order(self, order_id):
        order = self._find_on_market(order_id)
        if order.is_buy:
            self._erase(order, self.bids)
        else:
            self._erase(order, self.asks)
        self._publish()

    def replace_order(self, order_id, new_order):
        matched = False
        order = self._find_on_market(order_id)
        size_delta = order.open_qty - new_order.open_qty

    def return_order(self, order_id):
        order = self._find_on_market(order_id)
        return order

    def _find_on_market(self, order_id):
        if order_id not in self.orders:
            raise Error('Cannot find order with id: {}'.format(order_id))
        order = self.orders[order_id]
        return order

    def _set_market_price(self, price):
        old_market_price = self.market_price
        self.market_price = price
        if price > old_market_price:
            self._check_stop_orders(self.stop_bids, price)
        elif price < old_market_price:
            self._check_stop_orders(self.stop_asks, price)

    # Indexing Functionality ------------------------------------------------------------------------------------------>

    def _publish(self):
        """
        updates the ticker metrics
        """
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

    def _arrange(self, queue):
        return sorted(queue.iterkeys())

    def _insert(self, order, queue):
        if self.is_fifo:
                index = order.time_created * order.price
                queue[index] = order
        return queue

    def _erase(self, order, queue):
        del queue[order.order_id]

    # Checking Functionality ------------------------------------------------------------------------------------------>

    def _check_stop_orders(self, queue, price):
        for stop_order in queue:
            if price > stop_order.stop_price:
                self._push_back(self.pending_orders, stop_order)
                self._erase(stop_order, queue)

    def _check_deferred_aons(self, queue):
        result = False
        for aon in self.deferred_aons:
            matched = self._match_order(aon, queue)
            result += matched
            if aon.is_filled:
                self._erase(aon, self.deferred_aons)
        return result

    def _add_pending_orders(self):
        for order in self.pending_orders:
            self.new_order(order)

    # Matching Engines ------------------------------------------------------------------------------------------------>

    def _match_order(self, order, queue):
        matched = False
        deferred_qty = 0
        deferred_matches = []
        if not order.is_filled and order.is_active:
            for current_order in self._arrange(queue).keys():

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
                                self._push_back(self.deferred_aons, current_order)
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
                                    self._push_back(self.deferred_aons, queue)
                            else:
                                self._push_back(self.deferred_aons, current_order)
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

    def _try_create_deferred_trades(self, inbound, deferred_matches, max_qty, min_qty, current_orders):
        traded = 0
        found_qty = 0
        fills = {}
        index = 0

        for deferred_match in deferred_matches:
            index += 1
            if found_qty < max_qty:
                qty = inbound.open_qty

                if found_qty + qty > max_qty:
                    if inbound.is_aon:
                        qty = 0
                    else:
                        qty = max_qty - found_qty
                found_qty += qty
                fills[index] = qty

        if min_qty <= found_qty <= max_qty:
            for deferred_match in deferred_matches:
                if traded < found_qty:
                    traded += self._create_trade(inbound, )

        return traded

    def _negotiate(self, inbound, current):
        if inbound.is_market and current.is_limit:
            price = current.price
        elif current.is_market and inbound.is_limit:
            price = inbound.price
        elif current.is_limit and inbound.is_limit:
            price = current.price
        else:
            price = self.market_price
        """
            market_order_price = 0

        if market_order_price == cross_price:
            cross_price = inbound.price
        if market_order_price == cross_price:
            cross_price = self.market_price
        if market_order_price == cross_price:
            return 0
        """
        return price

    def _create_trade(self, inbound, current,  max_quantity= None):
        price = self.negotiate(inbound, current)
        if max_quantity is None:
                max_quantity = self.max_trade_size
        fill_qty = min(max_quantity, min(inbound.open_qty, current.open_qty))
        self._fill(inbound, fill_qty, price)
        self._fill(current, fill_qty, price)
        self._set_market_price(price)

    def _fill(self, order, qty, price):
        class Trade():
            newid = itertools.count().next
            def __init__(self, price, amount, side, actor, kind, pair):
                self.id = Trade.newid()
                self.time_created = time.time()
                self.price = price
                self.amount = amount
                self.side = side
                self.actor = actor
                self.kind = kind
                self.pair = pair

            def anonomised(self):
                raise NotImplemented


        if qty > order.open_qty:
            raise Error("")

        trade = Trade(price, qty, order.side, order.account, order.kind, order.pair)
        self.trades[trade.id] = trade
        order.open_qty -= qty
        self._handle_trade(trade)

    def _handle_trade(self, trade):
        return NotImplemented

    def _push_back(self, queue, order):
        return NotImplemented

class Queue():
    def __init__(self):
        raise NotImplemented