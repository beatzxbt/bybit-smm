
from frameworks.sharedstate.market import MarketDataSharedState
from frameworks.tools.logging.logger import Logger
from frameworks.exchange.ccxt.Exchange import Exchange
from numpy_ringbuffer import RingBuffer
import numpy as np
import asyncio
from frameworks.sharedstate.private import PrivateDataSharedState
class ExchangeMarketStream:

    def __init__(self, exchange: Exchange, sharedstate: MarketDataSharedState, symbol: str) -> None:
        self.exchange = exchange
        self.mdss = sharedstate
        self.symbol = symbol
        self.logging = Logger()

    async def _initialize(self):
        # this can be done concurrently tbd
        _klines = await self.exchange.fetch_ohlcv(self.symbol, "1m", 500)
        ExchangeKlineHandler(self.exchange, self.mdss, self.symbol).initialize(_klines)

        _trades = await self.exchange.fetch_trades(self.symbol, 1000)
        ExchangeTradesHandler(self.exchange, self.mdss, self.symbol).initialize(_trades)


    async def _open_orders_sync(self):
        # this does not belong here
        while True:
            res = await self.exchange.open_orders(self.symbol) # we can do this with Ws
            ExchangeOrderHandler(self.exchange, self.pdss, self.symbol).sync(res)
            await asyncio.sleep(15)

    async def _current_position_sync(self) -> None:
        """
        Sync the current position & stats every 15s 
        """
        while True:
            # recv = await self.private_client.current_position()
            recv = await self.exchange.current_position(self.symbol)
            ExchangePositionHandler(self.exchange, self.pdss, self.symbol).sync(recv)
            await asyncio.sleep(15)

    async def _wallet_info_sync(self) -> None:
        """
        Sync the wallet information every 15s 
        """
        while True:
            recv = await self.exchange.wallet_info()
            ExchangeWalletHandler(self.pdss, self.symbol).sync(recv)
            await asyncio.sleep(15)


    async def watch_trades(self, symbol: str):
        while True:
            trades = await self.exchange.watch_trades(symbol)
            # print(trades)
            ExchangeTradesHandler(self.exchange, self.mdss, self.symbol).update(trades)
            # await asyncio.sleep(1)

    async def watch_ohlcv (self, symbol: str, timeframe: str):
        while True:
            ohlcv = await self.exchange.watch_ohlcv(symbol, timeframe)
            ExchangeKlineHandler(self.exchange, self.mdss, self.symbol).update(ohlcv)

    async def _stream(self):
        self.logging.info(f"{self.exchange.id} market data initialized...")

        # spawn watch_Trades and ohlcv streams
        await asyncio.gather(
            self.watch_trades(self.symbol),
            self.watch_ohlcv(self.symbol, "1m")
        )

    async def start_feed(self):
        await asyncio.gather(
            asyncio.create_task(self._open_orders_sync()),
            asyncio.create_task(self._current_position_sync()),
            asyncio.create_task(self._stream())
        )

class ExchangeKlineHandler:
    def __init__(self, exchange: Exchange, sharedstate: MarketDataSharedState, symbol: str) -> None:
        obj = sharedstate.ccxt_exchanges[exchange.instance.id] # move this elsewhere
        if symbol not in obj:
            obj[symbol] = {}
            obj[symbol]["trades"] = RingBuffer(capacity=1000, dtype=(float, 4))
        self.exchange = sharedstate.ccxt_exchanges[exchange.instance.id][symbol]

    def initialize(self, data: list) -> None:
        """
        Initialize the klines array
        """

        for candle in data:
            arr = np.array(candle, dtype=float)
            self.exchange["klines"].appendleft(arr)

    def update(self, recv: list) -> None:
        """
        Update the klines array
        """

        for candle in recv["data"]:
            new = np.array(
                object=[
                    candle["timestamp"],
                    candle["open"],
                    candle["high"],
                    candle["low"],
                    candle["close"],
                    candle["volume"],
                    # candle["turnover"]],
                ],
                dtype=float
            )

            # If prev time same, then overwrite, else append
            if self.exchange["klines"][-1][0] != new[0]:
                self.exchange["klines"].append(new)

            else:
                self.exchange["klines"].pop()
                self.exchange["klines"].append(new)

class ExchangeTradesHandler:

    def __init__(self, instance: Exchange, sharedstate: MarketDataSharedState, symbol: str) -> None:
        obj = sharedstate.ccxt_exchanges[instance.instance.id]
        if symbol not in obj:
            obj[symbol] = {}
            obj[symbol]["trades"] = RingBuffer(capacity=1000, dtype=(float, 4))
        self.exchange = sharedstate.ccxt_exchanges[instance.instance.id][symbol]

    def initialize(self, data: list) -> None:
        for row in data:
            side = 0 if row["side"] == "buy" else 1
            trade = np.array([row["timestamp"], side, row["price"], row["amount"]], dtype=float)
            self.exchange["trades"].append(trade)

    def update(self, recv: dict) -> None:
        for row in recv["data"]:
            side = 0 if row["side"] == "buy" else 1
            trade = np.array([[row["timestamp"], side, row["price"], row["amount"]]], dtype=float)
            self.exchange["trades"].append(trade)


class ExchangeOrderHandler:


    def __init__(self, instance: Exchange, sharedstate: PrivateDataSharedState, symbol: str) -> None:
        self.pdss = sharedstate
        self.symbol = symbol
        obj = sharedstate.ccxt_exchanges[instance.instance.id]
        if symbol not in obj:
            obj[symbol] = {}
            obj[symbol]["Data"] = {}
        self.exchange = sharedstate.ccxt_exchanges[instance.instance.id][symbol]

    def sync(self, recv: list) -> None:
        self.exchange["current_orders"] = {
            order["orderId"]: {"price": float(order["price"]), "qty": float(order["qty"]), "side": order["side"]} 
            for order in recv["result"]["list"]
        }


    def update(self, data: dict) -> None:
        new_orders = {
            order["orderId"]: {"price": float(order["price"]), "qty": float(order["qty"]), "side": order["side"]}
            for order in data
            if order["orderStatus"] == "New" and order["symbol"] == self.symbol
        }

        filled_orders = set(
            order["orderId"]
            for order in data
            if order['info']["orderStatus"] == "Filled" and order["symbol"] == self.symbol
        )

        # Update the orders
        self.exchange["current_orders"].update(new_orders)

        # Remove filled orders
        for order_id in filled_orders:
            self.exchange["current_orders"].pop(order_id, None)


class ExchangePositionHandler:


    def __init__(self, instance: Exchange, sharedstate: PrivateDataSharedState, symbol: str) -> None:
        self.pdss = sharedstate
        self.symbol = symbol
       
        obj = sharedstate.ccxt_exchanges[instance.instance.id]
        if symbol not in obj:
            obj[symbol] = {}
            obj[symbol]["Data"] = {}
        self.exchange = sharedstate.ccxt_exchanges[instance.instance.id][symbol]
    
    def sync(self, recv: dict) -> None:
        self.process(recv)

    def update(self, data: list) -> None:
        data = data["info"] #bypass raw data
        side = data["side"]
        if side:
            self.exchange["position_size"] = float(data["size"]) if side == "Buy" else -float(data["size"]) 
            self.exchange["leverage"] = float(data["leverage"])
            self.exchange["unrealized_pnl"] = float(data["unrealisedPnl"])


class ExchangeWalletHandler:


    def __init__(self, instance:Exchange, sharedstate: PrivateDataSharedState, symbol: str) -> None:
        self.pdss = sharedstate
        self.symbol = symbol

        obj = sharedstate.ccxt_exchanges[instance.instance.id]
        if symbol not in obj:
            obj[symbol] = {}
            obj[symbol]["API"] = {}
        self.exchange = sharedstate.ccxt_exchanges[instance.instance.id][symbol]
    
    def sync(self, recv: dict) -> None:
        self.process(recv)


    def update(self, data: list) -> None:
        self.exchange["account_balance"] = float(data['info']["totalWalletBalance"])
        self.exchange["maintainance_margin"] = float(data['info']["totalMaintenanceMargin"])
