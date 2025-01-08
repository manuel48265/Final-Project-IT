from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, Updater
from telegram.ext import CallbackContext
import asyncio
from datetime import datetime, date, timedelta
from threading import Thread
import signal
from src.Constants import TOKEN 

class TelegramBot:
    def __init__(self, shared_data = None, condition = None):
        self.shared_data = shared_data
        self.user_chat_ids = {}
        self.user_notifications = {}  # Mapa con clave usuario y valor (bool, str, datetime)
        self.notify_flag = asyncio.Event()
        self.last_message_update = None
        self.payment_message = None
        self.app = None  # Añadir atributo de clase para la app
        self.condition = condition

    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        chat_id = update.effective_chat.id
        self.user_chat_ids[update.effective_user.username] = chat_id
        self.user_notifications[update.effective_user.username] = (False, "dias", None)
        await update.message.reply_text('Hello! Use /help to get more information.')

    async def notify(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        username = update.effective_user.username
        if username in self.user_notifications:
            await update.message.reply_text('You are currently receiving notifications every day.')
            await update.message.reply_text('Enter /hours /days or /weeks to set the notification interval.')
            
            self.user_notifications[username] = (True, "dias", None)
        else:
            await update.message.reply_text('User not found.')

    async def notify_hours(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        username = update.effective_user.username
        if username in self.user_notifications:
            self.user_notifications[username] = (True, "horas", None)
            await update.message.reply_text('Notifications set for every hour.')
        else:
            await update.message.reply_text('User not found.')

    async def notify_days(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        username = update.effective_user.username
        if username in self.user_notifications:
            self.user_notifications[username] = (True, "dias", None)
            await update.message.reply_text('Notifications set for every day.')
        else:
            await update.message.reply_text('User not found.')

    async def notify_weeks(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        username = update.effective_user.username
        if username in self.user_notifications:
            self.user_notifications[username] = (True, "semanas", None)
            await update.message.reply_text('Notifications set for every week.')
        else:
            await update.message.reply_text('User not found.')

    async def not_notified(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        username = update.effective_user.username
        
        if username in self.user_notifications:
            self.user_notifications[username] = (False, "dias", None)
            await update.message.reply_text('You have stopped receiving notifications.')
        else:
            await update.message.reply_text('User not found.')

    async def help(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        help_text = (
            "/start - Start the bot\n"
            "/notify - Set notifications\n"
                "\t /hours - Notify every hour\n"
                "\t /days - Notify every day\n"
                "\t /weeks - Notify every week\n"
            "/not_notified - Stop notifications\n"
            "/help - Show this help message"
        )
        await update.message.reply_text(help_text)

    async def send_custom_message(self, username: str, message: str, app) -> None:
        if username in self.user_chat_ids:
            chat_id = self.user_chat_ids[username]
            await app.bot.send_message(chat_id=chat_id, text=message)
        else:
            print(f"User {username} not found.")

    async def send_message_to_all(self, context: CallbackContext) -> None:
        current_time = datetime.now()
        

        if self.user_notifications is None:
            return
        else:
            payment_msg = await self.get_payment_message()
            for username, (notify, interval, last_notified) in self.user_notifications.items():
                if notify:
                    print(f"User {username} is being notified.")
                    if interval == "horas" and (last_notified is None or (current_time - last_notified) >= timedelta(seconds=20)):
                        await self.send_payment_message_to_user(username, context, payment_msg)
                        self.user_notifications[username] = (True, "horas", current_time)
                    elif interval == "dias" and (last_notified is None or (current_time - last_notified) >= timedelta(days=1)):
                        await self.send_payment_message_to_user(username, context, payment_msg)
                        self.user_notifications[username] = (True, "dias", current_time)
                    elif interval == "semanas" and (last_notified is None or (current_time - last_notified) >= timedelta(weeks=1)):
                        await self.send_payment_message_to_user(username, context)
                        self.user_notifications[username] = (True, "semanas", current_time, payment_msg)

    async def get_payment_message(self) -> None:
         with self.condition:
            # Notificar a la interfaz que se requiere un mensaje
            self.condition.notify_all()
            print("Bot waiting for message...")

            # Esperar hasta que el mensaje esté disponible
            self.condition.wait_for(lambda: self.shared_data["payment_message"] != "")

            # Obtener el mensaje
            lock = self.shared_data["lock"]
            lock.acquire()
            try:
                mensaje = self.shared_data["payment_message"]
                self.shared_data["payment_message"] = ""  # Limpiar el mensaje después de procesarlo
            finally:
                lock.release()

            return mensaje

    def set_payment_message(self, message: str) -> None:
        print("Setting payment message")
        lock = self.shared_data["lock"]
        with lock:
            self.shared_data["payment_message"] = message
        self.last_message_update = datetime.now()
        print("Payment message set")

    async def send_payment_message_to_user(self, username: str, context: CallbackContext, payment_msg: str) -> None:
        if username in self.user_chat_ids:
            if not payment_msg:
                await context.bot.send_message(chat_id=self.user_chat_ids[username], text="There was a problem getting the pending payments.")
            elif payment_msg == "":
                await context.bot.send_message(chat_id=self.user_chat_ids[username], text="NO PENDING PAYMENTS")
            else:
                await context.bot.send_message(chat_id=self.user_chat_ids[username], text=payment_msg, parse_mode="Markdown")
        else:
            print(f"User {username} not found.")

    def start_bot(self):
        self.app = ApplicationBuilder().token(TOKEN).build()
        self.app.add_handler(CommandHandler("start", self.start))
        self.app.add_handler(CommandHandler("notify", self.notify))
        self.app.add_handler(CommandHandler("not_notified", self.not_notified))
        self.app.add_handler(CommandHandler("help", self.help))
        self.app.add_handler(CommandHandler("hours", self.notify_hours))
        self.app.add_handler(CommandHandler("days", self.notify_days))
        self.app.add_handler(CommandHandler("weeks", self.notify_weeks))

        # Asegúrate de que JobQueue esté configurado
        job_queue = self.app.job_queue
        if job_queue is not None:
            job_queue.run_repeating(self.send_message_to_all, interval=30, first=0)
        else:
            print("JobQueue is not configured correctly.")

        # Ejecuta el bot de Telegram
        self.app.run_polling(stop_signals=[signal.SIGINT, signal.SIGTERM, signal.SIGUSR1])

if __name__ == "__main__":
    bot_app = TelegramBot()
    bot_app.start_bot()







