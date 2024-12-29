from google import genai
from google.genai import types
import pandas as pd
import subprocess
import os
from weasyprint import HTML
import re




GOOGLE_API_KEY = "AIzaSyAX25KeA27dvXLmJcJegsk7sQAFVO7DBE8"
client = genai.Client(api_key=GOOGLE_API_KEY)

MODEL_ID = "models/gemini-2.0-flash-exp"

def cargar_datos(archivo):
    return pd.read_csv(archivo)

# Envía los datos a la API de OpenAI para análisis
def analizar_datos(datos):
    prompt = f"""
    Analiza los siguientes datos financieros de una empresa:
    {datos.to_string()}
    
    Proporciona un resumen con insights, patrones, y recomendaciones.
    El resultado se va a usar para generar un pdf, por favor, no añadas 
    notas aclaratorias ni nada, solo el reporte financiero.

    A poder ser intenta explicar todo al máximo detalle.
    """
    
    response = client.models.generate_content(
        model=MODEL_ID,
        contents=prompt
    )

    return response.text


def Forecasting_Reports(datos):

    prompt = f"""
    "Generate a detailed forecasting report using the following financial data of the company. 
    The report should include a comprehensive analysis and projections for the upcoming months based on the input data. 
    Make sure to cover all possible aspects, including identifying patterns, trends, and any significant anomalies. 
    The report will be directly used to generate a PDF, so it should be clear, well-structured, and professional, with detailed explanations for each section.

    The input data is as follows:

    {datos.to_string()}

    The report should include, but not be limited to, the following sections:

        Trend Analysis:
            Identify and explain the observed trends in revenue and expenses over the year.
            Explain the growth or decrease in revenue and expenses, with emphasis on monthly and yearly changes.

        Future Projection (Forecasting):
            Use the provided data to make projections for revenue and expenses for the next 3, 6, and 12 months.
            Describe the forecasting model used, if applicable (e.g., regression methods, ARIMA, etc.).
            Include a range of projections to account for variability.

        Revenue-Expense Relationship Analysis:
            Explain how the relationship between revenue and expenses evolves throughout the year.
            Identify any points where expenses approach or exceed revenue and provide recommendations.

        External Factors (if relevant):
            Mention any external factors that may influence future financial outcomes (e.g., market changes, inflation, industry trends, etc.).

        Strategic Recommendations:
            Based on the previous analyses, offer recommendations on how the company can improve its financial results, optimize expenses, and leverage growth opportunities.

    Please ensure that the report is easily understandable for a reader without advanced financial expertise but detailed enough to be useful for decision-makers within the company.
    Do not add comments about the generation of the report, because your answer will be used in a PDF.
    Generate the report with the highest level of detail possible.
    Use professional language and structure the report clearly.
    The file should be in html format. Ready to be converted to pdf.
    Use latin-1 encoding for the output.
    Add page breaks when you consider it necessary.
    """
    
    response = client.models.generate_content(
        model=MODEL_ID,
        contents=prompt
    )

    return response.text

def limpiar_contenido(contenido):
    # Eliminar la cadena '''html
    contenido = re.sub(r"```html", "", contenido)
    # Eliminar los últimos caracteres específicos (por ejemplo, los últimos 3 caracteres)
    contenido = contenido[:-4] 
    return contenido

def generar_pdf(contenido, nombre_archivo="reporte.pdf"):
    # Limpiar el contenido
    contenido = limpiar_contenido(contenido)
    
    # Convertir el contenido a PDF
    HTML(string=contenido).write_pdf(nombre_archivo)

# Ejemplo de uso
if __name__ == "__main__":
    datos = cargar_datos("finanzas_empresa.csv")
    #analisis = analizar_datos(datos)
    #generar_pdf(analisis)
    forecasting = Forecasting_Reports(datos)
    generar_pdf(forecasting, "forecasting_report.pdf")

