import json
import os


class JsonHandler:
    def __init__(self, _type):
        self._type = _type
        if self._type == "address2account_id":
            self.filename = "data/cache/address2account_id.json"
        self.content = {}
        self.read_json()

    def read_json(self):
        fee_dir = os.path.dirname(self.filename)
        if not os.path.exists(fee_dir):
            os.makedirs(fee_dir)

        if not os.path.exists(self.filename):
            self.write_json()
        else:
            with open(self.filename, "r", encoding="utf-8") as f:
                self.content = json.load(f)

    def write_json(self):
        with open(self.filename, "w", encoding="utf-8") as f:
            json.dump(self.content, f, separators=(",", ": "), ensure_ascii=False, indent=4)

    def get_content(self, key):
        return self.content.get(key, None)

    def update_content(self, key, value):
        self.content[key] = value
