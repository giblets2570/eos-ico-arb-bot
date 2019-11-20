import json
import urllib.request
from ethereum import transactions
import rlp
import requests
import sha3
import codecs

from web3 import Web3

nets = {
	"main": {
		"address": "0x006DA85075cf27348CD295Dc66b3F0bbD5399a5C",
		"contract": "0xd0a6e6c54dbc68db5db3a091b171a77407ff7ccf",
		"privkey": open("./privatereal.txt").read(),
		"api": "https://api.etherscan.io",
		"key": "A98R7W5SGC5MGK92XD7TETB7HPPJ8REAPX",
		"provider": "https://mainnet.infura.io/VB6w0UngxVr7YK5Zkatv"
	},
	"kovan": {
		"contract": "0x2b0df80a0ddca2c3785b0e5813e4c7722d8ef01d",
		"address": "0x8aDe41C465fa645d84Df4e319524E1F9Fa366325",
		"privkey": open("./privatetest.txt").read(),
		"api": "https://kovan.etherscan.io",
		"key": "MAIRIBZXP4IGSC6D25IUPBQ48TQPC3XYHS",
		"provider": "https://kovan.infura.io/VB6w0UngxVr7YK5Zkatv"
	}
}

def signTransaction(to, value, privkey, nonce=0, gasPrice=20000000000, gas=21000, data=""):
	try:
		transaction = transactions.Transaction(nonce, gasPrice, gas, to, value, data).sign(privkey)
		sign = rlp.encode(transaction).hex()
		return { "error": False, "sign": sign }
	except Exception as msg:
		return { "error": True, "message":msg }


def broadcastTransaction(api_address, key, sign):
	url = api_address + "?module=proxy&action=eth_sendRawTransaction&apikey=" + key
	payload = {"hex": sign}
	result = requests.post(url, data=payload)
	return result.text

def fill_up_bytes(data):
	while len(data) < 64:
		data = "0" + data
	return data

def create_transaction_data():
	# Buy Limit Method
	method = b'buyWithLimit(uint256,uint256)'
	# method = b"buy()"
	s = sha3.keccak_256()
	s.update(method)
	method_hash = s.hexdigest()

	data = str(method_hash[:8] + fill_up_bytes(format(294, '02x')) + fill_up_bytes(format(0, '02x')))
	raw_bytes = codecs.decode(data, 'hex')
	return raw_bytes

def create_transaction(net='main'):

	web3 = Web3(Web3.HTTPProvider(nets[net]['provider']))
	nonce = web3.eth.getTransactionCount(nets[net]['address'])

	result = signTransaction(nets[net]['contract'],10000000000000000,nets[net]['privkey'],nonce=nonce,data=create_transaction_data(),gas=100000)

	if 'sign' in result:
		try:
			result = json.loads(broadcastTransaction(nets[net]['api']+"/api",nets[net]['key'],result['sign']))
			print(nets[net]['api']+"/tx/"+result['result'])
			return result
		except Exception as e:
			print(e)

if __name__ == '__main__':
	net = 'kovan'
	create_transaction(net)
# 		  uint     _numberOfDays,
#         uint128  _totalSupply,
#         uint     _openTime,
#         uint     _startTime,
#         uint128  _foundersAllocation,
#         string   _foundersKey

# [350, 100000, 1498482000, 1498914000, 50, "tom"]
# 0x2b0df80a0ddca2c3785b0e5813e4c7722d8ef01d