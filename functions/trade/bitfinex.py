# from etherscan.accounts import Account
import json
import os.path
import sys
import base64
import hmac
import hashlib
sys.path.append(os.path.join(os.path.dirname(__file__), "pip_modules"))

from time import time
import requests
import boto3

API_KEY = os.environ.get("BITFINEX_API_KEY")
API_SECRET = os.environ.get("BITFINEX_API_SECRET")
URL = "https://api.bitfinex.com"

def make_request(payload): # packs and signs the payload of the request.
	payload["nonce"] = str(time() * 1000000)

	j = json.dumps(payload).encode()
	data = base64.standard_b64encode(j)

	h = hmac.new(API_SECRET.encode(), data, hashlib.sha384)
	signature = h.hexdigest()

	signed_payload = {
		"X-BFX-APIKEY": API_KEY,
		"X-BFX-SIGNATURE": signature,
		"X-BFX-PAYLOAD": data
	}
	print(payload)
	r = requests.post(URL + payload["request"], headers=signed_payload, verify=True)
	return r.text

def balance(currency):
	payload = {
		"request":"/v1/balances",
	}
	return float([wallet for wallet in json.loads(make_request(payload)) if wallet['currency'] == currency and wallet['type'] == 'exchange'][0]['available'])

def orders():
	payload = {
		"request":"/v1/orders",
	}
	return json.loads(make_request(payload))

def new_market_order(pair, amount, action):
	payload = {
		"request": '/v1/order/new',
		"symbol": pair.upper(),
		"amount": str(amount),
		"price": '1000',
		"exchange": 'bitfinex',
		"side": action,
		"type": 'exchange market'
	}
	return json.loads(make_request(payload))

def withdraw(withdraw_address, amount):
	amount -= 0.01
	payload = {
		"request": "/v1/withdraw",
		"withdraw_type": "ethereum",
		"walletselected": "exchange",
		"amount": str(amount),
		"walletselected": "exchange",
		"address": withdraw_address
	}
	return json.loads(make_request(payload))



if __name__ == '__main__':
	bal = balance("eos")
	print(bal)
	if bal > 12:
		print("EOS to sell: {}".format(bal))
		print(new_market_order("eoseth", bal, "sell"))

# print("ETH: {}".format(balance("eth")))
# print("EOS: {}".format(balance("eos")))
# print(len(orders())>0)
# print(new_market_order("EOSETH", 12.0, "sell"))
# print(withdraw("0x04A942a038379070941dE35A8fd3Ee1E6518060C", 0.05))