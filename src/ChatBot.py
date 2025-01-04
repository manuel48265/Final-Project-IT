import tkinter as tk
from google import genai
from google.genai import types
import re
import markdown
from tkhtmlview import HTMLLabel  # Importar HTMLLabel para mostrar Markdown

GOOGLE_API_KEY = "AIzaSyAX25KeA27dvXLmJcJegsk7sQAFVO7DBE8"
# Configuración del cliente de Google API (sin incluir la API key real por seguridad)
client = genai.Client(api_key=GOOGLE_API_KEY)
MODEL_ID = "models/gemini-2.0-flash-exp"

class ChatBotFrame(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.configure(bg="#1E1E2F")
        self.create_widgets()

    def create_widgets(self):
        # Marco principal del log de chat
        self.chat_log_frame = tk.Frame(self, bg="#2F2F3F")
        self.chat_log_frame.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

        # Text widget para mostrar mensajes formateados
        self.chat_text = tk.Text(self.chat_log_frame, wrap=tk.WORD, bg="#3F3F4F", fg="white", font=("Arial", 12), height=15, state=tk.DISABLED)
        self.chat_text.pack(fill=tk.BOTH, expand=True)  # Cambié a fill=tk.BOTH y expand=True

        # Scrollbar
        self.scrollbar = tk.Scrollbar(self.chat_log_frame, command=self.chat_text.yview)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.chat_text.config(yscrollcommand=self.scrollbar.set)

        # Input de usuario
        self.user_input_frame = tk.Frame(self, bg="#1E1E2F")
        self.user_input_frame.pack(padx=10, pady=10, fill=tk.X)
        
        self.user_input = tk.Entry(self.user_input_frame, bg="#3F3F4F", fg="white", font=("Arial", 12), insertbackground="white")
        self.user_input.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        self.user_input.bind("<Return>", self.send_message)

        self.send_button = tk.Button(self.user_input_frame, text="Enviar", bg="#5F5FFF", fg="white", font=("Arial", 12), command=lambda: self.send_message(None))
        self.send_button.pack(side=tk.RIGHT)

    def send_message(self, event):
        user_message = self.user_input.get().strip()
        if not user_message:
            return

        if user_message.lower() in ["salir", "exit"]:
            self.quit()
        else:
            self.display_message(f"Tú: \n{user_message}", align="e")  # Cambiar "right" a "e"
            self.user_input.delete(0, tk.END)

            prompt = f"Usuario: {user_message}\nChatbot:"
            respuesta = self.generar_respuesta(prompt)
            self.display_message(f"Chatbot: \n{respuesta}", align="w")  # Cambiar "left" a "w"

    def display_message(self, message, align="w"):
        # Convertir el mensaje a formato Markdown
        #html_message = markdown.markdown(message)

        # Formatear el mensaje para Text widget
        #formatted_message = self.convert_html_to_text(html_message)
        formatted_message = message

        # Mostrar el mensaje en el Text widget
        self.chat_text.config(state=tk.NORMAL)
        self.chat_text.insert(tk.END, formatted_message + "\n")
        self.chat_text.config(state=tk.DISABLED)

        # Asegura que el scroll siempre se desplace hacia el final
        self.chat_text.yview(tk.END)

    def convert_html_to_text(self, html_message):
        # Eliminar etiquetas HTML simples y convertir a formato legible (solo negritas y cursivas por ahora)
        html_message = re.sub(r"<b>(.*?)</b>", r"\033[1m\1\033[0m", html_message)  # Negrita
        html_message = re.sub(r"<i>(.*?)</i>", r"\033[3m\1\033[0m", html_message)  # Cursiva
        # Limpiar cualquier otro HTML innecesario
        html_message = re.sub(r"<.*?>", "", html_message)
        return html_message

    def generar_respuesta(self, prompt):
        prompt += "\n Create this response in plain text without using bold, italics, or any other font style. Maintain line breaks where necessary."
        try:
            response = client.models.generate_content(
                model=MODEL_ID,
                contents=prompt
            )
            return response.text.strip() if response.text.strip() else "Lo siento, no puedo generar una respuesta en este momento."
        except Exception as e:
            return f"Error al generar respuesta: {e}"

if __name__ == "__main__":
    root = tk.Tk()
    root.title("ChatBot")
    root.geometry("500x700")
    root.configure(bg="#1E1E2F")

    chatbot_frame = ChatBotFrame(root)
    chatbot_frame.pack(fill=tk.BOTH, expand=True)

    root.mainloop()

