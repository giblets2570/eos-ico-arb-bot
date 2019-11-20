# from etherscan.accounts import Account
import requests
import json
import os.path
from datetime import datetime, timedelta
import plotly.offline as pyoff
from time import time, sleep
import boto3
import plotly.graph_objs as go

contract_address = '0xd0a6e6c54dbc68db5db3a091b171a77407ff7ccf'
key = 'A98R7W5SGC5MGK92XD7TETB7HPPJ8REAPX'

api_address = "https://api.etherscan.io/api?module=account&action=txlist&address=" + contract_address + "&sort=asc&apikey=" + key

seconds_in_period = 82800
period_zero_end = 1498914000
period = 0

# Let's use Amazon S3
s3 = boto3.resource('s3')                                             

def timeit(method):

    def timed(*args, **kw):
        ts = time()
        result = method(*args, **kw)
        te = time()

        print('%r (%r, %r) %2.2f sec' % (method.__name__, args, kw, te-ts))
        return result

    return timed


def collect_transactions():
	transactions = []
	s3.Bucket('ethereum-transactions').download_file('transactions.json', '/tmp/transactions-temp.json')
	if os.path.isfile("/tmp/transactions-temp.json"):
		with open("/tmp/transactions-temp.json") as data_file:
			transactions = json.load(data_file)
			start_block = transactions[-1]["blockNumber"]
			print(str(len(transactions)) + " loaded from file")

	more_transactions = True
	while more_transactions:
		response = json.loads(requests.get(api_address + "&startblock=" + start_block).text)
		if response["message"] == "OK" and response["result"][-1]["blockNumber"] != start_block:
			transactions += response["result"]
			start_block = response["result"][-1]["blockNumber"]
			print(start_block)
		else:
			more_transactions = False 
	transactions = remove_duplicate_transactions(transactions)
	print("Collected transactions")
	return transactions

def remove_duplicate_transactions(transactions):
	seen_transactions = {}
	to_delete = []
	for transaction_index, transaction in enumerate(transactions):
		transaction_id = transaction['blockNumber'] + '_' + transaction['transactionIndex']
		try:
			seen_transactions[transaction_id]
			to_delete.append(transaction_index)
		except Exception:
			seen_transactions[transaction_id] = True
		if (transaction_index % 10000) == 0:
			print(str((transaction_index/len(transactions))*100) + "%")
	for index in reversed(to_delete):
		transactions.pop(index)
	return transactions

def save_transactions(transactions):
	print("Saving transactions")
	with open('/tmp/transactions-temp.json', 'w') as outfile:
		json.dump(transactions, outfile)
	s3_client.upload_file('/tmp/transactions-temp.json', 'ethereum-transactions', 'transactions.json')
	print("Done saving transactions")

def get_period(timestamp):
	period = ((timestamp - period_zero_end) // seconds_in_period) + 1
	if period < 0:
		return 0
	else:
		return int(period)

def time_to_check():
	return (seconds_in_period - (time() % seconds_in_period)) < (seconds_in_period / 23)

def calculate_window_investments(transactions):
	window_amounts = {}
	window_investments = {}
	for i in range(0, 351):
		window_amounts[i] = 0
		window_investments[i] = {'times': [], 'prices': []}
	# Period 0 end 1498914000
	for transaction_index, transaction in enumerate(transactions):
		if transaction['isError'] == '0':
			current_window = get_period(int(transaction['timeStamp']))
			if (transaction['input'][:10] == "0xe0cb3aa0"):
				buy_window = int(transaction['input'][10:74], base=16)
				if buy_window >= current_window:
					window_amounts[buy_window] += float(transaction['value'])/1000000000000000000
					window_investments[buy_window]['times'].append(datetime.fromtimestamp(int(transaction['timeStamp'])))
					window_investments[buy_window]['prices'].append(window_amounts[buy_window])
			else:
				window_amounts[current_window] += float(transaction['value'])/1000000000000000000
				window_investments[current_window]['times'].append(datetime.fromtimestamp(int(transaction['timeStamp'])))
				window_investments[current_window]['prices'].append(window_amounts[current_window])
		if (transaction_index % 10000) == 0:
			print(str((transaction_index/len(transactions))*100) + "%")
	return window_amounts, window_investments

def calculate_window_diffs(window_investments):
	window_diffs = {'windows': [], 'before_close': [], 'at_close': [], 'estimate': [], 'ratio': []}

	current_period = get_period(time())
	# We get plus 1 so we can get the current period that is about to close.
	# For this period, at_close will be the current price
	for i in range(0, current_period+1):
		finish_time = window_investments[i]['times'][-1]
		check_index = -2
		while True:
			if window_investments[i]['times'][check_index] < (finish_time - timedelta(minutes=3)):
				break
			else:
				check_index -= 1
		window_diffs['windows'].append(i)
		window_diffs['before_close'].append(1/(2000000.0/window_investments[i]['prices'][check_index]))
		window_diffs['at_close'].append(1/(2000000.0/window_investments[i]['prices'][-1]))
		window_diffs['ratio'].append(window_diffs['at_close'][-1] / window_diffs['before_close'][-1])
		if i > 0:
			window_diffs['estimate'].append(window_diffs['ratio'][-2]*window_diffs['before_close'][-1])
		else:
			window_diffs['estimate'].append(0)
	return window_diffs


def should_i_buy(window_diffs):
	current_ico_price = window_diffs['at_close'][-1]
	last_period_ratio = window_diffs['ratio'][-2]
	estimate_ico_price = current_ico_price * last_period_ratio
	current_market_price = json.loads(requests.get("https://min-api.cryptocompare.com/data/price?fsym=EOS&tsyms=ETH&e=Bitfinex&extraParams=your_app_name").text)['ETH']

	return estimate_ico_price < (current_market_price * 0.9)

@timeit
def run_total():
	transactions = collect_transactions()
	print(time_to_check())
	window_amounts, window_investments = calculate_window_investments(transactions)
	window_diffs = calculate_window_diffs(window_investments)
	print(should_i_buy(window_diffs))

def plot():
	for i in range(0, 82):
		try:
			py.plot([go.Scatter(x=window_investments[i]['times'], y=window_investments[i]['prices'])], filename=('window_' + str(i)))
		except:
			pass

	# Here I'm finding the exchange prices 
	actual_prices = []
	for i in range(0, 82):
		close_time = (window_investments[i]['times'][-1] - datetime.utcfromtimestamp(0)).total_seconds()
		actual_prices.append(json.loads(requests.get("https://min-api.cryptocompare.com/data/pricehistorical?fsym=EOS&ts="+ str(int(close_time)) +"&tsyms=ETH&e=Bitfinex&extraParams=your_app_name").text)["EOS"]["ETH"])
		sleep(1)

	window_diffs = {'windows': [], 'before_close': [], 'at_close': [], 'estimate': [], 'market_at_close': actual_prices, 'ratio': []}

	for i in range(0, 82):
		finish_time = window_investments[i]['times'][-1]
		check_index = -2
		while True:
			if window_investments[i]['times'][check_index] < (finish_time - timedelta(minutes=3)):
				break
			else:
				check_index -= 1
		window_diffs['windows'].append(i)
		window_diffs['before_close'].append(1/(2000000.0/window_investments[i]['prices'][check_index]))
		window_diffs['at_close'].append(1/(2000000.0/window_investments[i]['prices'][-1]))
		window_diffs['ratio'].append(window_diffs['at_close'][-1] / window_diffs['before_close'][-1])
		if i > 0:
			window_diffs['estimate'].append(window_diffs['ratio'][-2]*window_diffs['before_close'][-1])
		else:
			window_diffs['estimate'].append(0)

	print("Plotting")
	before_trace = go.Scatter(
		x=window_diffs['windows'],
		y=window_diffs['before_close'],
		name = 'Before Close',
		mode = 'markers',
		marker = dict(
			size = 5,
			color = 'rgba(152, 0, 0, 1)'
		)
	)

	at_trace = go.Scatter(
		x=window_diffs['windows'],
		y=window_diffs['at_close'],
		name = 'At Close',
		mode = 'markers',
		marker = dict(
			size = 5,
			color = 'rgba(255, 182, 193, 1)'
		)
	)

	estimate = go.Scatter(
		x=window_diffs['windows'],
		y=window_diffs['estimate'],
		name = 'Estimate based on check',
		mode = 'markers',
		marker = dict(
			size = 5,
			color = 'rgba(0, 0, 0, 1)'
		)
	)

	market_at_close = go.Scatter(
		x=window_diffs['windows'],
		y=window_diffs['market_at_close'],
		name = 'Market price at close',
		mode = 'markers',
		marker = dict(
			size = 5,
			color = 'rgba(100, 100, 100, 1)'
		)
	)


	# ratio = go.Scatter(
	# 	x=window_diffs['windows'],
	# 	y=window_diffs['ratio'],
	# 	name = 'Ratio',
	#     mode = 'markers',
	#     marker = dict(
	#         size = 5,
	#         color = 'rgba(0, 0, 0, 1)'
	#     )
	# )
	data = [before_trace, at_trace, estimate, market_at_close]

	layout = dict(title = 'Styled Scatter',
				  yaxis = dict(zeroline = False),
				  xaxis = dict(zeroline = False)
				 )

	fig = dict(data=data, layout=layout)
	pyoff.plot(fig, filename='styled-scatter')

# https://min-api.cryptocompare.com/data/pricehistorical?fsym=EOS&ts=1503734400&tsyms=ETH&e=Bitfinex&extraParams=your_app_name

	# if int(transaction['timeStamp']) < 1498996800:
	# 	if (transaction['input'][:10] == "0xe0cb3aa0") and (int(transaction['input'][10:74], base=16) != 1):
	# 		pass
	# 	elif transaction['isError'] == '0':


# methods = {}
# for transaction in transactions:
# 	if len(transaction['input']) > 9:
# 		methods[transaction['input'][:10]] = transaction['hash']


# '0xf2c298be': 'register(string key)', 
# '0xa6f2ae3a': 'buy()', 
# '0x70a08231': 'balanceOf(address)', 
# '0x7a9e5e4b': 'setAuthority(address authority_)', 
# '0xddd5e1b2': 'claim(uint256 _blockNumber, address forCreditTo)', 
# '0x62a5af3b': 'freeze()', 
# '0x13af4035': 'setOwner(address owner_)', 
# '0xe5225381': 'collect()', 
# '0x095ea7b3': 'approve(address _spender, uint256 _value)', 
# '0xa9059cbb': 'transfer(address _to, uint256 _value)', 
# '0x379607f5': 'claim(uint256 day)', 
# '0xe0cb3aa0': 'buyWithLimit(uint256 day, uint256 limit)', 
# '0xc4d66de8': 'initialize(address eos)', 
# '0xb4427263': 'createTokens()', 
# '0x946941ec': 'Contribute(bytes24 tezos_pkh_and_chksum)', 
# '0x1e83409a': 'claim(address owner)', 
# '0x23b872dd': 'transferFrom(address _from, address _to, uint256 _value)', 
# '0x99e9376c': 'buyWithCustomerId(uint128 customerId)', 
# '0x0c77a697': 'claimFounders()', 
# '0xd1058e59': 'claimAll()' 


# u'input': u'0xe0cb3aa000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000'
# Function: buyWithLimit(uint256 day, uint256 limit)

# MethodID: 0xe0cb3aa0
# [0]:0000000000000000000000000000000000000000000000000000000000000000
# [1]:0000000000000000000000000000000000000000000000000000000000000000
# 0xe0cb3aa0 buy with limit


# look at all the potential buy methods
# sum up these methods plus no methods for a single window and see if the total ETh matches the eosscan eth

# import plotly.plotly as py
# import plotly.graph_objs as go
# py.iplot([go.Scatter(x=window_investments[1]['times'], y=window_investments[1]['prices'])], filename='line')


if __name__ == '__main__':
	run_total()
	# Print out bucket names
