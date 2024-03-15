from requests import Session
from requests.adapters import HTTPAdapter
from web3 import Web3
from web3._utils.rpc_abi import RPC
from web3.middleware import simple_cache_middleware, validation


def get_w3(rpc_url):
    adapter = HTTPAdapter(pool_connections=50, pool_maxsize=50)
    session = Session()
    session.mount("http://", adapter)
    session.mount("https://", adapter)

    w3 = Web3(Web3.HTTPProvider(rpc_url, session=session))
    w3.middleware_onion.add(simple_cache_middleware)
    validation.METHODS_TO_VALIDATE = [RPC.eth_sendTransaction, RPC.eth_estimateGas]

    return w3
