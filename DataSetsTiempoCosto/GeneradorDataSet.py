import numpy as np
import pandas as pd
# Crear un diccionario con los nombres de las columnas y sus rangos
data = {'UX Designer': np.random.normal(2,1, 1000),
        'UI Designer': np.random.randint(0, 2, 1000),
        'Front-End Designer': 
        'Front-End Developer':
        'Full-Stack Developer':
        'Software Developers':
        'Systems Engineer':
        'Database Administrator':
        'Data Scientist':
        'Data Analyst':
        'DevOps Engineer':
        'Time': np.random.uniform(80, 120, 1000)}

# Crear un DataFrame de pandas
df = pd.DataFrame(data)

# Guardar el DataFrame como un archivo CSV
df.to_csv('datos.csv', index=False)