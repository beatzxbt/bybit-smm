from typing import Dict

from frameworks.exchange.bybit.types import BybitSideConverter, BybitOrderTypeConverter
from frameworks.exchange.base.formats import Formats


class BybitFormats(Formats):
    def __init__(self) -> None:
        super().__init__(BybitSideConverter, BybitOrderTypeConverter)
        self.base_payload = {"category": "linear"}

    def create_order(
        self,
        symbol,
        side,
        orderType,
        size,
        price,
    ):
        format = {
            **self.base_payload,
            "symbol": symbol,
            "side": self.convert_side.to_str(side),
            "orderType": self.convert_order_type.to_str(orderType),
            "qty": str(size),
        }

        # Market order
        if orderType == 1:
            return format

        # Limit order
        elif orderType == 0:
            format["price"] = str(price)
            format["timeInForce"] = "PostOnly"

        return format

    def amend_order(
        self,
        orderId,
        side,
        size,
        price,
    ):
        return {
            **self.base_payload,
            "orderId": orderId,
            "price": str(price),
            "qty": str(size),
        }

    def cancel_order(self, symbol, orderId):
        return {**self.base_payload, "orderId": orderId}

    def cancel_all_orders(self, symbol):
        return {**self.base_payload, "symbol": symbol}

    def get_ohlcv(self, symbol, interval):
        return {
            **self.base_payload,
            "symbol": symbol,
            "interval": str(interval),
            "limit": "1000",  # NOTE: [1, 1000]. Default: 200
        }

    def get_trades(self, symbol):
        return {
            **self.base_payload,
            "symbol": symbol,
            "limit": "1000",  # NOTE: [1,1000], default: 500
        }

    def get_orderbook(self, symbol):
        return {
            **self.base_payload,
            "symbol": symbol,
            "limit": "200",  # NOTE: [1, 200]. Default: 25
        }

    def get_ticker(self, symbol):
        return {**self.base_payload, "symbol": symbol}

    def get_open_orders(self, symbol):
        return {**self.base_payload, "symbol": symbol, "limit": "50"}

    def get_position(self, symbol):
        return {**self.base_payload, "symbol": symbol}

    def get_account_info(self) -> Dict:
        return f"category={self.base_payload['category']}"

    def get_instrument_info(self, symbol: str) -> Dict:
        return {**self.base_payload, "symbol": symbol}
