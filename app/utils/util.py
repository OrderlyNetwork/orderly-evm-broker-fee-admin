import time
import json
import uuid
from datetime import datetime, timedelta
from utils.myconfig import ConfigLoader

config = ConfigLoader.load_config()


def get_timestamp():
    return int(time.time() * 1000)


def get_now_datetime():
    current_time = datetime.now()
    formatted_time = current_time.strftime("%Y-%m-%d %H:%M:%S")
    return formatted_time


def get_report_days():
    statistical_days = config["common"]["statistical_days"]
    now = datetime.now()
    end_time = now
    start_time = now - timedelta(days=statistical_days)
    return start_time.strftime("%Y-%m-%d %H:%M:%S"), end_time.strftime(
        "%Y-%m-%d %H:%M:%S"
    )


def convert_list_to_json_array(symbols):
    if symbols is None:
        return symbols
    res = json.dumps(symbols)
    return res.replace(" ", "")


def get_uuid():
    return str(uuid.uuid4())


def cleanNoneValue(d) -> dict:
    out = {}
    for k in d.keys():
        if d[k] is not None:
            out[k] = d[k]
    return out


class Error(Exception):
    pass


class ClientError(Error):
    def __init__(
        self, status_code, error_code, error_message, header, error_data=None
    ):
        # https status code
        self.status_code = status_code
        # error code returned from server
        self.error_code = error_code
        # error message returned from server
        self.error_message = error_message
        # the whole response header returned from server
        self.header = header
        # return data if it's returned from server
        self.error_data = error_data


class ServerError(Error):
    def __init__(self, status_code, message):
        self.status_code = status_c
