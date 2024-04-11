import datetime
import time
from decimal import Decimal

from controllers.api import (
    get_account,
    get_broker_users_fees,
    get_broker_default_rate,
    set_broker_default_rate,
    get_broker_users_volumes,
    get_user_fee_rates,
    set_broker_user_fee,
)
from controllers.evm import get_staking_bals
from utils.myconfig import ConfigLoader
from utils.mylogging import setup_logging
from utils.pd import BrokerFee, StakingBal
from utils.util import send_message

config = ConfigLoader.load_config()
logger = setup_logging()


def init_broker_fees():
    # 每次启动，将当前Broker所有用户费率配置情况更新到本地数据库
    _count = 1
    broker_fee = BrokerFee(_type="broker_user_fee")
    address2fee_rate = {}
    while True:
        data = get_broker_users_fees(_count)
        if not data or not data.get("data"):
            alert_message = f'WOOFi Pro {config["common"]["orderly_network"]} - get_broker_users_fees failed, _count: {_count}'
            send_message(alert_message)
            break
        if not data["data"].get("rows"):
            break
        if data:
            for _data in data["data"]["rows"]:
                print(_data)
                address2fee_rate[_data["address"]] = {
                    "futures_maker_fee_rate": _data["maker_fee_rate"],
                    "futures_taker_fee_rate": _data["taker_fee_rate"],
                }
                broker_fee.create_update_user_fee_data(_data, delete_flag=True)
        _count += 1
        time.sleep(2)

    verify_broker_fees_data(address2fee_rate)


def verify_broker_fees_data(address2fee_rate):
    broker_fee = BrokerFee(_type="broker_user_fee")
    for _row in broker_fee.pd.df.itertuples():
        fee_rate = address2fee_rate[_row.address]
        if fee_rate["futures_maker_fee_rate"] != _row.futures_maker_fee_rate:
            alert_message = f'WOOFi Pro Debug - address: {_row.address}, _row.futures_maker_fee_rate: {_row.futures_maker_fee_rate}, futures_maker_fee_rate: {fee_rate["futures_maker_fee_rate"]}'
            send_message(alert_message)
        if fee_rate["futures_taker_fee_rate"] != _row.futures_taker_fee_rate:
            alert_message = f'WOOFi Pro Debug - address: {_row.address}, _row.futures_taker_fee_rate: {_row.futures_taker_fee_rate}, futures_taker_fee_rate: {fee_rate["futures_taker_fee_rate"]}'
            send_message(alert_message)


def init_staking_bals():
    staking_bals = get_staking_bals()
    if staking_bals:
        address2bal = {}
        staking_bal = StakingBal(_type="staking_user_bal")
        broker_id = "woofi_pro"
        for _bal in staking_bals:
            query_result = staking_bal.query_data_by_address(_bal["address"])
            if query_result.empty:
                retry = 3
                while retry > 0:
                    data = get_account(_bal["address"], broker_id)
                    time.sleep(0.1)
                    if not data or (not data.get("data") and data.get("message", "") != "account does not exist"):
                        retry -= 1
                        alert_message = f'WOOFi Pro {config["common"]["orderly_network"]} - get_account failed, address: {_bal["address"]}, retry: {retry}'
                        send_message(alert_message)
                        continue
                    else:
                        break
                if data.get("message", "") == "account does not exist":
                    logger.info(f'address: {_bal["address"]} account does not exist')
                    continue
                account_id = data["data"]["account_id"]
                logger.info(f'address: {_bal["address"]}, get account_id: {account_id}')
            else:
                account_id = query_result["account_id"].iloc[0]
            address2bal[_bal["address"]] = _bal["bal"]
            staking_bal.create_update_user_bal_data({
                "account_id": account_id,
                "bal": _bal["bal"],
                "address": _bal["address"],
            })

        for _row in staking_bal.pd.df.itertuples():
            if _row.address not in address2bal:
                staking_bal.create_update_user_bal_data({
                    "account_id": _row.account_id,
                    "bal": "0",
                    "address": _row.address,
                })

        verify_staking_bals_data(address2bal)


def verify_staking_bals_data(address2bal):
    staking_bal = StakingBal(_type="staking_user_bal")
    for _row in staking_bal.pd.df.itertuples():
        bal = address2bal.get(_row.address, "0")
        if _row.bal != bal:
            alert_message = f"WOOFi Pro Debug - address: {_row.address}, _row.bal: {_row.bal}, bal: {bal}"
            send_message(alert_message)


def fetch_broker_default_rate():
    get_broker_default_rate()


def update_broker_default_fee(maker_fee, taker_fee):
    url = "/v1/broker/fee_rate/default"
    try:
        _data = get_broker_default_rate()
        if _data:
            logger.info(
                f'Modifying Broker Default Fees:  Maker Fee {_data["data"]["maker_fee_rate"]}->{maker_fee},Taker Fee {_data["data"]["taker_fee_rate"]}->{taker_fee}'
            )
        set_broker_default_rate(maker_fee, taker_fee)
    except Exception as e:
        logger.error(f"Get Broker Default Fee URL Failed: {url} - {e}")


def update_user_special_rate(account_id, maker_fee, taker_fee):
    _whitelists = config["rate"]["special_rate_whitelists"]
    if "special_rate_whitelists" in config["rate"] and isinstance(
        config["rate"]["special_rate_whitelists"], list
    ):
        if account_id not in _whitelists:
            _whitelists.append(f"{account_id}")
    else:
        logger.info(f"Key '{config['rate']}' not found or is not a list.")
    _data = [
        {
            "account_id": account_id,
            "futures_maker_fee_rate": maker_fee,
            "futures_taker_fee_rate": taker_fee,
        }
    ]
    _ok_count, _fail_count = set_broker_user_fee(_data)
    if _ok_count == 1:
        ConfigLoader.save_config(config)
    logger.info(
        f"Update User's Special Rate: Account ID = {account_id}, Taker Fee = {taker_fee}, Maker Fee = {maker_fee}"
    )


def update_user_rates():
    logger.info("Broker user rate update started")
    _count = 1
    user_fee = BrokerFee(_type="broker_user_fee")
    staking_bal = StakingBal(_type="staking_user_bal")
    account_id2data = {}
    for _row in staking_bal.pd.df.itertuples():
        account_id2data[_row.account_id] = {
            "staking_bal": Decimal(_row.bal),
            "perp_volume": 0,
            "address": _row.address,
        }

    while True:
        _data = get_broker_users_volumes(_count)
        if not _data or not _data.get("data"):
            alert_message = f'WOOFi Pro {config["common"]["orderly_network"]} - get_broker_users_volumes failed, _count: {_count}'
            send_message(alert_message)
            break
        if not _data["data"].get("rows"):
            break
        if _data:
            for _row in _data["data"]["rows"]:
                _account_id = _row["account_id"]
                if _account_id in account_id2data:
                    account_id2data[_account_id]["perp_volume"] = _row["perp_volume"]
                else:
                    account_id2data[_account_id] = {
                        "staking_bal": 0,
                        "perp_volume": _row["perp_volume"],
                        "address": _row["address"],
                    }

        _count += 1
        time.sleep(2)

    account_id2address = {_row.account_id: _row.address for _row in user_fee.pd.df.itertuples()}
    for _account_id, _data in account_id2data.items():
        if _account_id not in account_id2address:
            account_id2address[_account_id] = _data["address"]

    special_rate_whitelists = config["rate"]["special_rate_whitelists"]
    tier_count = {_tier["tier"]: 0 for _tier in config["rate"]["fee_tier"]}
    data = []
    for _account_id, _address in account_id2address.items():
        perp_volume = account_id2data.get(_account_id, {}).get("perp_volume", 0)
        staking_bal = account_id2data.get(_account_id, {}).get("staking_bal", 0)

        _user_fee = get_user_fee_rates(perp_volume, staking_bal)
        if not _user_fee:
            alert_message = f'WOOFi Pro {config["common"]["orderly_network"]} - get_user_fee_rates, _address: {_address}, perp_volume: {perp_volume}, staking_bal: {staking_bal}'
            send_message(alert_message)
            break
        if _account_id not in special_rate_whitelists:
            tier_count[_user_fee["tier"]] += 1
            _new_futures_maker_fee_rate = Decimal(_user_fee["futures_maker_fee_rate"])
            _new_futures_taker_fee_rate = Decimal(_user_fee["futures_taker_fee_rate"])
            old_user_fee = user_fee.pd.query_data(_account_id)
            if not old_user_fee.empty:
                _old_futures_maker_fee_rate = Decimal(old_user_fee.futures_maker_fee_rate.values[0])
                _old_futures_taker_fee_rate = Decimal(old_user_fee.futures_taker_fee_rate.values[0])
                try:
                    if (
                        _new_futures_maker_fee_rate
                        != _old_futures_maker_fee_rate
                        or _new_futures_taker_fee_rate
                        != _old_futures_taker_fee_rate
                    ):
                        maker_fee_rate = _new_futures_maker_fee_rate
                        taker_fee_rate = _new_futures_taker_fee_rate
                        logger.info(
                            f"{_account_id} - New Maker Fee Rate: {maker_fee_rate}, Smaller Taker Fee Rate: {taker_fee_rate}"
                        )
                        _ret = {
                            "account_id": _account_id,
                            "futures_maker_fee_rate": maker_fee_rate,
                            "futures_taker_fee_rate": taker_fee_rate,
                            "address": _address,
                        }
                        data.append(_ret)
                        user_fee.create_update_user_fee_data(_ret)
                except:
                    print(
                        f"New rates are not smaller than old rates: {_account_id}"
                    )
            else:
                _ret = {
                    "account_id": _account_id,
                    "futures_maker_fee_rate": _new_futures_maker_fee_rate,
                    "futures_taker_fee_rate": _new_futures_taker_fee_rate,
                    "address": _address,
                }
                data.append(_ret)
                user_fee.create_update_user_fee_data(_ret)

    ok_count, fail_count = set_broker_user_fee(data)

    alert_message = f'WOOFi Pro {config["common"]["orderly_network"]} - update_user_rates, ok_count: {ok_count}, fail_count: {fail_count}'
    send_message(alert_message)

    report_message = f'WOOFi Pro {config["common"]["orderly_network"]} Tier Report {datetime.date.today().strftime("%Y-%m-%d")}\n\n'
    for tier, count in tier_count.items():
        report_message += f"tier {tier}: {count}\n"
    report_message.rstrip("\n")
    send_message(report_message)

    logger.info(report_message)
    logger.info("Broker user rate update completed")


def update_user_rate():
    logger.info(
        "========================Orderly EVM Broker Fee Admin Startup========================"
    )
    init_broker_fees()
    init_staking_bals()
    update_user_rates()
