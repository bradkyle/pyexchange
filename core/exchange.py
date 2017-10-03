import uuid

from exchange.core.orderbook import Orderbook
from exchange.core.lendbook import Lendbook
from exchange.asset.asset import Asset
from exchange.account.account import Account
from exchange.asset.pair import Pair
from exchange.error import Error





class Exchange():
    def __init__(self):
        self.assets = {}
        self.pairs = {}
        self.orderbooks = {}
        self.lendbooks = {}
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

    def return_all_accounts(self):
        return dict([(instance_id, env.spec.id) for (instance_id, env) in self.envs.items()])

    def destroy_account(self, account_key):
        del self.accounts[account_key]

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

    def return_all_assets(self):
        return dict([(instance_id, env.spec.id) for (instance_id, env) in self.envs.items()])

    def new_pair(self, symbol, **kwargs):
        if symbol in self.pairs:
            raise Error('Cannot re-register pair with symbol: {}'.format(symbol))
        self.orderbooks[symbol] = Pair(symbol, **kwargs)

    def return_pair(self, symbol):
        if symbol not in self.pairs:
            raise Error('Cannot find pair with symbol: {}'.format(symbol))
        pair = self.pairs[symbol]
        return pair

    # Funding & Lends ------------------------------------------------------------------------------------------------->

    def new_lendbook(self, asset_symbol):
        asset = self.return_asset(asset_symbol)
        if asset in self.lendbooks:
            raise Error('Cannot re-register lendbook for asset with symbol: {}'.format(asset_symbol))
        self.lendbooks[asset_symbol] = Lendbook(asset)

    def return_lendbook(self, asset_symbol):
        asset = self.return_asset(asset_symbol)
        if asset not in self.lendbooks:
            raise Error('Cannot find lendbook for asset with symbol: {}'.format(asset_symbol))
        return self.lendbooks[asset]

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

    # Setup & Utilities ----------------------------------------------------------------------------------------------->

    def load(self):
        return

    def reload(self):
        return

    def setup(self):
        return

    def start(self):
        return
