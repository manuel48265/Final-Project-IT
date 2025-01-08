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
from src.InterfazData import InterfazData  # Import the new interface
from src.Constants import CURRENCY_TYPES
from src.ProjectManager import ProjectManager  # Import the new class
from src.ChatBot import ChatBotFrame  # Import the ChatBotFrame class
from src.DocumentationBoard import DocumentationBoard  # Import the DocumentationBoard class

class MainDashBoard:
    def __init__(self, root):
        self.root = root
        self.root.title("Project Dashboard")
        self.root.geometry("1200x700")
        self.root.configure(bg="#1E1E2F")  # Modern dark background

        self.project_manager = ProjectManager()
        self.current_page = None

        self.setup_ui()

    def setup_ui(self):
        """Set up the main interface."""
        # Create gradient background
        self.create_gradient_background()

        # Sidebar
        sidebar = tk.Frame(self.root, bg="#2F2F3F", width=200)
        sidebar.pack(side=tk.LEFT, fill=tk.Y)

        tk.Label(sidebar, text="Menu", bg="#2F2F3F", fg="white", font=("Arial", 16, "bold"), pady=10).pack()
        tk.Button(sidebar, text="Projects", bg="#3F3F4F", fg="white", font=("Arial", 12), relief=tk.FLAT, command=self.show_dashboard).pack(fill=tk.X, pady=5, padx=10)
        tk.Button(sidebar, text="General Costs", bg="#3F3F4F", fg="white", font=("Arial", 12), relief=tk.FLAT, command=self.show_general_expenses).pack(fill=tk.X, pady=5, padx=10)
        tk.Button(sidebar, text="Total Costs", bg="#3F3F4F", fg="white", font=("Arial", 12),
                  relief=tk.FLAT, command=self.show_total_expenses).pack(fill=tk.X, pady=5, padx=10)
        tk.Button(sidebar, text="ChatBot", bg="#3F3F4F", fg="white", font=("Arial", 12), relief=tk.FLAT, command=self.show_chatbot).pack(fill=tk.X, pady=5, padx=10)
        tk.Button(sidebar, text="Generate Documentation", bg="#3F3F4F", fg="white", font=("Arial", 12), relief=tk.FLAT, command=self.show_documentation).pack(fill=tk.X, pady=5, padx=10)

        # Combobox to select the currency
        tk.Label(sidebar, text="Currency:", bg="#2F2F3F", fg="white", font=("Arial", 12)).pack(pady=5)
        self.currency_var = tk.StringVar()
        self.currency_combobox = ttk.Combobox(sidebar, textvariable=self.currency_var, state="readonly", font=("Arial", 12))
        self.currency_combobox['values'] = CURRENCY_TYPES  # Example currencies
        self.currency_combobox.pack(pady=5)
        self.currency_combobox.bind("<<ComboboxSelected>>", self.change_currency)

        # Main container
        self.main_frame = tk.Frame(self.root, bg="#1E1E2F")
        self.main_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)

        self.show_dashboard()

    def create_gradient_background(self):
        width, height = 1200, 700
        gradient = Image.new('RGB', (width, height), color=0)
        draw = ImageDraw.Draw(gradient)

        for i in range(height):
            color = (30, 30, 47 + int(208 * (i / height)))  # Gradient from #1E1E2F to #D0D0FF
            draw.line([(0, i), (width, i)], fill=color)

        self.gradient_image = ImageTk.PhotoImage(gradient)
        self.gradient_label = tk.Label(self.root, image=self.gradient_image)
        self.gradient_label.place(x=0, y=0, relwidth=1, relheight=1)

    def change_currency(self, event):
        """Only update the currency and amounts, without reloading the entire interface."""
        Currency.change_currency(self.currency_var.get())
        self.refresh_currency()

    def refresh_currency(self):
        """Recalculate and update the displayed amounts."""
        if self.current_page is not None:
            self.current_page.update_currency()
        else:
            self.show_dashboard()
                
    def show_dashboard(self):
        """Show the project dashboard."""
        self.current_page = None
        for widget in self.main_frame.winfo_children():
            widget.destroy()

        tk.Label(self.main_frame, text="Project Dashboard", bg="#1E1E2F", fg="white", font=("Arial", 20, "bold"), pady=10).pack()

        # Frame to create projects
        frame_new_project = tk.Frame(self.main_frame, bg="#1E1E2F", pady=10)
        frame_new_project.pack(fill=tk.X, padx=10)

        # Frame to display projects
        self.frame_projects = tk.Frame(self.main_frame, bg="#1E1E2F")
        self.frame_projects.pack(pady=10, fill=tk.BOTH, expand=True)

        self.canvas = tk.Canvas(self.frame_projects, bg="#1E1E2F", highlightthickness=0)
        self.scroll_x = tk.Scrollbar(self.frame_projects, orient=tk.HORIZONTAL, command=self.canvas.xview)
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

        self.show_projects()

    def show_general_expenses(self):
        """Show the general expenses page."""
        for widget in self.main_frame.winfo_children():
            widget.destroy()
        self.current_page = PaginaGastosGenerales(self.main_frame)

    def show_total_expenses(self):
        """Show the page with the combined transactions table (income/expenses)."""
        self.current_page = None
        for widget in self.main_frame.winfo_children():
            widget.destroy()
        self.current_page = PaginaTransacciones(self.main_frame, self.project_manager.proyectos)

    def show_projects(self):
        """Display all projects."""
        for proyecto in self.project_manager.proyectos:
            proyecto.set_fechas(None, None)
            self.show_project(proyecto)

    def show_project(self, proyecto):
        print(f"Showing project: {proyecto.get_name()}")
        frame_project = tk.Frame(self.scroll_frame, bg="#2F2F3F", borderwidth=2, relief="groove", padx=10, pady=10)
        frame_project.pack(side=tk.LEFT, padx=10, pady=10)

        # Convert project name to a button
        project_button = tk.Button(frame_project, text=f"Project: {os.path.basename(proyecto.get_name())}", 
                                    bg="#2F2F3F", fg="white", font=("Arial", 14, "bold"),
                                    command=lambda: self.show_interface_data(proyecto))
        project_button.pack(anchor="w")

        ingresos = proyecto.calcular_total_ingresos()
        gastos = proyecto.calcular_total_gastos()
        balance = proyecto.calcular_balance()

        tk.Label(frame_project, text=f"Total Income: {round(ingresos,2)} {Currency.current_currency}", bg="#2F2F3F", fg="white", font=("Arial", 12)).pack(anchor="w")
        tk.Label(frame_project, text=f"Total Expenses: {round(gastos,2)} {Currency.current_currency}", bg="#2F2F3F", fg="white", font=("Arial", 12)).pack(anchor="w")
        tk.Label(frame_project, text=f"Balance: {round(balance,2)} {Currency.current_currency}", bg="#2F2F3F", fg="#4CAF50" if balance >= 0 else "#F44336", font=("Arial", 12, "bold")).pack(anchor="w")

        frame_project.chart_label = None  # Label for the chart
        
        frame_project.btn_chart = tk.Button(frame_project, text="View Chart",
                                              command=lambda: self.toggle_chart(proyecto, frame_project),
                                              bg="#2196F3", fg="white", font=("Arial", 12))
        frame_project.btn_chart.pack(pady=5)

        frame_project.btn_remove_chart = tk.Button(frame_project, text="Remove Chart",
                                                      command=lambda: self.remove_chart(proyecto,frame_project),
                                                      bg="#F44336", fg="white", font=("Arial", 12))
        frame_project.btn_remove_chart.pack_forget()

        if self.project_manager.project_states[proyecto.get_name()].get("chart_visible", False):
            period = self.project_manager.project_states[proyecto.get_name()].get("period")
            if period and frame_project.chart_label:
                frame_project.chart_label.set_period(period)
            if period:
                self.toggle_chart(proyecto, frame_project, period)
            else: 
                self.toggle_chart(proyecto, frame_project)

    def toggle_chart(self, proyecto: Proyecto, frame_project, period='mensual'):
        """Show/Hide the chart."""
        if frame_project.chart_label is None:
            ventana = Ventana(frame_project, proyecto, period)
            frame_project.btn_chart.pack_forget()
            frame_project.btn_remove_chart.pack(pady=5)
            frame_project.chart_label = ventana
            frame_project.btn_change_period = tk.Button(frame_project, text="Change Period",
                                                          command=lambda: self.change_period(frame_project),
                                                          bg="#FFC107", fg="white", font=("Arial", 12))
            frame_project.btn_change_period.pack(pady=5)
            frame_project.chart_label.show_chart()
            self.project_manager.project_states[proyecto.get_name()]["chart_visible"] = True

        else:
            self.remove_chart(proyecto,frame_project)
            self.project_manager.project_states[proyecto.get_name()]["chart_visible"] = False

    def change_period(self, frame_project):
        """Change the period and save it in the state."""
        frame_project.chart_label.change_period()
        # Save the current period in project_states
        if frame_project.chart_label and frame_project.chart_label.period:
            nombre_proyecto = frame_project.chart_label.proyecto.get_name()
            self.project_manager.project_states[nombre_proyecto]["period"] = frame_project.chart_label.period
        frame_project.chart_label.eliminate_chart()
        frame_project.chart_label.show_chart()
        frame_project.btn_change_period.pack(pady=5)

    def remove_chart(self, proyecto, frame_project):
        """Remove the chart if it exists."""
        if frame_project.chart_label:
            frame_project.chart_label.eliminate_chart()
            frame_project.chart_label = None
            frame_project.btn_remove_chart.pack_forget()
            frame_project.btn_change_period.pack_forget()
            frame_project.btn_chart.pack(pady=5)
            self.project_manager.project_states[proyecto.get_name()]["chart_visible"] = False

    def show_interface_data(self, proyecto):
        """Show the data interface of the selected project."""
        for widget in self.main_frame.winfo_children():
            widget.destroy()
        self.current_page = InterfazData(self.main_frame, proyecto)

    def show_chatbot(self):
        """Show the ChatBot frame."""
        for widget in self.main_frame.winfo_children():
            widget.destroy()
        self.current_page = ChatBotFrame(self.main_frame, self.project_manager)
        self.current_page.pack(fill=tk.BOTH, expand=True)

    def show_documentation(self):
        """Show the documentation generation frame."""
        for widget in self.main_frame.winfo_children():
            widget.destroy()
        self.current_page = DocumentationBoard(self.project_manager, self.main_frame)
        self.current_page.pack(fill=tk.BOTH, expand=True)

    def on_closing(self):
        self.root.quit()
        self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = MainDashBoard(root)
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    root.mainloop()

    print("End of program")
