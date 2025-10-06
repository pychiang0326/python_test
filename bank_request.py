import threading
import queue
import time


class CustomerRequest:
    def __init__(self, account_number, transaction_type, amount):
        self.account_number = account_number
        self.transaction_type = transaction_type
        self.amount = amount


class TellerThread(threading.Thread):
    def __init__(self, bankService_queue):
        threading.Thread.__init__(self)
        self.queue = bankService_queue

    def run(self):
        while True:
            customer_request = self.queue.get()
            print(f"Teller processing request for account {customer_request.account_number}")
            # Simulate processing time
            time.sleep(2)
            print(f"Teller finished processing request for account {customer_request.account_number}")
            self.queue.task_done()


class BankService:
    def __init__(self, num_tellers):
        self.queue = queue.Queue()
        self.tellers = []
        for _ in range(num_tellers):
            teller = TellerThread(self.queue)
            teller.daemon = True  # Daemon threads exit when the main program exits
            teller.start()
            self.tellers.append(teller)

    def add_customer_request(self, customer_request):
        self.queue.put(customer_request)

    def start(self):
        # Wait for all tasks to be completed
        self.queue.join()


# Example usage:
if __name__ == "__main__":
    bank_service = BankService(3)  # Create a bank with 3 tellers

    # Generate some customer requests
    requests = [
        CustomerRequest(123, "deposit", 1000),
        CustomerRequest(456, "withdraw", 500),
        # ... more requests
    ]

    for request in requests:
        bank_service.add_customer_request(request)

    bank_service.start()
