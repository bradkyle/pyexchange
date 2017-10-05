class Offer():
    def __init__(self, asset, amount, rate, period, side):
        self.asset = asset
        self.amount = amount
        self.rate = rate
        self.period = period
        self.side = side

    @property
    def is_lend(self):
        return NotImplemented

    @property
    def is_loan(self):
        return NotImplemented