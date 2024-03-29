import time
from decimal import Decimal

from utils.w3 import get_w3
from utils.multicall3 import Multicall3
from utils.myconfig import ConfigLoader
from utils.mylogging import setup_logging

config = ConfigLoader.load_config()
logger = setup_logging()

staking_manager_abi = [{"inputs":[{"internalType":"uint256","name":"start","type":"uint256"},{"internalType":"uint256","name":"end","type":"uint256"}],"name":"allStakers","outputs":[{"internalType":"address[]","name":"","type":"address[]"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"allStakers","outputs":[{"internalType":"address[]","name":"","type":"address[]"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"allStakersLength","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"address","name":"","type":"address"}],"name":"mpBalance","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"address","name":"","type":"address"}],"name":"wooBalance","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"}]


def get_staking_bals():
    start_time = time.time()
    w3 = get_w3(config["arbitrum"]["rpc_url"])
    m3 = Multicall3(config["arbitrum"]["rpc_url"], config["arbitrum"]["multicall3_address"])

    staking_manager = w3.eth.contract(config["arbitrum"]["staking_manager_address"], abi=staking_manager_abi)
    users_length = staking_manager.functions.allStakersLength().call()

    batch_size = 2000
    users = []
    woo_bal_funcs, mp_bal_funcs = [], []
    try:
        for i in range(0, users_length // batch_size + 1):
            start, end = i * batch_size, (i + 1) * batch_size
            end = users_length if end > users_length else end

            users += staking_manager.functions.allStakers(start, end).call()
            for user in users[start:end]:
                woo_bal_funcs.append(staking_manager.functions.wooBalance(user))
                mp_bal_funcs.append(staking_manager.functions.mpBalance(user))
            time.sleep(0.5)

        woo_bals, mp_bals = [], []
        for i in range(0, users_length, batch_size):
            woo_bals += m3.try_aggregate(True, woo_bal_funcs[i:i + batch_size])
            mp_bals += m3.try_aggregate(True, mp_bal_funcs[i:i + batch_size])
            time.sleep(0.5)
    except Exception as e:
        logger.error(f"Get User Staking Balances Failed: {e}")
        return None

    end_time = time.time()
    logger.info(f"user staking balances retrieval successful, elapsed_time: {end_time - start_time}s")
    return [{
        "address": user.lower(),
        "bal": str((Decimal(woo_bals[i]) + Decimal(mp_bals[i])) / Decimal(1e18)),
    } for i, user in enumerate(users)]
