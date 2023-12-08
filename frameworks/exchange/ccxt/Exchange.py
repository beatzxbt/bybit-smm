
import asyncio
import aiohttp
import ccxt.async_support as ccxt
from frameworks.exchange.bybit.post.types import OrderTypesFutures
from frameworks.sharedstate.private import PrivateDataSharedState

class Exchange:
    """
    Generic ccxt exchange
    """
    instance: ccxt.Exchange

    def __init__(self, id: str, apiKey: str, secret: str, sandboxMode = False) -> None:
        # self.pdss = sharedstate
        self.id = id
        self.instance = getattr(ccxt, id)({
            'apiKey': apiKey,
            'secret': secret,
            'sandbox': sandboxMode,
        })

    async def order_market(self, symbol:str, side: str, qty: float, tp: float=None) -> dict | None:
        params = {}
        if tp is not None:
            params =  {'takeProfit': {"triggerPrice": tp}}
        return await self.instance.create_order(symbol, 'market', side, qty, params=params)

    async def order_limit(self, symbol:str, side: str, qty: float, price: float, tp: float=None) -> dict | None:
        params = {}
        if tp is not None:
            params =  {'takeProfit': {"triggerPrice": tp}}
        return await self.instance.create_order(symbol, 'limit', side, qty, price, params=params)

    async def amend(self, id: str, symbol: str, side: str, price: float, qty: float, tp: float=None) -> dict | None:
        return await self.instance.edit_order(id, symbol, 'limit', side, price, qty)

    async def cancel_all(self):
        return await self.instance.cancel_all_orders()

    async def cancel(self, id: str, symbol: str) -> dict | None:
        return await self.instance.cancel_order(id, symbol)

    async def fetch_trades(self, symbol: str, limit: int = 1000):
        return await self.instance.fetch_trades(symbol, limit = limit)

    async def fetch_ohlcv(self, symbol: str, timeframe: str, limit: int = None):
        return await self.instance.fetch_ohlcv(symbol, timeframe, None, limit)

    async def open_orders(self, symbol: str):
        return await self.instance.fetch_open_orders(symbol)
    
    async def current_position(self, symbol: str):
        return await self.instance.fetch_position(symbol)
    
    async def wallet_info(self):
        return await self.instance.fetch_balance()

    async def watch_trades(self, symbol: str):
        while True:
            trades = await self.instance.watch_trades(symbol)
            yield trades

    async def watch_ohlcv (self, symbol: str, timeframe: str):
        while True:
            ohlcv = await self.instance.watch_ohlcv(symbol, timeframe)
            yield ohlcv