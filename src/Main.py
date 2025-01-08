import tkinter as tk
import threading
import time
import multiprocessing
from src.MainDashBoard import MainDashBoard
from src.TelegramBot import TelegramBot


def check_bot_notifications(app :MainDashBoard, stop_event, shared_data, condition):
    while not stop_event.is_set():
        with condition:
            print("Notification thread waiting for bot request...")
            condition.wait()  # Wait for the bot to request a message

            if stop_event.is_set():
                break

            print("Thread activated to generate message.")
            lock = shared_data["lock"]
            lock.acquire()
            try:
                # Generate the message from the interface
                string = app.project_manager.get_upcoming_payments_string()
                shared_data["payment_message"] = string
                #print("Message generated:", string)
            finally:
                lock.release()

            # Notify the bot that the message is ready
            condition.notify_all()
        

def start_bot(bot: TelegramBot, stop_event):
        bot.start_bot()
   

def main():
    root = tk.Tk()
    manager = multiprocessing.Manager()
    shared_data = manager.dict()
    shared_data["payment_message"] = ""
    shared_data["lock"] = manager.Lock()

    # Condition for synchronization
    condition = manager.Condition()

    bot = TelegramBot(shared_data, condition)  # Pass dict to the bot
    stop_event = threading.Event()
    bot_process = multiprocessing.Process(target=start_bot, args=(bot, stop_event))
    bot_process.start()

    app = MainDashBoard(root)

    def on_closing():
        """
        Handle application closing.
        """
        print("Closing application...")
        stop_event.set()
        bot_process.terminate() 
        
        with condition:
            condition.notify_all()
            condition.notify_all()
            condition.notify_all()

        notification_thread.join()
        bot_process.join()
        root.destroy()
        print("Application closed.")


    # Create and start the notification thread
    notification_thread = threading.Thread(target=check_bot_notifications, args=(app, stop_event, shared_data, condition))
    notification_thread.start()

    root.protocol("WM_DELETE_WINDOW", on_closing)

    root.mainloop()

    print("Closing GUI")

if __name__ == "__main__":
    main()

    print("End of program")





