import threading
import time


class Account:
    def __init__(self, balance=0.0):
        self.balance = balance

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

    def get_balance(self):
        return self.balance


class User:
    def __init__(self, username, pin, account):
        self.username = username
        self.pin = pin
        self.account = account

    def validate_pin(self, input_pin):
        return self.pin == input_pin


class Request:
    def __init__(self, user, action, amount):
        self.user = user
        self.action = action
        self.amount = amount


class RequestQueue:
    def __init__(self):
        self.queue = []
        self.lock = threading.Lock()

    def add_request(self, request):
        with self.lock:
            self.queue.append(request)

    def get_request(self):
        with self.lock:
            if self.queue:
                return self.queue.pop(0)
            return None


class BankService(threading.Thread):
    def __init__(self, request_queue):
        super().__init__()
        self.request_queue = request_queue
        self.running = True

    def run(self):
        while self.running:
            request = self.request_queue.get_request()
            if request is not None:
                user = request.user
                action = request.action
                amount = request.amount

                print(f"Processing request: {action} ${amount:.2f} for user {user.username}")
                if action == "deposit":
                    user.account.deposit(amount)
                elif action == "withdraw":
                    success = user.account.withdraw(amount)
                    if success:
                        print("Withdrawal successful.")
                    else:
                        print("Withdrawal failed.")
            else:
                time.sleep(0.5)  # Avoid busy waiting


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
                request = Request(self.user, "deposit", deposit_amount)
                self.request_queue.add_request(request)
                print("Your deposit request has been submitted and is being processed.")

                # Wait for processing to complete before allowing further actions
                while True:
                    time.sleep(0.5)  # Polling delay
                    if not self.request_queue.get_request():  # Check if processing is done
                        break

                # After processing is done, check updated balance
                print(f"Updated Balance: ${self.user.account.get_balance():.2f}")

            elif option == '3':
                withdrawal_amount = float(input("Enter withdrawal amount: "))
                request = Request(self.user, "withdraw", withdrawal_amount)
                self.request_queue.add_request(request)
                print("Your withdrawal request has been submitted and is being processed.")

                # Wait for processing to complete before allowing further actions
                while True:
                    time.sleep(0.5)  # Polling delay
                    if not self.request_queue.get_request():  # Check if processing is done
                        break

                # After processing is done, check updated balance
                print(f"Updated Balance: ${self.user.account.get_balance():.2f}")

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

    # Signal to stop processing requests when done (optional)
    bank_service.running = False  # Stop the bank service thread when done
    bank_service.join()  # Wait for bank service thread to finish