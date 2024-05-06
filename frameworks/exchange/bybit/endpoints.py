
BybitEndpoints = {
    "main1": "https://api.bybit.com",
    "main2": "https://api.bytick.com",
    "pub_ws": "wss://stream.bybit.com/v5/public/linear",
    "priv_ws": "wss://stream.bybit.com/v5/private",

    "ping": ("/v5/market/time", "GET"),                         
    "exchangeInfo": ("/fapi/v1/exchangeInfo", "GET"),      
    "instrumentInfo": ("/v5/market/instruments-info", "GET"), # NOTE: tick/lot sizes in filters (query per symbol)
    "orderbook": ("/v5/market/orderbook", "GET"),                   
    "trades": ("/v5/market/recent-trade", "GET"),                     
    "ohlcv": ("/v5/market/kline", "GET"),                      
    "allOpenOrders": ("/v5/order/realtime", "GET"),          
    "accountInfo": ("/v5/account/wallet-balance", "GET"),               
    "positionInfo": ("/v5/position/list", "GET"),         
    "feeRate": ("/v5/account/fee-rate", "GET"),            

    "createOrder": ("/v5/order/create", "POST"),                
    "amendOrder": ("/v5/order/amend", "POST"),                 
    "cancelOrder": ("/v5/order/cancel", "POST"),                
    "cancelAllOrders": ("/v5/order/cancel-all", "POST"),    
    "setLeverage": ("/v5/position/set-leverage", "POST"),             
}   