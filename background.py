# This file is intended to run as a background process and synchronize the wallets data in the database at a certain frequency. 
# Currently incomplete as my IP address is being rate limited. 

from json import loads
from requests import get
import sqlite3  
import time
from pprint import pprint


connection = sqlite3.connect('user_address_db.db')

cursor = connection.cursor()

# query db to get all addresses. 
addr_reference = cursor.execute('''SELECT ADDR from address_details''')
addresses = addr_reference.fetchall() 

# Iterate through every address in the database and synchronize with latest values. 
for address in addresses:

    # We need two API calls - one to sync the transactions, other to sync the balances. 
    url_txn = 'https://blockchain.info/rawaddr/'
    url_balance = 'https://blockchain.info/balance?active='

    btc_addr = address[0]
    
    
    request_balance = get(url_balance+btc_addr)

    # UNCOMMENT THE BELOW TWO LINES WHEN NO LONGER RATE LIMITED. 
    # request_txn = get(url_txn+btc_addr)
    # txns = loads(request.content)['txs']

    # Get the most updated balance using the API call
    balance = loads(request_balance.content)[btc_addr]['final_balance']

    cur_timestamp = time.ctime()
    params = [btc_addr, balance, cur_timestamp]

    # Update the values in the address_details database. 
    cursor.execute('''INSERT OR REPLACE INTO address_details (
                      ADDR, BALANCE, LAST_UPDATED) VALUES (
                      ?, ?, ?)''', params)
    
    
    # INCOMPLETE DUE TO RATE LIMIT 
    # Make API calls to find all the txns of this address - Blockchain.com's API ('https://blockchain.info/rawaddr/') can be used.
    # Extract transaction_id, source_address, destination_address and amount fields of txn table - The API result can be used to query the result for these details. 
    # Store those paramaeters in the txn table using cursor.execute statement. 
    # This will synchronize the latest transactions of all the addresses that the user is tracking. 


