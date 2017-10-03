class Asset():
    def __init__(self, asset_symbol, kind=None, name=None, fee=None, max_daily_withdrawal_limit=None):
        self.asset_symbol = asset_symbol
        self.name = name
        self.type = kind
        self.transaction_fee = fee
        self.max_daily_withdrawal_limit = max_daily_withdrawal_limit
        self.enabled = True

    def details(self):
        return NotImplementedError
