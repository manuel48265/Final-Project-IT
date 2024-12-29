from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from telegram.ext import CallbackContext
import asyncio

TOKEN = '7835632666:AAF6n515HqQN8soWdEQTcXhlPVSHSy5DSGU'

# Diccionario para almacenar los IDs de chat de los usuarios
user_chat_ids = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat_id = update.effective_chat.id
    user_chat_ids[update.effective_user.username] = chat_id
    await update.message.reply_text('Hola! Usa /notify para recibir una notificación.')

async def notify(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text('Esta es tu notificación!')

async def send_custom_message(username: str, message: str, app) -> None:
    if username in user_chat_ids:
        chat_id = user_chat_ids[username]
        await app.bot.send_message(chat_id=chat_id, text=message)
    else:
        print(f"Usuario {username} no encontrado.")

async def send_message_to_all(context: CallbackContext) -> None:
    for username, chat_id in user_chat_ids.items():
        await context.bot.send_message(chat_id=chat_id, text="Mensaje automático cada 20 segundos")

def main():
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("notify", notify))

    # Asegúrate de que JobQueue esté configurado
    job_queue = app.job_queue
    if job_queue is not None:
        job_queue.run_repeating(send_message_to_all, interval=20, first=0)
    else:
        print("JobQueue no está configurado correctamente.")

    app.run_polling()

if __name__ == '__main__':
    main()

