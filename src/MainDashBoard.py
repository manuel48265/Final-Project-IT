import tkinter as tk
from tkinter import ttk, messagebox
from tkinter.colorchooser import askcolor
import os
import matplotlib.pyplot as plt
from PIL import Image, ImageTk, ImageDraw
from Project import Proyecto, Ventana
from GeneralExpenses import PaginaGastosGenerales
from src.Currency import Currency
from src.TotalExpenses import PaginaTransacciones
from src.InterfazData import InterfazData  # Importar la nueva interfaz

class MainDashBoard:
    def __init__(self, root):
        self.root = root
        self.root.title("Project Dashboard")
        self.root.geometry("1200x700")
        self.root.configure(bg="#1E1E2F")  # Fondo oscuro moderno

        self.proyectos = []
        self.current_page = None
        self.project_states = {}

        self.setup_ui()

    def setup_ui(self):
        """Set up the main interface."""
        # Crear fondo degradado
        self.create_gradient_background()

        # Barra lateral
        sidebar = tk.Frame(self.root, bg="#2F2F3F", width=200)
        sidebar.pack(side=tk.LEFT, fill=tk.Y)

        tk.Label(sidebar, text="Menu", bg="#2F2F3F", fg="white", font=("Arial", 16, "bold"), pady=10).pack()
        tk.Button(sidebar, text="Projects", bg="#3F3F4F", fg="white", font=("Arial", 12), relief=tk.FLAT, command=self.mostrar_dashboard).pack(fill=tk.X, pady=5, padx=10)
        tk.Button(sidebar, text="General Costs", bg="#3F3F4F", fg="white", font=("Arial", 12), relief=tk.FLAT, command=self.mostrar_gastos_generales).pack(fill=tk.X, pady=5, padx=10)
        tk.Button(sidebar, text="Total Costs", bg="#3F3F4F", fg="white", font=("Arial", 12),
                  relief=tk.FLAT, command=self.mostrar_total_expenses).pack(fill=tk.X, pady=5, padx=10)

        # Combobox para seleccionar la divisa
        tk.Label(sidebar, text="Currency:", bg="#2F2F3F", fg="white", font=("Arial", 12)).pack(pady=5)
        self.currency_var = tk.StringVar()
        self.currency_combobox = ttk.Combobox(sidebar, textvariable=self.currency_var, state="readonly", font=("Arial", 12))
        self.currency_combobox['values'] = ["USD", "EUR", "GBP", "INR", "AUD", "CAD", "SGD", "CHF", "MYR", "JPY", "CNY", "LKR"]  # Ejemplo de monedas
        self.currency_combobox.pack(pady=5)
        self.currency_combobox.bind("<<ComboboxSelected>>", self.cambiar_divisa)

        # Contenedor principal
        self.main_frame = tk.Frame(self.root, bg="#1E1E2F")
        self.main_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)

        self.load_proyectos()
        self.mostrar_dashboard()

    def create_gradient_background(self):
        width, height = 1200, 700
        gradient = Image.new('RGB', (width, height), color=0)
        draw = ImageDraw.Draw(gradient)

        for i in range(height):
            color = (30, 30, 47 + int(208 * (i / height)))  # Degradado de #1E1E2F a #D0D0FF
            draw.line([(0, i), (width, i)], fill=color)

        self.gradient_image = ImageTk.PhotoImage(gradient)
        self.gradient_label = tk.Label(self.root, image=self.gradient_image)
        self.gradient_label.place(x=0, y=0, relwidth=1, relheight=1)

    def cambiar_divisa(self, event):
        """Only update the currency and amounts, without reloading the entire interface."""
        Currency.change_currency(self.currency_var.get())
        self.refrescar_divisa()

    def refrescar_divisa(self):
        """Recalculate and update the displayed amounts."""
        if self.current_page is not None:
            self.current_page.update_currency()
        else:
            self.mostrar_dashboard()
                
    def mostrar_dashboard(self):
        """Show the project dashboard."""
        self.current_page = None
        for widget in self.main_frame.winfo_children():
            widget.destroy()

        tk.Label(self.main_frame, text="Project Dashboard", bg="#1E1E2F", fg="white", font=("Arial", 20, "bold"), pady=10).pack()

        # Frame para crear proyectos
        frame_nuevo_proyecto = tk.Frame(self.main_frame, bg="#1E1E2F", pady=10)
        frame_nuevo_proyecto.pack(fill=tk.X, padx=10)

        #tk.Label(frame_nuevo_proyecto, text="Ruta DB:", bg="#1E1E2F", fg="white", font=("Arial", 12)).grid(row=0, column=0, padx=5, pady=5, sticky="w")
        #self.db_path_entry = tk.Entry(frame_nuevo_proyecto, width=30, font=("Arial", 12))
        #self.db_path_entry.grid(row=0, column=1, padx=5, pady=5)

        #tk.Label(frame_nuevo_proyecto, text="Google Drive:", bg="#1E1E2F", fg="white", font=("Arial", 12)).grid(row=0, column=2, padx=5, pady=5, sticky="w")
        #self.drive_link_entry = tk.Entry(frame_nuevo_proyecto, width=30, font=("Arial", 12))
        #self.drive_link_entry.grid(row=0, column=3, padx=5, pady=5)

        #tk.Button(frame_nuevo_proyecto, text="Crear Proyecto", command=self.crear_proyecto, bg="#4CAF50", fg="white", font=("Arial", 12), relief=tk.FLAT).grid(row=0, column=4, padx=5, pady=5)

        # Frame para mostrar proyectos
        self.frame_proyectos = tk.Frame(self.main_frame, bg="#1E1E2F")
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
        #self.canvas.bind_all("<Button-4>", self.scroll_horizontal)
        #self.canvas.bind_all("<Button-5>", self.scroll_horizontal)

        self.mostrar_proyectos()

    def mostrar_gastos_generales(self):
        """Show the general expenses page."""
        for widget in self.main_frame.winfo_children():
            widget.destroy()
        self.current_page = PaginaGastosGenerales(self.main_frame)

    def mostrar_total_expenses(self):
        """Show the page with the combined transactions table (income/expenses)."""
        self.current_page = None
        for widget in self.main_frame.winfo_children():
            widget.destroy()
        self.current_page = PaginaTransacciones(self.main_frame, self.proyectos)

    def scroll_horizontal(self, event):
        if event.num == 4:  # Desplazamiento hacia arriba
            self.canvas.xview_scroll(-1, "units")
        elif event.num == 5:  # Desplazamiento hacia abajo
            self.canvas.xview_scroll(1, "units")

    def crear_proyecto(self):
        """Create a new project."""
        db_path = self.db_path_entry.get()
        drive_link = self.drive_link_entry.get()

        if not db_path or not drive_link:
            messagebox.showerror("Error", "Please fill in all the fields.")
            return

        if not os.path.exists(db_path):
            messagebox.showerror("Error", "The database path doesn't exist.")
            return

        nuevo_proyecto = Proyecto(db_path, drive_link)
        self.proyectos.append(nuevo_proyecto)
        self.mostrar_proyecto(nuevo_proyecto)

    def load_proyectos(self):
        # Example projects
        self.proyectos.append(Proyecto("Proyecto 1", 'contabilidad.db', 'https://drive.google.com/drive/folders/your_folder_id'))
        self.proyectos.append(Proyecto("Proyecto 2", 'contabilidad.db', 'https://drive.google.com/drive/folders/your_folder_id'))
        self.proyectos.append(Proyecto("Proyecto 3", 'contabilidad.db', 'https://drive.google.com/drive/folders/your_folder_id'))

        # Inicializar estados de cada proyecto
        for p in self.proyectos:
            self.project_states[p.get_name()] = {
                "chart_visible": False,
                "period": None
            }

    def mostrar_proyectos(self):
        """Display all projects."""
        for proyecto in self.proyectos:
            proyecto.set_fechas(None, None)
            self.mostrar_proyecto(proyecto)

    def mostrar_proyecto(self, proyecto):

        print(f"Showing project: {proyecto.get_name()}")
        frame_proyecto = tk.Frame(self.scroll_frame, bg="#2F2F3F", borderwidth=2, relief="groove", padx=10, pady=10)
        frame_proyecto.pack(side=tk.LEFT, padx=10, pady=10)

        # Convertir el nombre del proyecto en un botón
        proyecto_button = tk.Button(frame_proyecto, text=f"Project: {os.path.basename(proyecto.get_name())}", 
                                    bg="#2F2F3F", fg="white", font=("Arial", 14, "bold"),
                                    command=lambda: self.mostrar_interfaz_data(proyecto))
        proyecto_button.pack(anchor="w")

        ingresos = proyecto.calcular_total_ingresos()
        gastos = proyecto.calcular_total_gastos()
        balance = proyecto.calcular_balance()

        tk.Label(frame_proyecto, text=f"Total Income: {round(ingresos,2)} {Currency.current_currency}", bg="#2F2F3F", fg="white", font=("Arial", 12)).pack(anchor="w")
        tk.Label(frame_proyecto, text=f"Total Expenses: {round(gastos,2)} {Currency.current_currency}", bg="#2F2F3F", fg="white", font=("Arial", 12)).pack(anchor="w")
        tk.Label(frame_proyecto, text=f"Balance: {round(balance,2)} {Currency.current_currency}", bg="#2F2F3F", fg="#4CAF50" if balance >= 0 else "#F44336", font=("Arial", 12, "bold")).pack(anchor="w")

        frame_proyecto.chart_label = None  # Etiqueta para el gráfico
        
        frame_proyecto.btn_grafico = tk.Button(frame_proyecto, text="Ver Gráfico",
                                              command=lambda: self.toggle_grafico(proyecto, frame_proyecto),
                                              bg="#2196F3", fg="white", font=("Arial", 12))
        frame_proyecto.btn_grafico.pack(pady=5)

        frame_proyecto.btn_quitar_grafico = tk.Button(frame_proyecto, text="Quitar Gráfico",
                                                      command=lambda: self.quitar_grafico(proyecto,frame_proyecto),
                                                      bg="#F44336", fg="white", font=("Arial", 12))
        frame_proyecto.btn_quitar_grafico.pack_forget()

        if self.project_states[proyecto.get_name()].get("chart_visible", False):
            periodo = self.project_states[proyecto.get_name()].get("period")
            if periodo and frame_proyecto.chart_label:
                frame_proyecto.chart_label.set_periodo(periodo)
            if periodo:
                self.toggle_grafico(proyecto, frame_proyecto, periodo)
            else: 
                self.toggle_grafico(proyecto, frame_proyecto)
            # Restaurar el periodo si se había guardado
            

    def toggle_grafico(self, proyecto: Proyecto, frame_proyecto, periodo='mensual'):
        """Show/Hide the chart."""
        if frame_proyecto.chart_label is None:
            ventana = Ventana(frame_proyecto, proyecto, periodo)
            frame_proyecto.btn_grafico.pack_forget()
            frame_proyecto.btn_quitar_grafico.pack(pady=5)
            frame_proyecto.chart_label = ventana
            frame_proyecto.btn_cambiar_periodo = tk.Button(frame_proyecto, text="Cambiar Periodo",
                                                          command=lambda: self.cambiar_periodo(frame_proyecto),
                                                          bg="#FFC107", fg="white", font=("Arial", 12))
            frame_proyecto.btn_cambiar_periodo.pack(pady=5)
            frame_proyecto.chart_label.mostrar_chart()
            self.project_states[proyecto.get_name()]["chart_visible"] = True

        else:
            self.quitar_grafico(proyecto,frame_proyecto)
            self.project_states[proyecto.get_name()]["chart_visible"] = False

    def cambiar_periodo(self, frame_proyecto):
        """Change the period and save it in the state."""
        frame_proyecto.chart_label.cambiar_periodo()
        # Guardar el periodo actual en project_states
        if frame_proyecto.chart_label and frame_proyecto.chart_label.periodo:
            nombre_proyecto = frame_proyecto.chart_label.proyecto.get_name()
            self.project_states[nombre_proyecto]["period"] = frame_proyecto.chart_label.periodo
        frame_proyecto.chart_label.eliminate_chart()
        frame_proyecto.chart_label.mostrar_chart()
        frame_proyecto.btn_cambiar_periodo.pack(pady=5)

    def quitar_grafico(self, proyecto, frame_proyecto):
        """Remove the chart if it exists."""
        if frame_proyecto.chart_label:
            frame_proyecto.chart_label.eliminate_chart()
            frame_proyecto.chart_label = None
            frame_proyecto.btn_quitar_grafico.pack_forget()
            frame_proyecto.btn_cambiar_periodo.pack_forget()
            frame_proyecto.btn_grafico.pack(pady=5)
            self.project_states[proyecto.get_name()]["chart_visible"] = False

    def mostrar_interfaz_data(self, proyecto):
        """Mostrar la interfaz de datos del proyecto seleccionado."""
        for widget in self.main_frame.winfo_children():
            widget.destroy()
        self.current_page = InterfazData(self.main_frame, proyecto)

    def on_closing(self):
        self.root.quit()
        self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = MainDashBoard(root)
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    root.mainloop()
