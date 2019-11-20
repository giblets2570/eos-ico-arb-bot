import sys, os, datetime, json
sys.path.append(os.path.join(os.path.dirname(__file__), "pip_modules"))

import codecs
from ethereum import transactions
import rlp
import requests
from web3 import Web3
import codecs
from Crypto.Hash import keccak

abi = [{"constant":True,"inputs":[{"name":"","type":"uint256"},{"name":"","type":"address"}],"name":"claimed","outputs":[{"name":"","type":"bool"}],"payable":False,"type":"function"},{"constant":False,"inputs":[{"name":"owner_","type":"address"}],"name":"setOwner","outputs":[],"payable":False,"type":"function"},{"constant":True,"inputs":[],"name":"time","outputs":[{"name":"","type":"uint256"}],"payable":False,"type":"function"},{"constant":True,"inputs":[],"name":"totalSupply","outputs":[{"name":"","type":"uint128"}],"payable":False,"type":"function"},{"constant":True,"inputs":[],"name":"foundersAllocation","outputs":[{"name":"","type":"uint128"}],"payable":False,"type":"function"},{"constant":False,"inputs":[{"name":"day","type":"uint256"}],"name":"claim","outputs":[],"payable":False,"type":"function"},{"constant":True,"inputs":[],"name":"foundersKey","outputs":[{"name":"","type":"string"}],"payable":False,"type":"function"},{"constant":True,"inputs":[{"name":"","type":"uint256"},{"name":"","type":"address"}],"name":"userBuys","outputs":[{"name":"","type":"uint256"}],"payable":False,"type":"function"},{"constant":True,"inputs":[{"name":"day","type":"uint256"}],"name":"createOnDay","outputs":[{"name":"","type":"uint256"}],"payable":False,"type":"function"},{"constant":False,"inputs":[],"name":"freeze","outputs":[],"payable":False,"type":"function"},{"constant":True,"inputs":[{"name":"","type":"address"}],"name":"keys","outputs":[{"name":"","type":"string"}],"payable":False,"type":"function"},{"constant":True,"inputs":[],"name":"startTime","outputs":[{"name":"","type":"uint256"}],"payable":False,"type":"function"},{"constant":False,"inputs":[{"name":"authority_","type":"address"}],"name":"setAuthority","outputs":[],"payable":False,"type":"function"},{"constant":True,"inputs":[{"name":"","type":"uint256"}],"name":"dailyTotals","outputs":[{"name":"","type":"uint256"}],"payable":False,"type":"function"},{"constant":True,"inputs":[],"name":"owner","outputs":[{"name":"","type":"address"}],"payable":False,"type":"function"},{"constant":False,"inputs":[],"name":"buy","outputs":[],"payable":True,"type":"function"},{"constant":True,"inputs":[],"name":"openTime","outputs":[{"name":"","type":"uint256"}],"payable":False,"type":"function"},{"constant":True,"inputs":[],"name":"EOS","outputs":[{"name":"","type":"address"}],"payable":False,"type":"function"},{"constant":True,"inputs":[],"name":"today","outputs":[{"name":"","type":"uint256"}],"payable":False,"type":"function"},{"constant":True,"inputs":[],"name":"authority","outputs":[{"name":"","type":"address"}],"payable":False,"type":"function"},{"constant":False,"inputs":[{"name":"eos","type":"address"}],"name":"initialize","outputs":[],"payable":False,"type":"function"},{"constant":True,"inputs":[],"name":"createFirstDay","outputs":[{"name":"","type":"uint256"}],"payable":False,"type":"function"},{"constant":False,"inputs":[],"name":"claimAll","outputs":[],"payable":False,"type":"function"},{"constant":True,"inputs":[{"name":"timestamp","type":"uint256"}],"name":"dayFor","outputs":[{"name":"","type":"uint256"}],"payable":False,"type":"function"},{"constant":False,"inputs":[{"name":"day","type":"uint256"},{"name":"limit","type":"uint256"}],"name":"buyWithLimit","outputs":[],"payable":True,"type":"function"},{"constant":False,"inputs":[],"name":"collect","outputs":[],"payable":False,"type":"function"},{"constant":True,"inputs":[],"name":"numberOfDays","outputs":[{"name":"","type":"uint256"}],"payable":False,"type":"function"},{"constant":False,"inputs":[{"name":"key","type":"string"}],"name":"register","outputs":[],"payable":False,"type":"function"},{"constant":True,"inputs":[],"name":"createPerDay","outputs":[{"name":"","type":"uint256"}],"payable":False,"type":"function"},{"inputs":[{"name":"_numberOfDays","type":"uint256"},{"name":"_totalSupply","type":"uint128"},{"name":"_openTime","type":"uint256"},{"name":"_startTime","type":"uint256"},{"name":"_foundersAllocation","type":"uint128"},{"name":"_foundersKey","type":"string"}],"payable":False,"type":"constructor"},{"payable":True,"type":"fallback"},{"anonymous":False,"inputs":[{"indexed":False,"name":"window","type":"uint256"},{"indexed":False,"name":"user","type":"address"},{"indexed":False,"name":"amount","type":"uint256"}],"name":"LogBuy","type":"event"},{"anonymous":False,"inputs":[{"indexed":False,"name":"window","type":"uint256"},{"indexed":False,"name":"user","type":"address"},{"indexed":False,"name":"amount","type":"uint256"}],"name":"LogClaim","type":"event"},{"anonymous":False,"inputs":[{"indexed":False,"name":"user","type":"address"},{"indexed":False,"name":"key","type":"string"}],"name":"LogRegister","type":"event"},{"anonymous":False,"inputs":[{"indexed":False,"name":"amount","type":"uint256"}],"name":"LogCollect","type":"event"},{"anonymous":False,"inputs":[],"name":"LogFreeze","type":"event"},{"anonymous":False,"inputs":[{"indexed":True,"name":"authority","type":"address"}],"name":"LogSetAuthority","type":"event"},{"anonymous":False,"inputs":[{"indexed":True,"name":"owner","type":"address"}],"name":"LogSetOwner","type":"event"}]
token_contract_abi = [{"constant":True,"inputs":[],"name":"name","outputs":[{"name":"","type":"bytes32"}],"payable":False,"type":"function"},{"constant":False,"inputs":[],"name":"stop","outputs":[],"payable":False,"type":"function"},{"constant":False,"inputs":[{"name":"guy","type":"address"},{"name":"wad","type":"uint256"}],"name":"approve","outputs":[{"name":"","type":"bool"}],"payable":False,"type":"function"},{"constant":False,"inputs":[{"name":"owner_","type":"address"}],"name":"setOwner","outputs":[],"payable":False,"type":"function"},{"constant":True,"inputs":[],"name":"totalSupply","outputs":[{"name":"","type":"uint256"}],"payable":False,"type":"function"},{"constant":False,"inputs":[{"name":"src","type":"address"},{"name":"dst","type":"address"},{"name":"wad","type":"uint256"}],"name":"transferFrom","outputs":[{"name":"","type":"bool"}],"payable":False,"type":"function"},{"constant":True,"inputs":[],"name":"decimals","outputs":[{"name":"","type":"uint256"}],"payable":False,"type":"function"},{"constant":False,"inputs":[{"name":"dst","type":"address"},{"name":"wad","type":"uint128"}],"name":"push","outputs":[{"name":"","type":"bool"}],"payable":False,"type":"function"},{"constant":False,"inputs":[{"name":"name_","type":"bytes32"}],"name":"setName","outputs":[],"payable":False,"type":"function"},{"constant":False,"inputs":[{"name":"wad","type":"uint128"}],"name":"mint","outputs":[],"payable":False,"type":"function"},{"constant":True,"inputs":[{"name":"src","type":"address"}],"name":"balanceOf","outputs":[{"name":"","type":"uint256"}],"payable":False,"type":"function"},{"constant":True,"inputs":[],"name":"stopped","outputs":[{"name":"","type":"bool"}],"payable":False,"type":"function"},{"constant":False,"inputs":[{"name":"authority_","type":"address"}],"name":"setAuthority","outputs":[],"payable":False,"type":"function"},{"constant":False,"inputs":[{"name":"src","type":"address"},{"name":"wad","type":"uint128"}],"name":"pull","outputs":[{"name":"","type":"bool"}],"payable":False,"type":"function"},{"constant":True,"inputs":[],"name":"owner","outputs":[{"name":"","type":"address"}],"payable":False,"type":"function"},{"constant":False,"inputs":[{"name":"wad","type":"uint128"}],"name":"burn","outputs":[],"payable":False,"type":"function"},{"constant":True,"inputs":[],"name":"symbol","outputs":[{"name":"","type":"bytes32"}],"payable":False,"type":"function"},{"constant":False,"inputs":[{"name":"dst","type":"address"},{"name":"wad","type":"uint256"}],"name":"transfer","outputs":[{"name":"","type":"bool"}],"payable":False,"type":"function"},{"constant":False,"inputs":[],"name":"start","outputs":[],"payable":False,"type":"function"},{"constant":True,"inputs":[],"name":"authority","outputs":[{"name":"","type":"address"}],"payable":False,"type":"function"},{"constant":True,"inputs":[{"name":"src","type":"address"},{"name":"guy","type":"address"}],"name":"allowance","outputs":[{"name":"","type":"uint256"}],"payable":False,"type":"function"},{"inputs":[{"name":"symbol_","type":"bytes32"}],"payable":False,"type":"constructor"},{"anonymous":True,"inputs":[{"indexed":True,"name":"sig","type":"bytes4"},{"indexed":True,"name":"guy","type":"address"},{"indexed":True,"name":"foo","type":"bytes32"},{"indexed":True,"name":"bar","type":"bytes32"},{"indexed":False,"name":"wad","type":"uint256"},{"indexed":False,"name":"fax","type":"bytes"}],"name":"LogNote","type":"event"},{"anonymous":False,"inputs":[{"indexed":True,"name":"authority","type":"address"}],"name":"LogSetAuthority","type":"event"},{"anonymous":False,"inputs":[{"indexed":True,"name":"owner","type":"address"}],"name":"LogSetOwner","type":"event"},{"anonymous":False,"inputs":[{"indexed":True,"name":"from","type":"address"},{"indexed":True,"name":"to","type":"address"},{"indexed":False,"name":"value","type":"uint256"}],"name":"Transfer","type":"event"},{"anonymous":False,"inputs":[{"indexed":True,"name":"owner","type":"address"},{"indexed":True,"name":"spender","type":"address"},{"indexed":False,"name":"value","type":"uint256"}],"name":"Approval","type":"event"}]

infuraKey = os.environ.get('INFURA_KEY')

nets = {
	"main": {
		"address": os.environ.get("ADDRESS_MAIN"),
		"contract": "0xd0a6e6c54dbc68db5db3a091b171a77407ff7ccf",
		"privkey": os.environ.get("PRIVATE_KEY_MAIN"),
		"api": "https://api.etherscan.io",
		"key": "A98R7W5SGC5MGK92XD7TETB7HPPJ8REAPX",
		"provider": "https://mainnet.infura.io/" + infuraKey,
		"token_contract": "0x86Fa049857E0209aa7D9e616F7eb3b3B78ECfdb0",
		"deposit_address": os.environ.get("BITFINEX_DEPOSIT_ADDRESS")
	},
	"kovan": {
		"contract": "0x2b0df80a0ddca2c3785b0e5813e4c7722d8ef01d",
		"address": os.environ.get("ADDRESS_KOVAN"),
		"privkey": os.environ.get("PRIVATE_KEY_KOVAN"),
		"api": "https://kovan.etherscan.io",
		"key": "MAIRIBZXP4IGSC6D25IUPBQ48TQPC3XYHS",
		"provider": "https://kovan.infura.io/" + infuraKey,
		"token_contract": "0x6c3ddfec3bdd7b7226593abb6fc0062c9a92bb2f",
		"deposit_address": os.environ.get("BITFINEX_DEPOSIT_ADDRESS")
	}
}

def signTransaction(to, value, privkey, nonce=0, gasPrice=80000000000, gas=21000, data=""):
	print(to, value, privkey, nonce, gasPrice, gas, data)
	if gasPrice < 80000000000:
		gasPrice = 80000000000
	try:
		transaction = transactions.Transaction(nonce, gasPrice, gas, to, value, data).sign(privkey)
		# sign = rlp.encode(transaction).hex()
		sign = codecs.encode(rlp.encode(transaction), 'hex')
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

def create_transaction_data(period):
	# Buy Limit Method
	method = b'buyWithLimit(uint256,uint256)'
	# method = b"buy()"
	s = keccak.new(digest_bits=256)
	s.update(method)
	method_hash = s.hexdigest()

	data = str(method_hash[:8] + fill_up_bytes(format(period, '02x')) + fill_up_bytes(format(0, '02x')))
	raw_bytes = codecs.decode(data, 'hex')
	return raw_bytes

def has_unclaimed(period, net='main'):
	web3 = Web3(Web3.HTTPProvider(nets[net]['provider']))
	contract = web3.eth.contract(address=nets[net]['contract'], abi=abi)
	if (not contract.call().claimed(period, nets[net]['address'])):
		return 0 < contract.call().userBuys(period, nets[net]['address'])
	return False

def claim(period, net='main'):
	web3 = Web3(Web3.HTTPProvider(nets[net]['provider']))
	nonce = web3.eth.getTransactionCount(nets[net]['address'])
	method = b'claim(uint256)'
	# method = b"buy()"
	s = keccak.new(digest_bits=256)
	s.update(method)
	method_hash = s.hexdigest()

	data = str(method_hash[:8] + fill_up_bytes(format(period, '02x')))
	raw_bytes = codecs.decode(data, 'hex')
	result = signTransaction(nets[net]['contract'],0,nets[net]['privkey'],nonce=nonce,data=raw_bytes,gas=100000,gasPrice=(web3.eth.gasPrice*2))
	if 'sign' in result:
		try:
			result = json.loads(broadcastTransaction(nets[net]['api']+"/api",nets[net]['key'],result['sign']))
			return(nets[net]['api']+"/tx/"+result['result'])
		except Exception as e:
			print(e)

def deposit_amount(net='main'):
	web3 = Web3(Web3.HTTPProvider(nets[net]['provider']))
	contract = web3.eth.contract(address=nets[net]['token_contract'], abi=token_contract_abi)
	return contract.call().balanceOf(nets[net]['address'])


def deposit(amount, net='main'):
	web3 = Web3(Web3.HTTPProvider(nets[net]['provider']))
	nonce = web3.eth.getTransactionCount(nets[net]['address'])
	method = b'transfer(address,uint256)'

	# method = b"buy()"
	s = keccak.new(digest_bits=256)
	s.update(method)
	method_hash = s.hexdigest()

	data = str(method_hash[:8] + fill_up_bytes(nets[net]['deposit_address'][2:]) + fill_up_bytes(format(amount, '02x')))
	raw_bytes = codecs.decode(data, 'hex')
	result = signTransaction(nets[net]['token_contract'],0,nets[net]['privkey'],nonce=nonce,data=raw_bytes,gas=100000,gasPrice=(web3.eth.gasPrice*2))
	if 'sign' in result:
		try:
			result = json.loads(broadcastTransaction(nets[net]['api']+"/api",nets[net]['key'],result['sign']))
			return(nets[net]['api']+"/tx/"+result['result'])
		except Exception as e:
			print(e)
# 0.0259409821 ETH ~= 8 USD
def create_transaction(period,net='main',save_amount=25940982100000000):
	web3 = Web3(Web3.HTTPProvider(nets[net]['provider']))
	nonce = web3.eth.getTransactionCount(nets[net]['address'])
	amount = (web3.eth.getBalance(nets[net]['address']) - save_amount)

	result = signTransaction(nets[net]['contract'],amount,nets[net]['privkey'],nonce=nonce,data=create_transaction_data(period),gas=100000,gasPrice=(web3.eth.gasPrice*4))
	print(result)

	if 'sign' in result:
		try:
			result = json.loads(broadcastTransaction(nets[net]['api']+"/api",nets[net]['key'],result['sign']))
			print(nets[net]['api']+"/tx/"+result['result'])
			return(nets[net]['api']+"/tx/"+result['result'])
		except Exception as e:
			print(e)


if __name__ == '__main__':
	net = 'transfer'
	period = 294
	create_transaction(period,net=net)

# 	uint     _numberOfDays,
    # uint128  _totalSupply,
    # uint     _openTime,
    # uint     _startTime,
    # uint128  _foundersAllocation,
    # string   _foundersKey

# 	[350, 100000, 1498482000, 1498914000, 50, "tom"]
# 	0x2b0df80a0ddca2c3785b0e5813e4c7722d8ef01d
