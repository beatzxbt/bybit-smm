from typing import List, Dict

from frameworks.exchange.base.ws_handlers.trades import TradesHandler


class BinanceTradesHandler(TradesHandler):
    def __init__(self, data: Dict) -> None:
        self.data = data
        super().__init__(self.data["trades"])

    def refresh(self, recv: List[Dict]) -> None:
        try:
            for trade in recv:
                self.format[0] = float(trade["time"])
                self.format[1] = 1.0 if trade["isBuyerMaker"] else 0.0
                self.format[2] = float(trade["price"])
                self.format[3] = float(trade["qty"])
                self.trades.append(self.format.copy())
        except Exception as e:
            raise Exception(f"Trades Refresh :: {e}")

    def process(self, recv: Dict) -> None:
        try:
            self.format[0] = float(recv["T"])
            self.format[1] = 1.0 if recv["m"] else 0.0
            self.format[2] = float(recv["p"])
            self.format[3] = float(recv["q"])
            self.trades.append(self.format.copy())

        except Exception as e:
            raise Exception(f"Trades Process :: {e}")
