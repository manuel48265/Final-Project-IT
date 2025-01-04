from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, Updater
from telegram.ext import CallbackContext
import asyncio
from datetime import datetime, date, timedelta
from threading import Thread
import signal



TOKEN = '7835632666:AAF6n515HqQN8soWdEQTcXhlPVSHSy5DSGU'

class TelegramBot:
    def __init__(self, shared_data, condition):
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
        self.user_notifications[update.effective_user.username] = (False, "días", None)
        await update.message.reply_text('Hola! Usa /help para recibir mas información.')

    async def notify(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        username = update.effective_user.username
        if username in self.user_notifications:
            await update.message.reply_text('Introduce /horas /dias o /semanas para configurar el intervalo de notificaciones.')
            await update.message.reply_text('Por defecto se configura cada día.')

            self.user_notifications[username] = (True, "dias", None)
        else:
            await update.message.reply_text('Usuario no encontrado.')

    async def notify_hours(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        username = update.effective_user.username
        if username in self.user_notifications:
            self.user_notifications[username] = (True, "horas", None)
            await update.message.reply_text('Notificaciones configuradas para cada hora.')
        else:
            await update.message.reply_text('Usuario no encontrado.')

    async def notify_days(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        username = update.effective_user.username
        if username in self.user_notifications:
            self.user_notifications[username] = (True, "dias", None)
            await update.message.reply_text('Notificaciones configuradas para cada día.')
        else:
            await update.message.reply_text('Usuario no encontrado.')

    async def notify_weeks(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        username = update.effective_user.username
        if username in self.user_notifications:
            self.user_notifications[username] = (True, "semanas", None)
            await update.message.reply_text('Notificaciones configuradas para cada semana.')
        else:
            await update.message.reply_text('Usuario no encontrado.')

    async def not_notified(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        username = update.effective_user.username
        
        if username in self.user_notifications:
            self.user_notifications[username] = (False, "días", None)
            await update.message.reply_text('Has dejado de recibir notificaciones.')
        else:
            await update.message.reply_text('Usuario no encontrado.')

    async def help(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        help_text = (
            "/start - Iniciar el bot\n"
            "/notify - Configurar notificaciones\n"
                "\t /horas - Notificar cada hora\n"
                "\t /dias - Notificar cada día\n"
                "\t /semanas - Notificar cada semana\n"
            "/not_notified - Detener notificaciones\n"
            "/help - Mostrar este mensaje de ayuda"
        )
        await update.message.reply_text(help_text)

    async def send_custom_message(self, username: str, message: str, app) -> None:
        if username in self.user_chat_ids:
            chat_id = self.user_chat_ids[username]
            await app.bot.send_message(chat_id=chat_id, text=message)
        else:
            print(f"Usuario {username} no encontrado.")

    async def send_message_to_all(self, context: CallbackContext) -> None:
        current_time = datetime.now()
        

        if self.user_notifications is None:
            return
        else:
            payment_msg = await self.get_payment_message()
            for username, (notify, interval, last_notified) in self.user_notifications.items():
                if notify:
                    if interval == "horas" and (last_notified is None or (current_time - last_notified) >= timedelta(seconds=10)):
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
            print("Bot esperando mensaje...")

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
                await context.bot.send_message(chat_id=self.user_chat_ids[username], text="Ha habido un problema al obtener los pagos pendientes.")
            elif payment_msg == "":
                await context.bot.send_message(chat_id=self.user_chat_ids[username], text="NO HAY PAGOS PENDIENTES")
            else:
                await context.bot.send_message(chat_id=self.user_chat_ids[username], text=payment_msg)
        else:
            print(f"Usuario {username} no encontrado.")

    def start_bot(self):
        self.app = ApplicationBuilder().token(TOKEN).build()
        self.app.add_handler(CommandHandler("start", self.start))
        self.app.add_handler(CommandHandler("notify", self.notify))
        self.app.add_handler(CommandHandler("not_notified", self.not_notified))
        self.app.add_handler(CommandHandler("help", self.help))
        self.app.add_handler(CommandHandler("horas", self.notify_hours))
        self.app.add_handler(CommandHandler("dias", self.notify_days))
        self.app.add_handler(CommandHandler("semanas", self.notify_weeks))

        # Asegúrate de que JobQueue esté configurado
        job_queue = self.app.job_queue
        if job_queue is not None:
            job_queue.run_repeating(self.send_message_to_all, interval=10, first=0)
        else:
            print("JobQueue no está configurado correctamente.")

        # Ejecuta el bot de Telegram
        self.app.run_polling(stop_signals=[signal.SIGINT, signal.SIGTERM, signal.SIGUSR1])

if __name__ == "__main__":
    bot_app = TelegramBot()
    try:
        bot_app.start_bot()
    except (KeyboardInterrupt, SystemExit):
        bot_app.stop_bot()







