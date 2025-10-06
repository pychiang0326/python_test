import threading
import time
import queue

# Define a Customer class to simulate bank customers
class Customer:
    def __init__(self, customer_id):
        self.customer_id = customer_id

# Define a Bank class to manage the queue and service customers
class Bank:
    def __init__(self, num_tellers):
        self.queue = queue.Queue()
        self.tellers = [threading.Thread(target=self.serve_customer, name=f'Teller-{i+1}') for i in range(num_tellers)]
        for teller in self.tellers:
            teller.start()

    def add_customer(self, customer):
        self.queue.put(customer)
        print(f"Customer {customer.customer_id} has arrived.")

    def serve_customer(self):
        while True:
            try:
                customer = self.queue.get(timeout=5)  # Wait for a customer for up to 5 seconds
                print(f"{threading.current_thread().name} is serving Customer {customer.customer_id}.")
                time.sleep(2)  # Simulate time taken to serve the customer
                print(f"{threading.current_thread().name} has finished serving Customer {customer.customer_id}.")
                self.queue.task_done()
            except queue.Empty:
                print(f"{threading.current_thread().name} found no customers to serve and is exiting.")
                break

# Simulating the bank service
def main():
    bank = Bank(num_tellers=3)

    # Create and add customers to the bank
    for i in range(10):
        customer = Customer(customer_id=i+1)
        bank.add_customer(customer)
        time.sleep(1)  # Simulate time between customer arrivals

    bank.queue.join()  # Wait until all customers have been served

    # Stop the tellers after serving all customers
    for teller in bank.tellers:
        teller.join()

if __name__ == "__main__":
    main()