import tkinter as tk
from tkinter import ttk
from FinancialReport import DocumentMaker
from ProjectManager import ProjectManager
from src.Constants import GOOGLE_API_KEY, MODEL_ID

class DocumentationBoard(tk.Frame):
    def __init__(self, project_manager: ProjectManager, master=None, api_key=GOOGLE_API_KEY, model_id=MODEL_ID):
        super().__init__(master)
        self.master = master
        self.document_maker = DocumentMaker(api_key=api_key, model_id=model_id)
        self.project_manager = project_manager
        self.create_widgets()

    def create_widgets(self):
        # Frame for project selection
        frame_selection = ttk.LabelFrame(self, text="Select Project", padding=(10, 10))
        frame_selection.grid(row=0, column=0, padx=10, pady=10, sticky="ew")

        self.combo_proyectos = ttk.Combobox(frame_selection, width=30)
        self.combo_proyectos['values'] = [p.get_name() for p in self.project_manager.proyectos]
        self.combo_proyectos.grid(row=0, column=0, padx=5, pady=5, sticky="ew")

        # Frame for buttons
        frame_buttons = ttk.LabelFrame(self, text="Report Options", padding=(10, 10))
        frame_buttons.grid(row=1, column=0, padx=10, pady=10, sticky="ew")

        self.btn_reporte_mensual_anual = ttk.Button(frame_buttons, text="Generate monthly and yearly report",
                                                    command=self.generate_monthly_year_report)
        self.btn_reporte_mensual_anual.grid(row=0, column=0, padx=5, pady=5, sticky="ew")

        self.btn_reporte_pronostico = ttk.Button(frame_buttons, text="Generate forecasting report",
                                                 command=self.generate_forecasting_report)
        self.btn_reporte_pronostico.grid(row=1, column=0, padx=5, pady=5, sticky="ew")

        self.btn_reporte_proyecto = ttk.Button(frame_buttons, text="Generate project-based report",
                                               command=self.project_based)
        self.btn_reporte_proyecto.grid(row=2, column=0, padx=5, pady=5, sticky="ew")

        # Adjust column weights for better resizing
        frame_selection.columnconfigure(0, weight=1)
        frame_buttons.columnconfigure(0, weight=1)

        # Center the frames
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        # Pack the main frame
        self.pack(fill="both", expand=True)

    def generate_monthly_year_report(self):
        data = self.project_manager.get_all_data()
        report = self.document_maker.monthly_year_report(data)
        self.document_maker.generate_pdf(report, "./docs/monthly_year_report.pdf")

    def generate_forecasting_report(self):
        data = self.project_manager.get_all_exhaustive_data()
        report = self.document_maker.forecasting_reports(data)
        self.document_maker.generate_pdf(report, "./docs/forecasting_report.pdf")

    def project_based(self):
        proyecto_seleccionado = self.combo_proyectos.get()
        proyecto = self.project_manager.get_proyectos(proyecto_seleccionado)
        datos = proyecto.get_accurate_data()
        reporte = self.document_maker.project_based(datos)
        self.document_maker.generate_pdf(reporte, f"./docs/{proyecto_seleccionado}_report.pdf")

def main():
    root = tk.Tk()
    app = DocumentationBoard(ProjectManager(), master=root)
    app.mainloop()

if __name__ == "__main__":
    main()
