import json
import os

import pandas as pd

from utils.util import get_now_datetime


class PandasCSVHandler:
    def __init__(self, _type="data/data/broker_fee.csv"):
        self._type = _type
        if self._type == "broker_user_fee":
            self.filename = "data/data/broker_user_fee.csv"
        elif self._type == "broker_user_volume":
            self.filename = "data/data/broker_user_volume.csv"
        elif self._type == "staking_user_bal":
            self.filename = "data/data/staking_user_bal.csv"
        self.read_csv()

    def read_csv(self):
        fee_dir = os.path.dirname(self.filename)
        if not os.path.exists(fee_dir):
            os.makedirs(fee_dir)

        if not os.path.exists(self.filename):
            if self._type == "broker_user_fee":
                headers = [
                    "account_id",
                    "futures_maker_fee_rate",
                    "futures_taker_fee_rate",
                    "address",
                    "update_time",
                ]
            elif self._type == "broker_user_volume":
                headers = [
                    "account_id",
                    "futures_maker_fee_rate",
                    "futures_taker_fee_rate",
                    "perp_volume",
                    "address",
                    "update_time",
                ]
            elif self._type == "staking_user_bal":
                headers = [
                    "account_id",
                    "bal",
                    "address",
                    "update_time",
                ]
            pd.DataFrame(columns=headers).to_csv(self.filename, index=False)
        self.df = pd.read_csv(
            self.filename,
            dtype={"futures_maker_fee_rate": str, "futures_taker_fee_rate": str, "bal": str},
        )

    def write_csv(self):
        self.df.to_csv(self.filename, index=False)

    def query_data(self, query_str):
        query_result = self.df.query(f'account_id == "{query_str}"')
        if query_result.empty:
            return pd.DataFrame()
        return query_result

    def update_data_if_needed(self, query_result, column, new_value):
        rows_to_update = query_result[column] != new_value
        if rows_to_update.any():
            self.df.loc[query_result.index[rows_to_update], column] = new_value
            self.df.loc[
                query_result.index[rows_to_update], "update_time"
            ] = get_now_datetime()

    def write_json_to_csv(self, json_data):
        if isinstance(json_data, str):
            data = json.loads(json_data)
        else:
            data = json_data
        df = pd.DataFrame([data]) if isinstance(data, dict) else pd.DataFrame(data)
        df.to_csv(self.filename, mode="a", header=False, index=False)


class BrokerFee:
    def __init__(self, _type="broker_user_fee"):
        self._type = _type
        self.pd = PandasCSVHandler(_type=self._type)
        self.flag = True

    def create_user_fee_data(self, rec, delete_flag=False):
        rec.pop("fee_tier", None)
        rec["update_time"] = get_now_datetime()
        if delete_flag and self.flag:
            self.remove_user_fee_data()
            self.pd = PandasCSVHandler(_type=self._type)
            self.flag = False

        self.pd.write_json_to_csv(rec)

    def create_update_user_fee_data(self, rec, delete_flag=False):
        rec.pop("fee_tier", None)
        rec["update_time"] = get_now_datetime()
        if delete_flag and self.flag:
            self.remove_user_fee_data()
            self.pd = PandasCSVHandler(_type=self._type)
            self.flag = False
        query_result = self.pd.query_data(rec["account_id"])
        if not query_result.empty:
            updates_needed = False
            for key, value in rec.items():
                if (
                    key in ["futures_maker_fee_rate", "futures_taker_fee_rate"]
                    and query_result[key].iloc[0] != value
                ):
                    self.pd.update_data_if_needed(query_result, key, value)
                    updates_needed = True

            if updates_needed:
                self.pd.write_csv()
        else:
            self.pd.write_json_to_csv(rec)

    def remove_user_fee_data(self):
        os.remove(self.pd.filename)


class StakingBal:
    def __init__(self, _type="staking_user_bal"):
        self._type = _type
        self.pd = PandasCSVHandler(_type=self._type)

    def query_data_by_address(self, query_str):
        query_result = self.pd.df.query(f'address == "{query_str}"')
        if query_result.empty:
            return pd.DataFrame()
        return query_result

    def create_update_user_bal_data(self, rec):
        rec["update_time"] = get_now_datetime()
        query_result = self.query_data_by_address(rec["address"])
        if not query_result.empty:
            updates_needed = False
            for key, value in rec.items():
                if key == "bal" and query_result[key].iloc[0] != value:
                    self.pd.update_data_if_needed(query_result, key, value)
                    updates_needed = True

            if updates_needed:
                self.pd.write_csv()
        else:
            self.pd.write_json_to_csv(rec)
