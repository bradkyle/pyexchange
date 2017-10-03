class MatchingEngine():

    def __new__(cls, *args, **kwargs):
        # We use __new__ since we want the core instance to be able to
        # override __init__ without having to call super.
        engine = super(MatchingEngine, cls).__new__(cls)
        return engine

    def match_order(self, order, current_orders, deferred_aons):
        if order.is_aon:
            return self._match_aon_order(order, current_orders, deferred_aons)

        elif order.is_post_only:
            return self._match_post_only_order(order, current_orders, deferred_aons)

        else:
            return self._match_regular_order(order, current_orders, deferred_aons)

    def _match_aon_order(self, order, current_orders, deferred_aons):
        raise NotImplementedError

    def _match_regular_order(self, order, current_orders, deferred_aons):
        raise NotImplementedError

    def _match_post_only_order(self, order, current_orders, deferred_aons):
        raise NotImplementedError

    def _negotiate(self):
        return NotImplemented


class FifoMatchingEngine(MatchingEngine):

    def _match_aon_order(self, order, current_orders, deferred_aons):
        return NotImplemented

    def _match_regular_order(self, order, current_orders, deferred_aons):
        return NotImplemented

    def _match_post_only_order(self, order, current_orders, deferred_aons):
        return NotImplemented


class ProRataMatchingEngine(MatchingEngine):

    def _match_aon_order(self, order, current_orders, deferred_aons):
        return NotImplemented

    def _match_regular_order(self, order, current_orders, deferred_aons):
        return NotImplemented

    def _match_post_only_order(self, order, current_orders, deferred_aons):
        return NotImplemented

