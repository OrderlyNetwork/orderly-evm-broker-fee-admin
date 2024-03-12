import time
from decimal import Decimal

from utils.myconfig import ConfigLoader
from utils.mylogging import setup_logging
from utils.rest import sign_request
from utils.util import get_report_days

logger = setup_logging()
config = ConfigLoader.load_config()


def get_broker_users_fees(count=1):
    url = f"/v1/broker/user_info?page={count}&size=500"
    try:
        data = sign_request("GET", f"{url}")
    except Exception as e:
        data = None
        logger.error(f"Get Broker User's Fee URL Failed: {url} - {e}")
    return data


def get_broker_default_rate():
    url = "/v1/broker/fee_rate/default"
    try:
        data = sign_request("GET", f"{url}")
    except Exception as e:
        data = None
        logger.error(f"Get Broker Default Fee URL Failed: {url} - {e}")
    return data


def set_broker_default_rate(maker_fee_rate, taker_fee_rate):
    url = "/v1/broker/fee_rate/default"
    _payload = {"maker_fee_rate": maker_fee_rate, "taker_fee_rate": taker_fee_rate}
    try:
        _post_data = sign_request("POST", f"{url}", payload=_payload)
    except Exception as e:
        logger.error(f"Get Broker Default Fee URL Failed: {url} - {e}")
    return


def get_broker_users_volumes(count):

    start_time, end_time = get_report_days()
    _payload = {
        "start_date": start_time,
        "end_date": end_time,
        "size": "500",
        "page": count,
        "aggregateBy": "account",
    }
    _volumes = sign_request("GET", "/v1/volume/broker/daily", payload=_payload)
    return _volumes


def get_tier(volume):
    _tiers = config["rate"]["fee_tier"]
    # tier_found = None
    for tier in _tiers:
        if tier["volume_min"] <= volume and (
            tier["volume_max"] is None or volume < tier["volume_max"]
        ):
            tier_found = {
                "futures_maker_fee_rate": Decimal(tier["maker_fee"].replace("%", ""))
                / 100,
                "futures_taker_fee_rate": Decimal(tier["taker_fee"].replace("%", ""))
                / 100,
            }
            return tier_found
            break


def reset_user_fee_default(account_ids):
    _payload = {"account_ids": account_ids}
    _reset_fee = sign_request(
        "POST", "/v1/broker/fee_rate/set_default", payload=_payload
    )
    return _reset_fee


def set_broker_user_fee(_data):

    data = {}
    _tier1 = config["rate"]["fee_tier"][0]
    _tier1_maker_fee = Decimal(_tier1["maker_fee"].replace("%", "")) / 100
    _tier1_taker_fee = Decimal(_tier1["taker_fee"].replace("%", "")) / 100
    if _data:
        for _da in _data:
            _futures_maker_fee_rate = _da["futures_maker_fee_rate"]
            _futures_taker_fee_rate = _da["futures_taker_fee_rate"]
            _fee_key = f"{_futures_maker_fee_rate}:{_futures_taker_fee_rate}"
            if _fee_key not in data.keys():
                data[_fee_key] = []
            data[_fee_key].append(_da["account_id"])
        _ok_count = 0
        _fail_count = 0
        for _fk, _fv in data.items():
            maker_fee_rate = Decimal(_fk.split(":")[0])
            taker_fee_rate = Decimal(_fk.split(":")[1])
            account_ids = _fv

            batch_size = 100
            
            for i in range(0, len(account_ids), batch_size):
                batch_ids = account_ids[i:i+batch_size]
                _payload = {
                    "account_ids": batch_ids,
                    "maker_fee_rate": str(maker_fee_rate),
                    "taker_fee_rate": str(taker_fee_rate),
                }
                try:
                    if (
                        maker_fee_rate == _tier1_maker_fee
                        or taker_fee_rate == _tier1_taker_fee
                    ):
                        _reset_fee = reset_user_fee_default(batch_ids)
                        if not _reset_fee["success"]:
                            logger.error(
                                f"Failed to reset user rates account_ ids - {batch_ids}"
                            )
                    _update_fee = sign_request(
                        "POST", "/v1/broker/fee_rate/set", payload=_payload
                    )
                    if _update_fee["success"] == True:
                        _ok_count += len(batch_ids)
                    else:
                        _fail_count += len(batch_ids)
                except Exception as e:
                    _fail_count += len(batch_ids)
                    logger.error(
                        f"Set Broker User's Fee Failed: {_fk} - {_payload} - {str(e)} "
                    )
                time.sleep(2)
        logger.info(
            f"Set Broker User's Status - success: {_ok_count}, failed: {_fail_count}"
        )
        return _ok_count, _fail_count
