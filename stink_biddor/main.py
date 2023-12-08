
import asyncio
from stink_biddor.strategy.core import Strategy
from stink_biddor.settings import StrategyParameters
from frameworks.sharedstate.market import MarketDataSharedState
from frameworks.sharedstate.private import PrivateDataSharedState
from frameworks.exchange.ccxt.Exchange import Exchange


async def main(configuration_directory: str, parameter_directory: str):


    # Instantiate exchange
    # tmp: read this from the file
    exchange_id = "okx"
    sandbox = True
    api_key = ""
    secret = ""
    exchange = Exchange(exchange_id, api_key, secret, sandbox)


    params = StrategyParameters(parameter_directory)
    mdss = MarketDataSharedState(params)
    pdss = PrivateDataSharedState(params)
    
    # rememeber the data feeds being ran from sharedstate still needs to be
    # implemented. Modify any behaviour if it turns the mdss class a bit funny 
    # this also means that refreshing parameters will be managed within the class
    # and not outsourced into the strategy/main file, cluttering it
    await Strategy(mdss, pdss, params).run()


if __name__ == "__main__":
    CONFIGURATION_DIR = "./frameworks/config/config.yaml"
    PARAMETERS_DIR = "./stink_biddor/parameters.yaml"

    asyncio.run(main(CONFIGURATION_DIR, PARAMETERS_DIR))
