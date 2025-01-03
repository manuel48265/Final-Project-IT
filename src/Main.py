import tkinter as tk
import threading
import time
import multiprocessing
from src.MainDashBoard import MainDashBoard
from src.TelegramBot import TelegramBot
from src.ProjectManager import ProjectManager


def check_bot_notifications(app :MainDashBoard, stop_event, shared_data):
    while not stop_event.is_set():
        print("Checking notifications")
        lock = shared_data["lock"]
        with lock:
            string = app.project_manager.get_upcoming_payments_string()
            shared_data["payment_message"] = string
        time.sleep(1)

def start_bot(bot: TelegramBot):
    
    bot.start_bot() 

def main():
    root = tk.Tk()
    manager = multiprocessing.Manager()
    shared_data = manager.dict()
    shared_data["payment_message"] = ""
    shared_data["lock"] = manager.Lock()

    bot = TelegramBot(shared_data)  # Pasar dict al bot
    bot_process = multiprocessing.Process(target=start_bot, args=(bot,))
    bot_process.start()

    app = MainDashBoard(root)
    stop_event = threading.Event()

    def on_closing():
        print("Cerrando hilo de notificaciones")
        stop_event.set()
        notification_thread.join()
        print("Ventana cerrada, deteniendo programa.")
        app.on_closing()
        bot_process.terminate()
        bot_process.join()


    # Crear y empezar la hebra para las notificaciones
    notification_thread = threading.Thread(target=check_bot_notifications, args=(app, stop_event, shared_data))
    notification_thread.start()

    root.protocol("WM_DELETE_WINDOW", on_closing)

    root.mainloop()

    print("Closing GUI")

if __name__ == "__main__":
    main()

    print("Fin del programa")


