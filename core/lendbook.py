class Lendbook():
    def __init__(self, asset):
        self.asset = asset

    def asks(self):
        return NotImplementedError

    def bids(self):
        return NotImplementedError