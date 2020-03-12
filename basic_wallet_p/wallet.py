import requests

class Wallet():
    def __init__(self, id):
        self.id = id
        self.chain = None
        self.server = "http://localhost:5000"
        self.balance = 0


    # SETTER METHODS
    def change_id(self, id):
        self.id = id

    def change_server(self, server):
        self.server = server
    
    def update_chain(self):
        r = requests.get(url=self.server + "/chain")
        
        try:
            data = r.json()
        except ValueError:
            print("Error:  Non-json response")
            print("Response returned:")
            print(r)
            return
        
        if 'chain' in data:
            self.chain = data['chain']
        else:
            print("ERROR: Chain not in response")
            print("Response returned:")
            print(r)
            return

    def update_balance(self):
        if self.chain is not None:
            for block in self.chain:
                transactions = block['transactions']
                for transaction in transactions:
                    if transaction['recipient'] == self.id:
                        self.balance += transaction['amount']
    

    # GETTER METHODS
    def get_balance(self):
        return self.balance


if __name__ == '__main__':
    print("WELCOME TO WALLET")
    id = input("Please enter your id: ")

    wallet = Wallet(id)

    while True:
        print("Select an option:")
        print("(1) Update chain")
        print("(2) Update balance")
        print("(3) Get balance")
        print("(4) Change id")
        print("(5) Change server")
        print("(q) Quit")

        option = input(">>> ")
        if option == '1':
            wallet.update_chain()
        elif option == '2':
            wallet.update_balance()
        elif option == '3':
            balance = wallet.get_balance()
            print(f"Balance: {balance}")
        elif option == '4':
            id = input("Enter new id: ")
            wallet.change_id(id)
        elif option == '5':
            server = input("Enter new server address: ")
            wallet.change_server(server)
        elif option == 'q':
            break
        else:
            print(f'{option} is not a valid command.')
