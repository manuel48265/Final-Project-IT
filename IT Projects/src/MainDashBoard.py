import tkinter as tk
from tkinter import ttk, messagebox
from tkinter.colorchooser import askcolor
import os
import matplotlib.pyplot as plt
from PIL import Image, ImageTk
from Project import Proyecto

class MainDashBoard:
    def __init__(self, root):
        self.root = root
        self.root.title("Dashboard de Proyectos")
        self.root.geometry("1200x700")
        self.root.configure(bg="#1E1E2F")  # Fondo oscuro moderno

        self.proyectos = []

        self.setup_ui()

    def setup_ui(self):
        # Barra lateral
        sidebar = tk.Frame(self.root, bg="#2F2F3F", width=200)
        sidebar.pack(side=tk.LEFT, fill=tk.Y)

        tk.Label(sidebar, text="Menú", bg="#2F2F3F", fg="white", font=("Arial", 16, "bold"), pady=10).pack()
        tk.Button(sidebar, text="Inicio", bg="#3F3F4F", fg="white", font=("Arial", 12), relief=tk.FLAT).pack(fill=tk.X, pady=5, padx=10)
        tk.Button(sidebar, text="Configuración", bg="#3F3F4F", fg="white", font=("Arial", 12), relief=tk.FLAT).pack(fill=tk.X, pady=5, padx=10)

        # Contenedor principal
        main_frame = tk.Frame(self.root, bg="#1E1E2F")
        main_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Título
        tk.Label(main_frame, text="Dashboard de Proyectos", bg="#1E1E2F", fg="white", font=("Arial", 20, "bold"), pady=10).pack()

        # Frame para crear proyectos
        frame_nuevo_proyecto = tk.Frame(main_frame, bg="#1E1E2F", pady=10)
        frame_nuevo_proyecto.pack(fill=tk.X, padx=10)

        tk.Label(frame_nuevo_proyecto, text="Ruta DB:", bg="#1E1E2F", fg="white", font=("Arial", 12)).grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.db_path_entry = tk.Entry(frame_nuevo_proyecto, width=30, font=("Arial", 12))
        self.db_path_entry.grid(row=0, column=1, padx=5, pady=5)

        tk.Label(frame_nuevo_proyecto, text="Google Drive:", bg="#1E1E2F", fg="white", font=("Arial", 12)).grid(row=0, column=2, padx=5, pady=5, sticky="w")
        self.drive_link_entry = tk.Entry(frame_nuevo_proyecto, width=30, font=("Arial", 12))
        self.drive_link_entry.grid(row=0, column=3, padx=5, pady=5)

        tk.Button(frame_nuevo_proyecto, text="Crear Proyecto", command=self.crear_proyecto, bg="#4CAF50", fg="white", font=("Arial", 12), relief=tk.FLAT).grid(row=0, column=4, padx=5, pady=5)

        # Frame para mostrar proyectos
        self.frame_proyectos = tk.Frame(main_frame, bg="#1E1E2F")
        self.frame_proyectos.pack(pady=10, fill=tk.BOTH, expand=True)

        self.canvas = tk.Canvas(self.frame_proyectos, bg="#1E1E2F", highlightthickness=0)
        self.scroll_x = tk.Scrollbar(self.frame_proyectos, orient=tk.HORIZONTAL, command=self.canvas.xview)
        self.scroll_frame = tk.Frame(self.canvas, bg="#1E1E2F")

        self.scroll_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(
                scrollregion=self.canvas.bbox("all")
            )
        )

        self.canvas.create_window((0, 0), window=self.scroll_frame, anchor="nw")
        self.canvas.configure(xscrollcommand=self.scroll_x.set)

        self.canvas.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        self.scroll_x.pack(side=tk.BOTTOM, fill=tk.X)

        # Habilitar desplazamiento táctil
        self.canvas.bind_all("<Button-4>", self.scroll_horizontal)
        self.canvas.bind_all("<Button-5>", self.scroll_horizontal)

        self.load_proyectos()
        self.mostrar_proyectos()

    def scroll_horizontal(self, event):
        if event.num == 4:  # Desplazamiento hacia arriba
            self.canvas.xview_scroll(-1, "units")
        elif event.num == 5:  # Desplazamiento hacia abajo
            self.canvas.xview_scroll(1, "units")

    def crear_proyecto(self):
        db_path = self.db_path_entry.get()
        drive_link = self.drive_link_entry.get()

        if not db_path or not drive_link:
            messagebox.showerror("Error", "Por favor, complete todos los campos.")
            return

        if not os.path.exists(db_path):
            messagebox.showerror("Error", "La ruta de la base de datos no existe.")
            return

        nuevo_proyecto = Proyecto(db_path, drive_link)
        self.proyectos.append(nuevo_proyecto)
        self.mostrar_proyecto(nuevo_proyecto)

    def load_proyectos(self):
        # Proyectos de ejemplo
        self.proyectos.append(Proyecto("Proyecto 1", 'contabilidad.db', 'https://drive.google.com/drive/folders/your_folder_id'))
        self.proyectos.append(Proyecto("Proyecto 2", 'contabilidad.db', 'https://drive.google.com/drive/folders/your_folder_id'))
        self.proyectos.append(Proyecto("Proyecto 3", 'contabilidad.db', 'https://drive.google.com/drive/folders/your_folder_id'))

    def mostrar_proyectos(self):
        for proyecto in self.proyectos:
            self.mostrar_proyecto(proyecto)

    def mostrar_proyecto(self, proyecto):
        frame_proyecto = tk.Frame(self.scroll_frame, bg="#2F2F3F", borderwidth=2, relief="groove", padx=10, pady=10)
        frame_proyecto.pack(side=tk.LEFT, padx=10, pady=10)

        tk.Label(frame_proyecto, text=f"Proyecto: {os.path.basename(proyecto.get_name())}", bg="#2F2F3F", fg="white", font=("Arial", 14, "bold")).pack(anchor="w")

        ingresos = proyecto.calcular_total_ingresos()
        gastos = proyecto.calcular_total_gastos()
        balance = proyecto.calcular_balance()

        tk.Label(frame_proyecto, text=f"Ingresos Totales: {ingresos}", bg="#2F2F3F", fg="white", font=("Arial", 12)).pack(anchor="w")
        tk.Label(frame_proyecto, text=f"Gastos Totales: {gastos}", bg="#2F2F3F", fg="white", font=("Arial", 12)).pack(anchor="w")
        tk.Label(frame_proyecto, text=f"Balance: {balance}", bg="#2F2F3F", fg="#4CAF50" if balance >= 0 else "#F44336", font=("Arial", 12, "bold")).pack(anchor="w")

        btn_grafico = tk.Button(frame_proyecto, text="Ver Gráfico", command=lambda: self.toggle_grafico(proyecto, frame_proyecto, btn_grafico), bg="#2196F3", fg="white", font=("Arial", 12))
        btn_grafico.pack(pady=5)

        frame_proyecto.chart_label = None  # Etiqueta para el gráfico

    def toggle_grafico(self, proyecto, frame_proyecto, btn_grafico):
        if frame_proyecto.chart_label:
            frame_proyecto.chart_label.destroy()
            frame_proyecto.chart_label = None
            btn_grafico.config(text="Ver Gráfico")
        else:
            chart_path = "chart.png"
            proyecto.generar_chart(chart_path=chart_path)

            img = Image.open(chart_path)
            img_tk = ImageTk.PhotoImage(img)

            chart_label = tk.Label(frame_proyecto, image=img_tk, bg="#2F2F3F")
            chart_label.image = img_tk  # Guardar referencia para evitar recolección por el garbage collector
            chart_label.pack()
            frame_proyecto.chart_label = chart_label
            btn_grafico.config(text="Quitar Gráfico")

    def on_closing(self):
        for frame in self.scroll_frame.winfo_children():
            if hasattr(frame, "chart_label") and frame.chart_label:
                frame.chart_label.destroy()

        if os.path.exists("chart.png"):
            os.remove("chart.png")

        self.root.quit()
        self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = MainDashBoard(root)
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    root.mainloop()
