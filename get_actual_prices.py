import sys, os, datetime, json
sys.path.append(os.path.join(os.path.dirname(__file__), "functions/trade/pip_modules"))
import requests
from time import time, sleep

seconds_in_period = 82800
period_zero_end = 1498914000 
max_window = 109
def end_time(period):
	return period * seconds_in_period + period_zero_end

actual_prices = []
for i in range(0, max_window):
	close_time = end_time(i)
	actual_prices.append(json.loads(requests.get("https://min-api.cryptocompare.com/data/pricehistorical?fsym=EOS&ts="+ str(int(close_time)) +"&tsyms=ETH&e=Bitfinex&extraParams=your_app_name").text)["EOS"]["ETH"])
	print (i)
	sleep(1)
print(actual_prices)