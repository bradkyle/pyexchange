import uuid
from orderbook.orderbook import Orderbook
from offerbook.offerbook import Offerbook
from asset.asset import Asset
from account.account import Account
from asset.pair import Pair
from error import Error


class Exchange():
    def __init__(self):
        self.assets = {}
        self.pairs = {}
        self.orderbooks = {}
        self.offerbooks = {}
        self.accounts = {}
        self.fees = {}
        self.sessions = {}
        self.load()

    # Functionality ===================================================================================================>

    # Accounts -------------------------------------------------------------------------------------------------------->

    def new_account(self, status, balances):
        account_key = str(uuid.uuid4().hex)[:8]
        account_private = str(uuid.uuid4().hex)[:10]
        self.accounts[account_key] = Account(account_key, account_private, balances, status)
        return account_key, account_private

    def return_all_accounts(self):
        return dict([(account_key, account.balances) for (account_key, account) in self.accounts.items()])

    def destroy_account(self, account_key):
        del self.accounts[account_key]
        return

    # Assets & Pairs -------------------------------------------------------------------------------------------------->

    def new_asset(self, asset_symbol, **kwargs):
        if asset_symbol in self.assets:
            raise Error('Cannot re-register asset with symbol: {}'.format(asset_symbol))
        self.assets[asset_symbol] = Asset(asset_symbol, **kwargs)

    def return_asset(self, asset_symbol):
        if asset_symbol not in self.assets:
            raise Error('Cannot find asset with symbol: {}'.format(asset_symbol))
        asset = self.assets[asset_symbol]
        return asset

    def disable_asset(self):
        return NotImplemented

    def return_all_assets(self):
        return dict([(account_key, account.balances) for (account_key, account) in self.assets.items()])

    def new_pair(self, symbol, **kwargs):
        if symbol in self.pairs:
            raise Error('Cannot re-register pair with symbol: {}'.format(symbol))
        self.orderbooks[symbol] = Pair(symbol, **kwargs)

    def disable_pair(self):
        return NotImplemented

    def return_pair(self, symbol):
        if symbol not in self.pairs:
            raise Error('Cannot find pair with symbol: {}'.format(symbol))
        pair = self.pairs[symbol]
        return pair

    # Offering & Lends ------------------------------------------------------------------------------------------------>

    def new_offerbook(self, asset_symbol):
        asset = self.return_asset(asset_symbol)
        if asset in self.offerbooks:
            raise Error('Cannot re-register offerbook for asset with symbol: {}'.format(asset_symbol))
        self.offerbooks[asset_symbol] = Offerbook(asset)

    def return_offerbook(self, asset_symbol):
        asset = self.return_asset(asset_symbol)
        if asset not in self.offerbooks:
            raise Error('Cannot find offerbook for asset with symbol: {}'.format(asset_symbol))
        return self.offerbooks[asset]

    def new_offer(self):
        return NotImplemented

    def cancel_offer(self):
        return NotImplemented

    def return_offer(self):
        return NotImplemented

    # Ordering & Trades ----------------------------------------------------------------------------------------------->

    def new_orderbook(self, symbol, **kwargs):
        pair = self.return_pair(symbol)
        if pair in self.orderbooks:
            raise Error('Cannot re-register orderbook for pair with symbol: {}'.format(symbol))
        self.orderbooks[symbol] = Orderbook(pair, **kwargs)

    def return_orderbook(self, symbol):
        pair = self.return_pair(symbol)
        if pair not in self.orderbooks:
            raise Error('Cannot find orderbook for pair with symbol: {}'.format(symbol))
        return self.orderbooks[pair]

    def new_order(self):
        return NotImplemented

    def cancel_order(self):
        return NotImplemented

    def replace_order(self):
        return NotImplemented

    def return_order(self):
        return NotImplemented


    # Setup & Utilities ----------------------------------------------------------------------------------------------->

    def load(self):
        return

    def reload(self):
        return

    def setup(self):
        return

    def start(self):
        return
