import threading
import time
from datetime import datetime

def thread1(event, stop_event):
    while not stop_event.is_set():
        for _ in range(60):
            if stop_event.is_set():
                break
            print(f"[Thread1] 現在時間: {datetime.now().strftime('%H:%M:%S')}")
            time.sleep(1)
        if stop_event.is_set():
            break
        print("[Thread1] 1分鐘到了，通知Thread2")
        event.set()  # 通知Thread2
        event.clear()  # 重置事件，等待下一輪

def thread2(event, stop_event):
    while not stop_event.is_set():
        event.wait()  # 等待Thread1通知
        if stop_event.is_set():
            break
        print(f"[Thread2] 收到通知，現在時間: {datetime.now().strftime('%H:%M:%S')}")

if __name__ == "__main__":
    event = threading.Event()
    stop_event = threading.Event()

    t1 = threading.Thread(target=thread1, args=(event, stop_event))
    t2 = threading.Thread(target=thread2, args=(event, stop_event))

    t1.start()
    t2.start()

    try:
        while True:
            time.sleep(0.1)
    except KeyboardInterrupt:
        print("\n收到 Ctrl-C，準備結束程式...")
        stop_event.set()
        event.set()  # 確保thread2不會卡在等待
        t1.join()
        t2.join()
        print("程式已安全結束。")
