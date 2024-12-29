import tkinter as tk
from tkinter import simpledialog, filedialog
from PIL import Image, ImageTk
import matplotlib.pyplot as plt
from io import BytesIO
import random

class ProjectManagementApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Project Management Tool")
        self.root.configure(bg="lightblue")

        # Frame para contener columnas
        self.columns_frame = tk.Frame(self.root, bg="lightblue")
        self.columns_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Crear columnas
        self.columns = []
        for column_name in ["To Do", "In Progress", "Done"]:
            self.add_column(column_name)

        # Almacenar referencias de imágenes
        self.image_references = {}

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
        file_path = filedialog.askopenfilename(filetypes=[("Image Files", "*.png"), ("JPEG Files", "*.jpg;*.jpeg"), ("Bitmap Files", "*.bmp")])
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
            widget.startX = None
            widget.startY = None
            widget.place_forget()  # Eliminar posición fija

            # Detectar la nueva columna
            for canvas in self.columns:
                if self.is_within_canvas(event.x_root, event.y_root, canvas):
                    widget.pack(in_=canvas, pady=5, padx=5)
                    widget.current_canvas = canvas
                    break

        widget.bind("<Button-1>", on_start_drag)
        widget.bind("<B1-Motion>", on_drag)
        widget.bind("<ButtonRelease-1>", on_drop)

    def is_within_canvas(self, x, y, canvas):
        canvas_x = canvas.winfo_rootx()
        canvas_y = canvas.winfo_rooty()
        canvas_width = canvas.winfo_width()
        canvas_height = canvas.winfo_height()
        return canvas_x <= x <= canvas_x + canvas_width and canvas_y <= y <= canvas_y + canvas_height

if __name__ == "__main__":
    root = tk.Tk()
    app = ProjectManagementApp(root)
    root.geometry("900x600")
    root.mainloop()

