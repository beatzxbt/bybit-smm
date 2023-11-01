
import numpy as np


class BaseOrderBook:


    def __init__(self):
        self.asks = np.empty(shape=(0, 2), dtype=float)
        self.bids = np.empty_like(self.asks)


    def sort_book(self):
        self.asks = self.asks[self.asks[:, 0].argsort()]
        self.bids = self.bids[self.bids[:, 0].argsort()[::-1]]


    def update_book(self, asks_or_bids, data):
        for price, qty in data:
            asks_or_bids = asks_or_bids[asks_or_bids[:, 0] != price]

            if qty > 0:
                asks_or_bids = np.vstack((asks_or_bids, np.array([price, qty])))

        return asks_or_bids

    def clear(self):
        '''
        Should only be used when the WebSocket connection is closed.
        '''
        self.asks = np.empty(shape=(0, 2), dtype=float)
        self.bids = np.empty_like(self.asks)


    def process(self, recv):
        raise NotImplementedError("Derived classes should implement this method")
