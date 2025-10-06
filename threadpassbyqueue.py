import threading
import time
from datetime import datetime
import queue

def monitor_date(signal_queue, stop_event):
    """執行緒一：監控是否換天，若換天則放訊號到queue"""
    current_date = datetime.now().date()
    while not stop_event.is_set():
        now_date = datetime.now().date()
        if now_date != current_date:
            print(f"Date changed from {current_date} to {now_date}, sending signal to writer thread.")
            current_date = now_date
            signal_queue.put("date_changed")
        time.sleep(1)

def writer(signal_queue, stop_event):
    """執行緒二：開檔並每2秒寫入時間，收到換天訊號時換檔"""
    current_date = datetime.now().date()
    filename = current_date.strftime("%Y-%m-%d") + ".txt"
    file = open(filename, "a", encoding="utf-8")
    print(f"Writer thread opened file: {filename}")

    try:
        while not stop_event.is_set():
            # 寫入目前時間
            now = datetime.now()
            file.write(now.strftime("%Y-%m-%d %H:%M:%S") + "\n")
            file.flush()
            print(f"Wrote time {now.strftime('%Y-%m-%d %H:%M:%S')} to {filename}")

            # 等待2秒期間檢查換天訊號
            for _ in range(20):  # 每0.1秒檢查一次，共2秒
                if stop_event.is_set():
                    break
                try:
                    msg = signal_queue.get_nowait()
                    if msg == "date_changed":
                        # 換檔
                        file.close()
                        print(f"Writer thread closed file: {filename}")
                        current_date = datetime.now().date()
                        filename = current_date.strftime("%Y-%m-%d") + ".txt"
                        file = open(filename, "a", encoding="utf-8")
                        print(f"Writer thread opened new file: {filename}")
                except queue.Empty:
                    pass
                time.sleep(0.1)

    finally:
        file.close()
        print(f"Writer thread closed file: {filename}")

def main():
    signal_queue = queue.Queue()
    stop_event = threading.Event()

    t_monitor = threading.Thread(target=monitor_date, args=(signal_queue, stop_event))
    t_writer = threading.Thread(target=writer, args=(signal_queue, stop_event))

    t_monitor.start()
    t_writer.start()

    try:
        while True:
            time.sleep(0.1)
    except KeyboardInterrupt:
        print("\nCtrl+C pressed, stopping threads...")
        stop_event.set()

    t_monitor.join()
    t_writer.join()
    print("Program exited gracefully.")

if __name__ == "__main__":
    main()
