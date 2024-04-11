import base64
import decimal
import json
from json import JSONDecodeError

import base58
import requests
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from eth_account.messages import encode_structured_data
from web3 import Web3

from utils.myconfig import ConfigLoader
from utils.mylogging import setup_logging
from utils.util import get_timestamp, clean_none_value, ClientError, ServerError

config = ConfigLoader.load_config()
logger = setup_logging()

session = requests.Session()
api_key = config["common"]["api_key"]
api_secret = config["common"]["api_secret"]
account_id = config["common"]["account_id"]
orderly_endpoint = config["common"]["orderly_endpoint"]


def generate_signature(api_secret, message=None):
    if not api_secret:
        raise "Please configure orderly secret in the configuration file config.ini"
    _api_secret = api_secret.split(":")[1]
    _orderly_private_key = Ed25519PrivateKey.from_private_bytes(
        base58.b58decode(_api_secret)[0:32]
    )
    _timestamp = get_timestamp()
    if message and isinstance(message, dict):
        message["timestamp"] = _timestamp
    else:
        message = f"{_timestamp}{message}" if message else _timestamp
    _signature = base64.b64encode(
        _orderly_private_key.sign(bytes(str(message), "utf-8"))
    ).decode("utf-8")
    return str(_timestamp), _signature


def generate_wallet_signature(wallet_secret, message=None):
    private_key = f"0x{wallet_secret}"
    _message = message
    encoded_message = encode_structured_data(_message)
    w3 = Web3()
    signed_message = w3.eth.account.sign_message(
        encoded_message, private_key=private_key
    )
    return signed_message.signature.hex()


def _request(http_method, url_path, payload=None):
    if payload:
        _payload = clean_none_value(payload)
        if _payload:
            if http_method == "GET" or http_method == "DELETE":
                url_path += "?" + "&".join([f"{k}={v}" for k, v in _payload.items()])
                payload = ""
            else:
                payload = _payload

    if payload is None:
        payload = ""
    url = config["common"]["orderly_endpoint"] + url_path
    params = clean_none_value(
        {
            "url": url,
            "params": payload,
        }
    )
    response = _dispatch_request(http_method, params)
    logger.info(
        f"raw response from server: {response.text}, elapsed_time: {response.elapsed.total_seconds()}s"
    )
    try:
        data = response.json()
    except ValueError:
        data = response.text

    return data


def sign_request(http_method, url_path, payload=None):
    _payload = ""
    if payload:
        _payload = clean_none_value(payload)
        if _payload:
            if http_method == "GET" or http_method == "DELETE":
                url_path += "?" + "&".join([f"{k}={v}" for k, v in _payload.items()])
                _payload = ""

    params = {}
    payload = _payload if _payload else ""
    params["url_path"] = url_path
    params["payload"] = payload
    params["http_method"] = http_method
    query_string = _prepare_params(params)
    _timestamp, _signature = generate_signature(api_secret, message=query_string)

    session.headers.update(
        {
            "orderly-timestamp": _timestamp,
            "orderly-account-id": account_id,
            "orderly-key": api_key,
            "orderly-signature": _signature,
            "User-Agent": "EVM Broker Fee Admin ",
        }
    )
    # logger.info(f"Sign Request Headers: {session.headers}")
    return send_request(http_method, url_path, payload)


def send_request(http_method, url_path, payload=None):
    if payload is None:
        payload = {}
    url = orderly_endpoint + url_path
    params = clean_none_value({"url": url, "params": payload})
    response = _dispatch_request(http_method, params)
    # logger.info(
    #     f"raw response from server: {response.text}, elapsed_time: {response.elapsed.total_seconds()}s"
    # )
    _handle_rest_exception(response)

    try:
        data = json.loads(response.text, parse_float=decimal.Decimal)
    except ValueError:
        data = response.text
    result = {}

    if len(result) != 0:
        result["data"] = data
        return result
    return data


def _prepare_params(params: dict):
    _http_method = params["http_method"]
    _url_path = params["url_path"]
    _payload = json.dumps(params["payload"]) if params["payload"] else params["payload"]
    _params = "{0}{1}{2}".format(_http_method, _url_path, _payload)
    return _params


def _dispatch_request(http_method, params):
    method_func = {
        "GET": session.get,
        "DELETE": session.delete,
        "PUT": session.put,
        "POST": session.post,
    }.get(http_method, "GET")
    if http_method == "POST":
        logger.info(params)
        return method_func(url=params["url"], json=params["params"])
    else:
        return method_func(url=params["url"])


def _handle_rest_exception(response):
    status_code = response.status_code
    if status_code < 400:
        return None
    if 400 <= status_code < 500:
        error_data = None
        try:
            err = json.loads(response.text)
        except JSONDecodeError:
            raise ClientError(status_code, None, response.text, response.headers, error_data)
        if "data" in err:
            error_data = err["data"]
        raise ClientError(
            status_code, err["error"], err["message"], response.headers, error_data
        )
    raise ServerError(status_code, response.text)
