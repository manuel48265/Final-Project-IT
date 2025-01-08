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

    def get_proyectos(self,name) -> Proyecto:
        for proyecto in self.proyectos:
            if proyecto.get_name() == name:
                return proyecto
        return None


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
            payments_str += (
                "-----------------------------------\n"
                f"📌 *Concept:* {p[0]}\n"
                f"💰 *Total Amount:* {p[1]:,.2f} {p[4]}\n"
                f"⏳ *Deadline:* {p[2]}\n"
                f"🧾 *Invoice Number:* {p[3]}\n"
                "-----------------------------------\n\n"
            )

        return payments_str
    
    def get_all_data(self):
        datos = ""

        datos += "The following data is given:" + "\n"

        datos += "There are some general expenses related to the company" + "\n"

        datos += self.gastos_db.get_basic_data()

        datos += "\n"

        datos += "There are some projects related to the company" + "\n"


        for proyecto in self.proyectos:
            datos += "For project: " + proyecto.get_name() + "\n" +"The following data is given:" + "\n"
            datos += proyecto.get_basic_data()
            datos += "\n"

        datos += "That's all the data available" + "\n"


        return datos
    
    def get_all_exhaustive_data(self):
        datos = ""

        datos += "The following data is given:" + "\n"

        datos += "There are some general expenses related to the company" + "\n"

        datos += self.gastos_db.get_basic_data()

        datos += "\n"

        datos += "There are some projects related to the company" + "\n"


        for proyecto in self.proyectos:
            datos += "For project: " + proyecto.get_name() + "\n" +"The following data is given:" + "\n"
            datos += proyecto.get_accurate_data()
            datos += "\n"

        datos += "That's all the data available" + "\n"

        return datos 

        

    
    


        

        
