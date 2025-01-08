import tkinter as tk
from google import genai
from google.genai import types
import re
import markdown
from tkhtmlview import HTMLLabel  # Import HTMLLabel to display Markdown
from src.Constants import GOOGLE_API_KEY, MODEL_ID
from src.ProjectManager import ProjectManager
from tkinter import ttk

# Google API client configuration (without including the real API key for safety)
client = genai.Client(api_key=GOOGLE_API_KEY)

class ChatBotFrame(tk.Frame):
    def __init__(self, parent, project_manager: ProjectManager):
        super().__init__(parent)
        self.configure(bg="white")  # Change background to white
        self.project_manager = project_manager
        self.chat_histories = {"General": "<div style='font-family: Arial; color: green;'>Welcome to the General Chat</div>"}
        self.chat_histories["Normal Conversation"] = "<div style='font-family: Arial; color: green;'>Welcome to the Normal Conversation Chat</div>"
        for project in self.project_manager.proyectos:
            self.chat_histories[project.get_name()] = f"<div style='font-family: Arial; color: green;'>Welcome to the chat of the project {project.get_name()}</div>"
        self.current_project = "Normal Conversation"
        self.create_widgets()

    def create_widgets(self):
        # Main container
        self.main_frame = tk.Frame(self, bg="white")  # Change background to white
        self.main_frame.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

        # ComboBox to select a project
        data = ["Normal Conversation"] + ["General"] + [p.get_name() for p in self.project_manager.proyectos]
        self.combo_projects = ttk.Combobox(self.main_frame, values=data, state="readonly")
        self.combo_projects.current(0)
        self.combo_projects.pack(pady=5)
        self.combo_projects.bind("<<ComboboxSelected>>", self.project_selected)

        # HTMLLabel to show formatted messages
        self.html_label = HTMLLabel(self.main_frame, html=self.chat_histories[self.current_project], background="white")  # Change background to white
        self.html_label.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Frame for the user input and buttons
        self.user_input_frame = tk.Frame(self, bg="white")  # Change background to white
        self.user_input_frame.pack(padx=10, pady=10, fill=tk.X)

        self.user_input = tk.Entry(self.user_input_frame, bg="green", fg="white", font=("Arial", 12), insertbackground="white")  # Change background to green
        self.user_input.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        self.user_input.bind("<Return>", self.send_message)

        self.send_button = tk.Button(self.user_input_frame, text="Send", bg="green", fg="white", font=("Arial", 12), command=lambda: self.send_message(None))  # Change background to green
        self.send_button.pack(side=tk.RIGHT)

        self.clear_button = tk.Button(self.user_input_frame, text="Clear", bg="red", fg="white", font=("Arial", 12), command=self.clear_conversation)  # Button to clear the conversation
        self.clear_button.pack(side=tk.RIGHT, padx=(0, 5))

    def project_selected(self, event):
        self.current_project = self.combo_projects.get()
        self.html_label.set_html(self.chat_histories[self.current_project])

    def send_message(self, event):
        user_message = self.user_input.get().strip()
        if not user_message:
            return
        else:
            self.display_message(f"You: \n{user_message}", align="right")  # Change "right" to "e"
            self.user_input.delete(0, tk.END)

            if self.current_project == "Normal Conversation":
                prompt = f"{user_message}\n"
                
            elif self.current_project == "General":
                prompt = f"{user_message}\n"
                prompt += f"use the following data if and only if it is relevant to the answer\n"
                prompt += f"Company data:\n {self.project_manager.get_all_data()}\n"

            else:
                prompt = f"{user_message}\n"
                prompt += f"use the following data if and only if it is relevant to the answer\n"
                prompt += f"Project data:\n {self.project_manager.get_proyectos(self.current_project).get_accurate_data()}\n"

            response = self.generate_response(prompt)
            response = self.clean_content(response)
            self.display_message(f"<div style='font-family: Arial; color: green;'>ChatBot:</div>\n{response}", align="left")  # Change "left" to "w"

    def display_message(self, message, align="left"):
        # Format the message as HTML
        self.chat_histories[self.current_project] += f"<div style='text-align: {align};'>{message}</div>"
        self.html_label.set_html(self.chat_histories[self.current_project])
        self.user_input.delete(0, tk.END)

    def clean_content(self, content):
        # Erase the string '''html
        content = re.sub(r"```html", "", content)
        # Erase the last specific characters (for example, the last 3 characters)
        content = content[:-4] 
        return content

    def generate_response(self, prompt):
        prompt += "\n Create this response in html. Maintain line breaks where necessary."
        try:
            response = client.models.generate_content(
                model=MODEL_ID,
                contents=prompt
            )
            return response.text.strip() if response.text.strip() else "Sorry, I can't generate an answer at this moment."
        except Exception as e:
            return f"Error generating response: {e}"

    def clear_conversation(self):
        self.chat_histories[self.current_project] = f"<div style='font-family: Arial; color: green;'>Welcome to the chat {self.current_project}</div>"
        self.html_label.set_html(self.chat_histories[self.current_project])

if __name__ == "__main__":
    root = tk.Tk()
    root.title("ChatBot")
    root.geometry("500x700")
    root.configure(bg="white")  # Change background to white

    chatbot_frame = ChatBotFrame(root, project_manager=ProjectManager())
    chatbot_frame.pack(fill=tk.BOTH, expand=True)

    root.mainloop()
