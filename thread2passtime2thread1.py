import threading
import time
import queue
from datetime import datetime

def thread1(q, stop_event):
    while not stop_event.is_set():
        try:
            # 嘗試非阻塞取得執行緒2傳來的時間
            new_time = q.get_nowait()
            print(f"Thread1 received time from Thread2: {new_time}")
        except queue.Empty:
            # 沒有新時間，印出自己的時間
            print(f"Thread1 time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        time.sleep(1)

def thread2(q, stop_event):
    while not stop_event.is_set():
        time.sleep(5)
        current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        q.put(current_time)
        print("Thread2 sent current time to Thread1")

def main():
    q = queue.Queue()
    stop_event = threading.Event()

    t1 = threading.Thread(target=thread1, args=(q, stop_event))
    t2 = threading.Thread(target=thread2, args=(q, stop_event))

    t1.start()
    t2.start()

    try:
        while True:
            time.sleep(0.1)
    except KeyboardInterrupt:
        print("\nCtrl+C pressed, stopping threads...")
        stop_event.set()

    t1.join()
    t2.join()
    print("Program exited gracefully.")

if __name__ == "__main__":
    main()
