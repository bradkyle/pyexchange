class Pair():
    def __init__(self,
                 symbol,
                 price_asset,
                 quantity_asset,
                 min_order_inc,
                 min_price_inc,
                 min_order_price = 0.0,
                 min_order_size = 0.0,
                 id = None
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
