class Asset():
    def __init__(self, symbol, kind=None, name=None, fee=None, max_daily_withdrawal_limit=None):
        self.symbol = symbol
        self.name = name
        self.kind = kind
        self.transaction_fee = fee
        self.max_daily_withdrawal_limit = max_daily_withdrawal_limit
        self.enabled = True

    def details(self):
        return NotImplementedError


class Pair():
    def __init__(self,
                 symbol,
                 price_asset,
                 quantity_asset,
                 min_order_size,
                 min_order_inc,
                 min_price_inc,
                 ):
        self.symbol = symbol
        self.price_asset = price_asset
        self.quantity_asset = quantity_asset
        self.min_order_size = min_order_size
        self.min_order_inc = min_order_inc
        self.min_price_inc = min_price_inc
        self.enabled = True


    def high_detail(self):
        return NotImplementedError

    def mid_detail(self):
        return NotImplementedError

    def low_detail(self):
        return NotImplementedError
