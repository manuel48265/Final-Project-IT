import tkinter as tk
import threading
import time
import multiprocessing
from src.MainDashBoard import MainDashBoard
from src.TelegramBot import TelegramBot


def check_bot_notifications(app :MainDashBoard, stop_event, shared_data, condition):
    while not stop_event.is_set():
        with condition:
            print("Hilo de notificaciones esperando solicitud del bot...")
            condition.wait()  # Esperar a que el bot solicite un mensaje

            if stop_event.is_set():
                break

            print("Hilo activado para generar mensaje.")
            lock = shared_data["lock"]
            lock.acquire()
            try:
                # Generar el mensaje desde la interfaz
                string = app.project_manager.get_upcoming_payments_string()
                shared_data["payment_message"] = string
                #print("Mensaje generado:", string)
            finally:
                lock.release()

            # Notificar al bot que el mensaje está listo
            condition.notify_all()
        

def start_bot(bot: TelegramBot, stop_event):
    try:
        bot.start_bot()
    except (KeyboardInterrupt, SystemExit):
        bot.stop_bot()
        stop_event.set()

def main():
    root = tk.Tk()
    manager = multiprocessing.Manager()
    shared_data = manager.dict()
    shared_data["payment_message"] = ""
    shared_data["lock"] = manager.Lock()

    # Condición para sincronización
    condition = manager.Condition()

    bot = TelegramBot(shared_data, condition)  # Pasar dict al bot
    stop_event = threading.Event()
    bot_process = multiprocessing.Process(target=start_bot, args=(bot, stop_event))
    bot_process.start()

    app = MainDashBoard(root)

    def on_closing():
        """
        Manejar el cierre de la aplicación.
        """
        print("Cerrando aplicación...")
        stop_event.set()
        bot_process.terminate()
        lock = shared_data["lock"]
        lock.acquire()  
        with condition:
            condition.notify_all()
            

        notification_thread.join()
        bot_process.join()
        root.destroy()
        print("Aplicación cerrada.")


    # Crear y empezar la hebra para las notificaciones
    notification_thread = threading.Thread(target=check_bot_notifications, args=(app, stop_event, shared_data, condition))
    notification_thread.start()

    root.protocol("WM_DELETE_WINDOW", on_closing)

    root.mainloop()

    print("Closing GUI")

if __name__ == "__main__":
    main()

    print("Fin del programa")


