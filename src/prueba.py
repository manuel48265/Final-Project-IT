import tkinter as tk
from tkhtmlview import HTMLLabel

root = tk.Tk()
root.title("Ejemplo de HTMLLabel")

html_content = """
<h1>Hola, Mundo!</h1>
<p>Este es un ejemplo de <b>HTMLLabel</b> mostrando contenido <i>HTML</i> y <i>Markdown</i>.</p>
"""

html_label = HTMLLabel(root, html=html_content)
html_label.pack(fill="both", expand=True)

root.mainloop()