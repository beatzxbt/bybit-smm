import orjson
import hashlib
import hmac

from frameworks.exchange.base.client import Client


class BinanceClient(Client):
    recv_window = "5000"

    def __init__(self, api_key: str, api_secret: str) -> None:
        super().__init__(api_key, api_secret)

        self.headers_template = {
            **self.default_headers,
            "timestamp": self.timestamp,
            "signature": "",
        }

    def sign_headers(self, method, headers):
        self.update_timestamp()
        hash_signature = hmac.new(
            key=self.api_secret.encode(),
            msg=orjson.dumps(headers),
            digestmod=hashlib.sha256,
        )
        self.headers_template["timestamp"] = str(self.timestamp)
        self.headers_template["signature"] = hash_signature.hexdigest()
        return self.headers_template.copy()

    def error_handler(self, recv):
        match int(recv.get("code")):
            case 200:
                return (False, "")

            case 1003 | 1015:
                return (False, "Rate limits exceeded!")

            case 1008:
                return (True, "Server overloaded...")

            case 1021:
                return (True, "Out of recvWindow...")

            case 1111 | 4029 | 4030:
                return (False, "Incorrect tick/lot size...")

            case 1125:
                return (False, "Invalid listen key...")

            case 2010:
                return (False, "Order create rejected...")

            case 2011:
                return (False, "Order cancel rejected...")

            case 2012:
                return (False, "Order cancel all rejected...")

            case 2013:
                return (False, "Order does not exist...")

            case 2018:
                return (False, "Insufficient balance...")

            case _:
                return (False, "Unknown error code...")
