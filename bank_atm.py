import threading
import queue
import time


class Account:
    def __init__(self, balance):
        self.balance = balance

    def get_balance(self):
        return self.balance

    def deposit(self, amount):
        if amount > 0:
            self.balance += amount
            print(f"Deposited: ${amount:.2f}")
        else:
            print("Invalid deposit amount.")

    def withdraw(self, amount):
        if 0 < amount <= self.balance:
            self.balance -= amount
            print(f"Withdrawn: ${amount:.2f}")
            return True
        else:
            print("Insufficient funds or invalid amount.")
            return False


class User:
    def __init__(self, username, pin, account):
        self.username = username
        self.pin = pin
        self.account = account

    def validate_pin(self, input_pin):
        return self.pin == input_pin


class RequestQueue:
    def __init__(self):
        self.queue = queue.Queue()

    def add_request(self, request):
        self.queue.put(request)

    def get_request(self):
        return self.queue.get()


class BankService(threading.Thread):
    def __init__(self, request_queue):
        threading.Thread.__init__(self)
        self.request_queue = request_queue
        self.daemon = True  # Daemonize thread

    def run(self):
        while True:
            request = self.request_queue.get_request()
            if request is None:  # Exit signal
                break

            user, action, amount = request
            print(f"Processing request: {action} ${amount:.2f} for user {user.username}")
            if action == "deposit":
                user.account.deposit(amount)
            elif action == "withdraw":
                user.account.withdraw(amount)
            time.sleep(1)  # Simulate processing time1234


class ATM:
    def __init__(self, user, request_queue):
        self.user = user
        self.request_queue = request_queue

    def start(self):
        print("Welcome to the ATM")

        input_pin = input("Enter your PIN: ")
        if not self.user.validate_pin(input_pin):
            print("Invalid PIN. Transaction cancelled.")
            return

        while True:
            print("\n1. Check Balance\n2. Deposit\n3. Withdraw\n4. Exit")
            option = input("Select an option: ")

            if option == '1':
                print(f"Current Balance: ${self.user.account.get_balance():.2f}")
            elif option == '2':
                deposit_amount = float(input("Enter deposit amount: "))
                self.request_queue.add_request((self.user, "deposit", deposit_amount))
                print(f"Request added: Deposit ${deposit_amount:.2f}")
            elif option == '3':
                withdrawal_amount = float(input("Enter withdrawal amount: "))
                self.request_queue.add_request((self.user, "withdraw", withdrawal_amount))
            elif option == '4':
                print("Thank you for using the ATM.")
                break
            else:
                print("Invalid option. Please try again.")


if __name__ == "__main__":
    initial_balance = 1000.00
    user_account = Account(initial_balance)  # Create an account with initial balance
    user = User(username="john_doe", pin="1234", account=user_account)  # Create a user with a PIN and account

    request_queue = RequestQueue()  # Initialize the request queue
    bank_service = BankService(request_queue)  # Create the bank service thread
    bank_service.start()  # Start the bank service thread

    atm = ATM(user, request_queue)  # Initialize the ATM with the user and request queue
    atm.start()  # Start the ATM interface

    # Signal to stop the bank service thread when done (optional)
    request_queue.add_request(None)  # Send exit signal to bank service thread