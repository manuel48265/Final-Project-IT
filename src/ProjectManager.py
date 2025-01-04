import os
from Project import Proyecto
from GeneralExpenses import GastosDB

class ProjectManager:
    def __init__(self):
        self.proyectos = []
        self.project_states = {}
        self.gastos_db = GastosDB("genericos.db")
        self.load_proyectos()

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


    def _get_upcoming_payments(self):
        payments = []
        for proyecto in self.proyectos:
            payments.extend(proyecto.get_upcoming_payments())

        payments.extend(self.gastos_db.get_upcoming_payments())
        
        payments.sort(key=lambda x: x[2])

        return payments
    
    def get_upcoming_payments_string(self):
        payments = self._get_upcoming_payments()
        payments_str = ""
        for p in payments:
            
            payments_str += f"Concept: {p[0]} Total Amount:{p[1]} Currency: {p[4]} Deadline: {p[2]} Invoice Number: {p[3]}\n"
            payments_str += "-----------------------------------\n"


        return payments_str
    
    


        

        
