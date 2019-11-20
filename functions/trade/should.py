# from etherscan.accounts import Account
import json
import os.path
from datetime import datetime, timedelta
from transact import has_unclaimed
from time import time, sleep
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), "pip_modules"))

import requests
import boto3

contract_address = '0xd0a6e6c54dbc68db5db3a091b171a77407ff7ccf'


key = os.environ.get("ETHERSCAN_KEY")

api_address = "https://api.etherscan.io/api?module=account&action=txlist&address=" + contract_address + "&sort=asc&apikey=" + key
s3_transactions_bucket = os.environ.get("S3_TRANSACTIONS_BUCKET_NAME")

seconds_in_period = 82800
period_zero_end = 1498914000
period = 0

s3 = boto3.resource('s3')
s3_client = boto3.client('s3')

def collect_transactions():
	transactions = []
	obj = s3_client.get_object(Bucket=s3_transactions_bucket, Key='transactions.json')
	transactions = json.loads(obj['Body'].read())
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
	s3.Object(s3_transactions_bucket, 'transactions.json').put(Body=json.dumps(transactions))
	print("Done saving transactions")

def get_period(timestamp):
	period = ((timestamp - period_zero_end) // seconds_in_period) + 1
	if period < 0:
		return 0
	else:
		return int(period)

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
				buy_window = 0
				try:
					buy_window = int(transaction['input'][10:74], base=16)
				except:
					print("failed to parse transaction added to period 0")
					print(transaction)
				if buy_window >= current_window and buy_window in window_amounts:
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

def time_to_check(_time=None):
	# when time() is default arg it seems to be a pointer so does not change each call
	if _time is None:
		_time = time()

	# just check we are in last twenty minutes
	ten_minutes = 10 * 60
	# print(ten_minutes)
	current_period = get_period(_time)
	# print(current_period)

	et = end_time(current_period)
	# print(et)
	secs_left = (et - _time)
	# print(secs_left)
	return secs_left < ten_minutes

	# return _time > (period_zero_end - ten_minutes + (current_period * seconds_in_period))

def should_i_buy(window_diffs):
	current_ico_price = window_diffs['at_close'][-1]
	print("Current ico price is {}".format(current_ico_price))
	last_period_ratio = window_diffs['ratio'][-2]
	print("Last period ratio is {}".format(last_period_ratio))
	two_before_period_ratio = window_diffs['ratio'][-3]
	print("Two before period ratio is {}".format(two_before_period_ratio))
	effective_ratio = two_before_period_ratio * 0.35 + last_period_ratio * 0.65
	print("Effective ratio is {}".format(effective_ratio))
	estimate_ico_price = current_ico_price * effective_ratio
	print("Estimate for ico price is {}".format(estimate_ico_price))
	current_market_price = None
	try:
		current_market_price = json.loads(requests.get("https://min-api.cryptocompare.com/data/price?fsym=EOS&tsyms=ETH&e=Bitfinex&extraParams=your_app_name").text)['ETH']
	except Exception:
		current_market_price = json.loads(requests.get("https://api.bitfinex.com/v2/ticker/tEOSETH").text)[0]
	print("Current market price is {}".format(current_market_price))
	return estimate_ico_price < (current_market_price)

def should_i_claim():
	last_period = get_period(time()) - 1
	return has_unclaimed(last_period)

def end_time(period):
	return period * seconds_in_period + period_zero_end

if __name__ == '__main__':
	transactions = collect_transactions()
	window_amounts, window_investments = calculate_window_investments(transactions)
	window_diffs = calculate_window_diffs(window_investments)
	should_i_buy(window_diffs)
	# def total_seconds(t):
	# 	return (t-datetime.fromtimestamp(0)).total_seconds()

	# _time = datetime(2017, 10, 3, 11, 57, 00)

	# print(time_to_check(total_seconds(_time)))

	# print(_time)
	# print(datetime.fromtimestamp(total_seconds(_time)))
