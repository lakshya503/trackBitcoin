This project was coded in Python 3.9.6 but it should be compatible with any Python 3+. No other special requirements to run this project. 


# trackBTC.py 
This file holds all the key functioncality of the project. At a high level, I make use of two tables and Blockchain.com's APIs to serve the user. The two databases used are - 

1) address_details (address, balance, timestamp) - This table has address as a primary key and is used to amintain the balance of each address as of a current timestamp 
2) txn (txn_id, source_addr, dest_addr, amount) - This table has txn_id as a primary key and is used to keep track of all the transactions that a certain address has been involved in. 

The two API calls used are - 
1) https://blockchain.info/balance?active= : This is used to get the most updated balance. 
2) https://blockchain.info/rawaddr/ : This is used to get all transactions assosciated with a certain address.


The user can initialize a manageWallet object which will give them access to the following functions - 

1) getBalance(self, address, most_updated)
This function allows the user to get the balance of a specific address. They need to specify whether they want the most updated value or not. 
If the user wants the most updated value, we make a network call using Blockchain.com's API to return the most updated balance. If they decide they don't want the latest values, the program will query the address_details table and return the balance as of the previously updated time. 

2) addAddress(self, address)
This function allows the user to add addresses to track. When they try to add an address, a network call is made to get the most updated balance. I store this address in the address_details table along with the most recent balance and the current timestamp. 

3) viewAddresses() 
This function allows the user to see all the addresses that they are tracking. 

4) removeAddress(address) 
This function allows the user to remove an address that they no longer want to track. This function will delete the entry from the address_details table as well as all the rows in the txn table where this address is either a source address or a destination address. Ideally you would want to synchronize after this step becuase of the following situation - 
User tracks address A and address B. 
address A and address B are involved in a transaction and have an entry logged in txn table. 
User removes address A -- this will delete the previous step's transaction details and hence address B will not have all the transactions listed in txn table. TO synchronize, we can run background.py. 

5) getTxns(address, most_updated) 
This function allows the user to get all the transactions assosciated with an address. They need to specify whether they want the most updated list or not. If the user wants the most updated list, we make a network call using Blockchain.com's API which will fetch all the transactions that the address has been involved in. The program will return a list of transaction_ids. If the user does not want the most updated list, the program will query the txn table and fetch all the transaction ids where the current address was either the source address or the destination address. 


# background.py 
This file is intended to be a background job and can be set up as a cron job to run at certain intervals. This file will synchronize our database with all the updated values. The way it works is the program will fetch all the addresses that the user is tracking and iterate through that list. For each address, I make two network calls - to get the balance and to get the transactions. The results are collected and the tables are updated with the most recent values. Currently, I only have the functionality to synchronize the balances. My IP is rate limited for the API which is used to get the transactions. Once I am no longer blocked, I can synchronize all transactions as well. 
