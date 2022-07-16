from bitcoin import * 
from json import loads
from requests import get
import sqlite3  
import time
from pprint import pprint


class manageWallet():
    def __init__(self):
        
        # Initialize connection to database 
        self.connection = sqlite3.connect('user_address_db.db')

        self.cursor = self.connection.cursor()

        # Uncomment the below two lines initialize class if fresh database needed - 
        self.cursor.execute("DROP TABLE IF EXISTS address_details")
        self.cursor.execute("DROP TABLE IF EXISTS txn")

        # Keep track of balance at each address location and how up to date it is 
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS address_details(
                          ADDR TEXT, 
                          BALANCE INT, 
                          LAST_UPDATED TEXT)''')
        
        # keep track of all transactions which involve one of teh addresses user is following 
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS txn(
                          TXN_ID TEXT , 
                          SOURCE_ADDR TEXT , 
                          DEST_ADDR TEXT ,
                          AMOUNT INT)''')

        self.connection.commit() 
    

    def getBalance(self, address, most_updated):

        params = [address]

        # Initialize balance to 0 
        balance = 0 

        # If user does not want the most updated value, we will serve the request by querying the database 
        if not most_updated:
            check = self.cursor.execute('''SELECT * from address_details WHERE ADDR = ?''', [address])
            check_values = check.fetchall() 
            if not check_values:
                print ("Request failed. Try again")
                return

            values = self.cursor.execute('''SELECT BALANCE, LAST_UPDATED FROM address_details WHERE ADDR=?''', params)
            balance,timestamp = values.fetchall()[0]
            print(f'The balance is {balance} as of time {timestamp}')
            return balance

        # If user wants teh most updated value, we make a network call to get the data using blockchain.com's API 
        else:
            url = 'https://blockchain.info/balance?active='
            btc_addr = address 
            try:
                request = get(url+btc_addr)
                balance = loads(request.content)[address]['final_balance']
            except:
                raise Exception("Request failed. Try again")

        return balance 
    

    def addAddress(self, address): 
        
        # We verify whether the address the user is trying to add has already been added or not. 
        check = self.cursor.execute('''SELECT * FROM address_details WHERE ADDR=?''', [address])
        check_values = check.fetchall() 
        if check_values:
            print("Address already added")
            return
        
        # Make a call to get the most updated balance. 
        # If the user has specified an incorrect address, this call will fail with an Exception
        balance = self.getBalance(address, True)

        # Get the current time
        current_time = time.ctime()

        params = (address, balance, current_time)

        # Initialize an entry in the DB 
        self.cursor.execute('''INSERT INTO address_details(
                          ADDR, BALANCE, LAST_UPDATED 
                          ) 
                          VALUES 
                          (?, ?, ?)''', params)
        
        self.connection.commit()
    

    def viewAddresses(self):

        # Get all the addresses user is tracking in the database
        addr_reference = self.cursor.execute('''SELECT ADDR FROM address_details''')

        addresses = addr_reference.fetchall()

        return addresses
    

    def removeAddress(self, address):
        
        params = (address)

        # remove the address from the address_details database
        self.cursor.execute('''DELETE FROM address_details WHERE ADDR = ?''', [params])

        # Remove all occurrences of the address from txn database where the address was either the source or the destination 
        self.cursor.execute('''DELETE FROM txn WHERE SOURCE_ADDR = ? OR DEST_ADDR = ?''', [params,params]) 

        self.connection.commit() 

    
    def getTxns(self, address, most_updated):

        params = [address,address]
        result = []
        
        # If user does not require the most updated version, we will fetch from the DB 
        if not most_updated: 
            check = self.cursor.execute('''SELECT * from address_details WHERE ADDR = ?''', [address])
            check_values = check.fetchall() 
            if not check_values:
                print ("Invalid address")
                return

            values = self.cursor.execute('''SELECT TXN_ID from txn WHERE SOURCE_ADDR = ? UNION SELECT TXN_ID from txn WHERE DEST_ADDR = ?''', params)
            result = values.fetchall()

            return result

        # If user requires the most updated version, we make a network call to fetch it using Blockchain.com's API. 
        else:
            url = 'https://blockchain.info/rawaddr/'
            btc_addr = address
            try:
                request = get(url+btc_addr)
                txns = loads(request.content)['txs']
            except:
                raise Exception("Request failed. Try again")

            result = [] 
            for txn in txns:
                result.append(txn['hash'])

        return result



# UNCOMMENT FOR TESTING PURPOSES
# object = manageWallet()
# object.addAddress('1EymUzELRQR7v9Sko54MjpEUDohtCJkHXa')
# object.addAddress('33U8mcdkjCMoMsHAntjBVyE5wTr3BRn5ov')
# object.addAddress('bc1q8k82aw4mwmxcc0mrmgg2xe58hwk56jqzekpaf6')

# object.viewAddresses()

# object.getBalance('1EymUzELRQR7v9Sko54MjpEUDohtCJkHXa', False)
# object.getBalance('33U8mcdkjCMoMsHAntjBVyE5wTr3BRn5ov', False)
# object.getBalance('bc1q8k82aw4mwmxcc0mrmgg2xe58hwk56jqzekpaf6', False)




