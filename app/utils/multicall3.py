import eth_abi

from utils.w3 import get_w3


class Multicall3:
    def __init__(self, rpc_url, multicall3_address):
        self.w3 = get_w3(rpc_url)

        abi = [{"inputs": [{"internalType": "bool", "name": "requireSuccess", "type": "bool"}, {"components": [{"internalType": "address", "name": "target", "type": "address"},{"internalType": "bytes", "name": "callData", "type": "bytes"}],"internalType": "struct Multicall3.Call[]", "name": "calls", "type": "tuple[]"}], "name": "tryAggregate","outputs": [{"components": [{"internalType": "bool", "name": "success", "type": "bool"},{"internalType": "bytes", "name": "returnData","type": "bytes"}], "internalType": "struct Multicall3.Result[]","name": "returnData", "type": "tuple[]"}], "stateMutability": "payable","type": "function"}]
        self.m3 = self.w3.eth.contract(multicall3_address, abi=abi)

    def _encode_to_calls(self, funcs):
        calls = []
        for func in funcs:
            contract = self.w3.eth.contract(func.address, abi=[func.abi])
            calls.append((func.address, contract.encodeABI(func.fn_name, args=func.args)))

        return calls

    def _decode_to_results(self, funcs, data):
        results = []
        for i, _data in enumerate(data):
            types = [item["type"] for item in funcs[i].abi["outputs"]]
            if len(types) == 0:
                results.append(None)
            else:
                if _data[0]:
                    decoded_data = eth_abi.decode(types, _data[1])
                    if len(types) == 1:
                        results.append(decoded_data[0])
                    else:
                        results.append(list(decoded_data))
                else:
                    results.append(False)

        return results

    def try_aggregate(self, require_success, funcs):
        calls = self._encode_to_calls(funcs)

        data = self.m3.functions.tryAggregate(require_success, calls).call()

        return self._decode_to_results(funcs, data)
