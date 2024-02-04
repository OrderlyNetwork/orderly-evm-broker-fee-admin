from utils.mylogging import setup_logging
import sys
import scheduler
from controllers.fee import (
    update_broker_default_fee,
    update_user_special_rate,
    update_user_rate_base_volume,
    init_broker_fees,
    fetch_broker_default_rate,
)
from utils.myconfig import ConfigLoader

config = ConfigLoader.load_config()
logger = setup_logging()

def show_help():
    help_text = """
    Help Information(Option,Parameters):
    - update-broker-default-fee <maker fee> <taker fee> 
    - update-user-special-rate <account_id> <maker fee> <taker fee> 
    - update-user-rate-base-volume
    Description: The fee unit uses percentiles, e.g. 0.0003 = 0.03%
    
    Examples: python3 app/main.py update-broker-default-fee 0.0003 0.0005
    """
    print(help_text)


if __name__ == "__main__":
    
    args = sys.argv[1:]
    if len(args) == 0:
        show_help()
    elif args[0] == "update-broker-default-fee" and len(args) == 3:
        update_broker_default_fee(args[1], args[2])
    elif args[0] == "update-user-special-rate" and len(args) == 4:
        update_user_special_rate(args[1], args[2], args[3])
    elif args[0] == "get_broker_default_rate":
        fetch_broker_default_rate()
    elif args[0] == "update-user-rate-base-volume":
        if config["rate"]["startup_batch_update_fee"]:
            logger.info(
                "For the first time, the broker user rate is updated based on the yaml configuration startup_batch_update_fee=True"
            )
            init_broker_fees()
            update_user_rate_base_volume()
        scheduler.run()
    else:
        logger.info("Invalid arguments.")
        show_help()
