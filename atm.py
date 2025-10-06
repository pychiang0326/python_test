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


class ATM:
    def __init__(self, user):
        self.user = user

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
                self.user.account.deposit(deposit_amount)
            elif option == '3':
                withdrawal_amount = float(input("Enter withdrawal amount: "))
                self.user.account.withdraw(withdrawal_amount)
            elif option == '4':
                print("Thank you for using the ATM.")
                break
            else:
                print("Invalid option. Please try again.")


if __name__ == "__main__":
    initial_balance = 1000.00
    user_account = Account(initial_balance)  # Create an account with initial balance
    user = User(username="john_doe", pin="1234", account=user_account)  # Create a user with a PIN and account
    atm = ATM(user)  # Initialize the ATM with the user
    atm.start()  # Start the ATM interface