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
def monthly_year_report(datos):

    prompt = f"""
        Create a comprehensive financial report that details the monthly and yearly performance of the company. 
        The report should include the following sections:
        
        1. Executive Summary: A concise overview of the financial performance, highlighting key figures and trends.
        2. Income Breakdown: A detailed analysis of total income, segmented by category and source.
        3. Expense Breakdown: A thorough analysis of total expenses, categorized appropriately.
        4. Profit and Loss Calculation: A clear explanation of profit or loss, with supporting calculations.
        5. Key Insights and Recommendations: Actionable insights and recommendations based on the financial analysis.
        
        The data to be analyzed is as follows:
        {datos.to_string()}

        The report should be written in a professional and clear tone, suitable for both non-expert readers and decision-makers. It should be easy to understand without requiring advanced financial knowledge, but also detailed enough to provide value for strategic decision-making.

        Ensure that the report is structured in a logical and visually appealing way. Use appropriate headings, subheadings, and bullet points to organize the content. Avoid any references to the report generation process, as the content will be used in a PDF format.

        The document should be in HTML format, prepared for PDF conversion, and encoded in Latin-1. Include page breaks as necessary to ensure the document is well-organized.

        Please generate the report with the highest level of detail possible, ensuring clarity and professionalism throughout.
    """


    
    response = client.models.generate_content(
        model=MODEL_ID,
        contents=prompt
    )

    return response.text


def proyect_based(datos):

    prompt = f"""
    Write a professional and comprehensive document template for project-based financial reports. The report should focus on providing a detailed breakdown of income, expenses, and profit/loss for each project. The structure of the document should include the following sections:

    1. Title Page:
    - Report title
    - Date of the report
    - Company name and logo

    2. Table of Contents:
    - List all sections and their page numbers for easy navigation.

    3. Executive Summary:
    - Provide a brief overview of the project’s financial performance, highlighting key outcomes and trends.

    4. Project Overview:
    - Describe the project name, timeline, objectives, and stakeholders involved.

    5. Income Breakdown:
    - Itemized list of income sources for the project, including:
        - Amounts received per source
        - Dates of payments
        - Percentage contribution of each source to the total income
    - Present the data in a table format with columns for source, amount, date, and percentage contribution.

    6. Expense Breakdown:
    - Itemized list of expenses, categorized into groups such as labor, materials, operational costs, marketing, etc.
        - Amount spent in each category
        - Dates of expenses
        - Percentage contribution of each category to the total expenses
    - Present the data in a table format with columns for category, amount, date, and percentage contribution.

    7. Profit/Loss Analysis:
    - Provide a detailed calculation of profit or loss:
        - Total income minus total expenses
        - Include percentage margins (profit or loss as a percentage of total income)
    - Present the profit/loss information in a table format, showing total income, total expenses, profit/loss, and the profit margin.

    8. Key Insights and Recommendations:
    - Summarize the key findings from the financial data.
    - Provide actionable recommendations for improving project profitability or cost management.

    9. Appendices:
        - Include supporting documentation such as receipts, invoices, contracts, or other relevant financial records.

    The document should use a professional tone and formatting style, with clear headings, bullet points, and table formatting for data presentation. Ensure the content is detailed and avoids ambiguities, making it suitable for stakeholders who may not be familiar with the project’s financial nuances.

    The data to be analyzed is as follows:
    {datos.to_string()}

    The report should be written in a professional and clear tone, suitable for both non-expert readers and decision-makers. It should be easy to understand without requiring advanced financial knowledge, but also detailed enough to provide value for strategic decision-making.

    Ensure that the report is structured in a logical and visually appealing way. Use appropriate headings, subheadings, and bullet points to organize the content. Avoid any references to the report generation process, as the content will be used in a PDF format.

    The document should be in HTML format, prepared for PDF conversion, and encoded in Latin-1. Include page breaks as necessary to ensure the document is well-organized.

    Please generate the report with the highest level of detail possible, ensuring clarity and professionalism throughout.
    """


    response = client.models.generate_content(
        model=MODEL_ID,
        contents=prompt
    )

    return response.text



def Forecasting_Reports(datos):

    prompt = f"""
        Generate a detailed forecasting report using the following financial data of the company. 
        The report should include a comprehensive analysis and projections for the upcoming months based on the input data. 
        Make sure to cover all possible aspects, including identifying patterns, trends, and any significant anomalies. 
        The report will be directly used to generate a PDF, so it should be clear, well-structured, and professional, with detailed explanations for each section.

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

        The data to be analyzed is as follows:
        {datos.to_string()}

        The report should be written in a professional and clear tone, suitable for both non-expert readers and decision-makers. It should be easy to understand without requiring advanced financial knowledge, but also detailed enough to provide value for strategic decision-making.

        Ensure that the report is structured in a logical and visually appealing way. Use appropriate headings, subheadings, and bullet points to organize the content. Avoid any references to the report generation process, as the content will be used in a PDF format.

        The document should be in HTML format, prepared for PDF conversion, and encoded in Latin-1. Include page breaks as necessary to ensure the document is well-organized.

        Please generate the report with the highest level of detail possible, ensuring clarity and professionalism throughout.
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

    # Generar el reporte mensual y anual
    monthly_year_report = monthly_year_report(datos)
    generar_pdf(monthly_year_report, "./docs/monthly_year_report.pdf")

    # Generar el reporte basado en proyectos
    proyect_based = proyect_based(datos)
    generar_pdf(proyect_based, "./docs/proyect_based.pdf")

    # Generar el reporte de pronóstico
    forecasting = Forecasting_Reports(datos)
    generar_pdf(forecasting, "./docs/forecasting_report.pdf")

