import json, requests

def getblock(block_hash):
	return wallet_fetch({"method": "getblock", "params":[block_hash]})

def getblockhash(block_index):
	return wallet_fetch({"method": "getblockhash", "params":[block_index]})

def getinfo():
	return wallet_fetch({"method":"getinfo"})

def getnetworkhashps(block_index=None):
	return ""

def getrawtransaction(tx_id, verbose=1):
	return wallet_fetch ({"method":"getrawtransaction","params":[tx_id, verbose]})

def wallet_fetch(request_array):
	info = requests.post("http://127.0.0.1:28332/", auth=("", "boing9884"), data=json.dumps(request_array), headers={'content-type': 'application/json'}).json()
	if "error" in info and info["error"] is not None:
		raise Exception(info["error"]["message"])
	return info["result"]
