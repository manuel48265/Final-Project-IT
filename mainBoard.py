import tkinter as tk
from tkinter import simpledialog, filedialog, ttk
from PIL import Image, ImageTk
import matplotlib.pyplot as plt
from io import BytesIO
import random
from forex_python.converter import CurrencyRates
import datetime

class ProjectManagementApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Project Management Tool")
        self.root.configure(bg="lightblue")

        self.currency_converter = CurrencyRates()
        self.base_currency = "EUR"

        # Main frames
        self.overview_frame = tk.Frame(self.root, bg="white", bd=2, relief=tk.GROOVE)
        self.overview_frame.pack(fill=tk.X, padx=10, pady=10)

        self.columns_frame = tk.Frame(self.root, bg="lightblue")
        self.columns_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Project Overview Section
        self.add_overview_section()

        # Columns
        self.columns = []
        for column_name in ["To Do", "In Progress", "Done"]:
            self.add_column(column_name)

        # Almacenar referencias de imágenes
        self.image_references = {}

    def add_overview_section(self):
        tk.Label(self.overview_frame, text="Project Overview", bg="steelblue", fg="white", font=("Arial", 14, "bold")).pack(fill=tk.X, pady=5)

        stats_frame = tk.Frame(self.overview_frame, bg="white")
        stats_frame.pack(fill=tk.X, padx=10, pady=10)

        self.total_income_label = tk.Label(stats_frame, text="Total Income: 0 EUR", font=("Arial", 12))
        self.total_income_label.grid(row=0, column=0, sticky="w")

        self.total_expenses_label = tk.Label(stats_frame, text="Total Expenses: 0 EUR", font=("Arial", 12))
        self.total_expenses_label.grid(row=1, column=0, sticky="w")

        self.profit_loss_label = tk.Label(stats_frame, text="Profit/Loss: 0 EUR", font=("Arial", 12))
        self.profit_loss_label.grid(row=2, column=0, sticky="w")

        self.currency_selector = ttk.Combobox(stats_frame, values=["EUR", "PLN", "USD", "GBP"], state="readonly")
        self.currency_selector.set(self.base_currency)
        self.currency_selector.grid(row=3, column=0, sticky="w", pady=5)
        self.currency_selector.bind("<<ComboboxSelected>>", self.update_currency)

        chart_button = tk.Button(stats_frame, text="Show Charts", command=self.show_charts)
        chart_button.grid(row=4, column=0, sticky="w", pady=10)

        self.upcoming_payments = tk.Text(self.overview_frame, height=5, wrap=tk.WORD, bg="lightyellow")
        self.upcoming_payments.pack(fill=tk.X, padx=10, pady=10)
        self.upcoming_payments.insert(tk.END, "Upcoming Payments:\n")

    def add_column(self, title):
        column_frame = tk.Frame(self.columns_frame, bg="white", bd=2, relief=tk.GROOVE)
        column_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=5)

        # Título de la columna
        title_label = tk.Label(column_frame, text=title, bg="steelblue", fg="white", font=("Arial", 14, "bold"))
        title_label.pack(fill=tk.X, pady=5)

        # Canvas para las tarjetas
        cards_canvas = tk.Canvas(column_frame, bg="white", highlightthickness=0)
        cards_canvas.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Botón para añadir tarjetas
        add_card_button = tk.Button(column_frame, text="+ Add Card", bg="lightgreen", fg="black", font=("Arial", 10, "bold"), command=lambda: self.add_card(cards_canvas))
        add_card_button.pack(fill=tk.X, pady=5)

        self.columns.append(cards_canvas)

    def add_card(self, canvas):
        # Diálogo para obtener el texto de la tarjeta
        text = simpledialog.askstring("New Card", "Enter card text:")
        if text:
            # Crear tarjeta
            card_frame = tk.Frame(canvas, bg="lightyellow", relief=tk.RAISED, bd=2)
            card_frame.pack(pady=5, padx=5, fill=tk.X)

            card_label = tk.Label(card_frame, text=text, bg="lightyellow", fg="black", wraplength=150, justify="center", font=("Arial", 10))
            card_label.pack(pady=5)

            # Botones para agregar imagen o gráfica
            button_frame = tk.Frame(card_frame, bg="lightyellow")
            button_frame.pack(fill=tk.X, pady=5)

            add_image_button = tk.Button(button_frame, text="Add Image", bg="lightblue", command=lambda: self.add_image(card_frame))
            add_image_button.pack(side=tk.LEFT, padx=5)

            add_chart_button = tk.Button(button_frame, text="Add Chart", bg="lightblue", command=lambda: self.add_chart(card_frame))
            add_chart_button.pack(side=tk.LEFT, padx=5)

            # Hacer la tarjeta "draggable" y movible entre columnas
            self.make_draggable(card_frame, canvas)

    def add_image(self, parent):
        file_path = filedialog.askopenfilename(filetypes=[("Image Files", "*.png;*.jpg;*.jpeg;*.bmp")])
        if file_path:
            try:
                img = Image.open(file_path)
                img.thumbnail((150, 150))
                img_tk = ImageTk.PhotoImage(img)

                img_label = tk.Label(parent, image=img_tk, bg="lightyellow")
                img_label.image = img_tk
                img_label.pack(pady=5)

                # Guardar referencia para evitar recolección por el garbage collector
                self.image_references[img_label] = img_tk
            except Exception as e:
                tk.messagebox.showerror("Error", f"Failed to load image: {e}")

    def add_chart(self, parent):
        # Crear un gráfico simple
        fig, ax = plt.subplots()
        ax.plot([0, 1, 2, 3], [random.randint(0, 10) for _ in range(4)], marker="o")
        ax.set_title("Sample Chart")

        # Convertir el gráfico en imagen para tkinter
        buf = BytesIO()
        plt.savefig(buf, format="png")
        buf.seek(0)
        plt_img = Image.open(buf)
        plt_img.thumbnail((150, 150))
        chart_tk = ImageTk.PhotoImage(plt_img)

        chart_label = tk.Label(parent, image=chart_tk, bg="lightyellow")
        chart_label.image = chart_tk
        chart_label.pack(pady=5)

        # Guardar referencia para evitar recolección por el garbage collector
        self.image_references[chart_label] = chart_tk

        buf.close()

    def show_charts(self):
        # Crear un gráfico de ejemplo para ingresos y gastos
        fig, ax = plt.subplots()
        months = ["Jan", "Feb", "Mar", "Apr", "May"]
        income = [random.randint(1000, 5000) for _ in months]
        expenses = [random.randint(500, 4000) for _ in months]

        ax.bar(months, income, label="Income", color="green")
        ax.bar(months, expenses, label="Expenses", color="red", alpha=0.7)
        ax.set_title("Monthly Income vs Expenses")
        ax.legend()

        plt.show()

    def update_currency(self, event):
        new_currency = self.currency_selector.get()
        try:
            conversion_rate = self.currency_converter.get_rate(self.base_currency, new_currency)
            self.base_currency = new_currency

            # Actualizar etiquetas con la nueva moneda
            income = 10000 * conversion_rate  # Simulación
            expenses = 8000 * conversion_rate  # Simulación
            profit_loss = income - expenses

            self.total_income_label.config(text=f"Total Income: {income:.2f} {new_currency}")
            self.total_expenses_label.config(text=f"Total Expenses: {expenses:.2f} {new_currency}")
            self.profit_loss_label.config(text=f"Profit/Loss: {profit_loss:.2f} {new_currency}")
        except Exception as e:
            tk.messagebox.showerror("Error", f"Currency conversion failed: {e}")


    def make_draggable(self, widget, current_canvas):
        def on_start_drag(event):
            widget.startX = event.x
            widget.startY = event.y
            widget.current_canvas = current_canvas

        def on_drag(event):
            x = widget.winfo_x() - widget.startX + event.x
            y = widget.winfo_y() - widget.startY + event.y
            widget.place(x=x, y=y)

        def on_drop(event):
            for canvas in self.columns:
                if canvas.winfo_containing(event.x_root, event.y_root):
                    widget.place_forget()
                    widget.pack(in_=canvas, pady=5, padx=5, fill=tk.X)
                    break

        widget.bind("<Button-1>", on_start_drag)
        widget.bind("<B1-Motion>", on_drag)
        widget.bind("<ButtonRelease-1>", on_drop)

if __name__ == "__main__":
    root = tk.Tk()
    app = ProjectManagementApp(root)
    root.mainloop()
