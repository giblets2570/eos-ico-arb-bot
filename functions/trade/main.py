import sys, os, datetime, json
from time import time
from should import get_period, collect_transactions, calculate_window_investments, calculate_window_diffs, should_i_buy, save_transactions, time_to_check, should_i_claim
from transact import create_transaction, claim, deposit_amount, deposit
from bitfinex import balance, new_market_order, withdraw
import subprocess

sys.path.append(os.path.join(os.path.dirname(__file__), "pip_modules"))
# sys.path.append("/usr/src/app/functions/trade/pip_modules")

from twilio.rest import Client

# Your Account SID from twilio.com/console
account_sid = os.environ.get("TWILIO_ACCOUNT_SID")
# Your Auth Token from twilio.com/console
auth_token  = os.environ.get("TWILIO_AUTH_TOKEN")

to_phone_number = os.environ.get("TWILIO_TO_PHONE_NUMBER")
from_phone_number = os.environ.get("TWILIO_FROM_PHONE_NUMBER")

client = Client(account_sid, auth_token)

def handle(event, context):
	transactions = collect_transactions()
	if(time_to_check()): # Are we in the last half hour
		print("This is the time to make the investment")
		window_amounts, window_investments = calculate_window_investments(transactions)
		window_diffs = calculate_window_diffs(window_investments)
		if(should_i_buy(window_diffs)): # should I buy the tokens
			print("I should buy")
			period = get_period(time())
			if os.environ.get('AMOUNT'):
				amount = os.environ.get('AMOUNT')
			transaction_url = create_transaction(period)
			message = client.messages.create(
				to=to_phone_number, 
				from_=from_phone_number,
				body="Trade just made for EOS!!! {}".format(transaction_url)
			)
		else:
			message = client.messages.create(
				to=to_phone_number, 
				from_=from_phone_number,
				body="No EOS purchase. Window price too high"
			)
			print("I shouldn't buy")
	elif (should_i_claim()):
		print("CLAIM CLAIM CLAIM")
		print(claim(get_period(time())-1))
	elif deposit_amount() > 0:
		da = deposit_amount()
		print("deposit {}".format(da))
		print(deposit(da))
	elif balance("eos") > 12:
		bal = balance("eos")
		print("EOS to sell: {}".format(bal))
		print(new_market_order("eoseth", bal, "sell"))
	elif balance("eth") > 0.05:
		bal = balance("eth")
		print("ETH to withdraw: {}".format(bal))
		print(withdraw(os.environ.get("ADDRESS_MAIN"), bal))

	save_transactions(transactions)

if os.environ.get("ENV") == "development":
	handle(None, None)