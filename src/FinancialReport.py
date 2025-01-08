from google import genai
from google.genai import types
import pandas as pd
import subprocess
import os
from weasyprint import HTML
import re
from src.Constants import GOOGLE_API_KEY, MODEL_ID


class DocumentMaker:
    def __init__(self, api_key=GOOGLE_API_KEY, model_id=MODEL_ID):
        self.client = genai.Client(api_key=api_key)
        self.model_id = model_id

    def load_data(self, archivo):
        return pd.read_csv(archivo)

    def monthly_year_report(self, datos):
        prompt = f"""
            Create a comprehensive financial report detailing the company's monthly and yearly performance.  
            The report should include the following sections:  
            1. **Executive Summary:**  
            - Provide a concise overview of the financial performance, emphasizing key figures, trends, and significant changes from previous months/years.  
            - Use simple, clear language that highlights essential insights.  

            2. **Income Breakdown:**  
            - Present a categorized summary of income, segmented by source (e.g., product lines, services).  
            - Use bullet points or tables to clearly outline each income stream. Avoid complex charts and use text-based descriptions of trends.  

            3. **Expense Breakdown:**  
            - List expenses by category, detailing significant cost areas (e.g., operations, salaries, marketing).  
            - Include comparisons to previous periods to highlight increases or reductions in spending.   

            4. **Profit and Loss Calculation:**  
            - Summarize profit or loss calculations in a clear, itemized format.  
            - Provide step-by-step explanations without relying on visual graphs. Use text-based comparisons to describe profit margins and variances.  

            5. **Key Insights and Recommendations:**  
            - Offer actionable insights derived from the financial analysis.  
            - Highlight areas of concern or opportunity, focusing on cost-saving measures, revenue growth, and efficiency improvements.  

            **Important Considerations:**  
            - Ensure the report is written in a professional and accessible tone, suitable for both non-expert readers and decision-makers.  
            - Use structured headings, subheadings, and bullet points for clarity.  
            - Avoid incorporating charts, visual elements, or non-text outputs.  
            - Present the report in plain HTML, prepared for PDF conversion, and ensure encoding in Latin-1.  
            - Use simple HTML page breaks (`<div style="page-break-before: always;"></div>`) where needed for section separation.  

            The data to analyze is as follows:  
            {datos}  

            Generate the report with the highest level of detail and professionalism, focusing on text-based explanations rather than visual representations.  
        """

        response = self.client.models.generate_content(
            model=self.model_id,
            contents=prompt
        )
        return response.text

    def project_based(self, datos: str):
        prompt = f"""
            Write a professional and comprehensive project-based financial report template.  
            The report should focus on providing a clear and detailed breakdown of income, expenses, and profit/loss for each project.  
            The structure of the document should include the following sections:  

            1. **Title Page:**  
                - Report Title  
                - Date of the Report  

            2. **Table of Contents:**  
                - List all sections with page numbers for easy navigation. Use simple text-based links instead of visual elements.  

            3. **Executive Summary:**  
                - Provide a brief overview of the project's financial performance.  
                - Highlight key figures, trends, and significant outcomes using clear and concise language.  

            4. **Project Overview:**  
                - Describe the project name, objectives, timeline, and stakeholders.  
                - Keep the description brief and to the point.  

            5. **Income Breakdown:**  
                - Present an itemized list of income sources with details such as:  
                    - Amount received  
                    - Date of payment  
                    - Contribution percentage to total income  
                - Use a simple HTML table to display income data. Ensure the format is text-based without complex visualizations.  
                - Example:  
                    ```html
                    <table border="1">  
                    <tr><th>Source</th><th>Amount</th><th>Date</th><th>% Contribution</th></tr>  
                    <tr><td>Client A</td><td>$10,000</td><td>2025-01-01</td><td>50%</td></tr>  
                    </table>  

            6. **Expense Breakdown:**

                - List all expenses by category (e.g., labor, materials, operational costs).
                - Provide the amount, date, and percentage contribution to total expenses.
                - Display data in a structured, text-based table format.
                Example:
                    ```html
                    <table border="1">  
                    <tr><th>Category</th><th>Amount</th><th>Date</th><th>% Contribution</th></tr>  
                    <tr><td>Labor</td><td>$5,000</td><td>2025-01-05</td><td>25%</td></tr>  
                    </table> 

            7. **Profit/Loss Analysis:**

                - Calculate profit or loss by subtracting total expenses from total income.
                - Present the calculation step by step in a table format, including profit margins in percentage form.
                - Avoid charts or graphs; use clear text-based summaries instead.

            8. **Key Insights and Recommendations:**

                - Summarize major findings from the financial data.
                - Offer actionable suggestions for improving profitability or reducing costs.

            9. **Appendices (Optional):**
                - Reference any supporting documentation such as invoices or contracts, but avoid including actual files in the generated output.

            **Important considerations:**

                - Write in a clear and professional tone, ensuring accessibility for non-expert readers and decision-makers.
                - Structure the report using headings, subheadings, and bullet points for clarity.
                - Avoid references to the report generation process. Focus on content presentation for PDF export.
                - The report should be in plain HTML format, ready for PDF conversion, and encoded in Latin-1.
                - Insert page breaks where necessary using:
                    <div style="page-break-before: always;"></div> 

            The data to be analyzed is as follows:
                {datos}

            Generate the report with the highest level of detail while ensuring readability and professionalism. Focus on text and table-based formatting rather than visual elements. 

        """

        response = self.client.models.generate_content(
            model=self.model_id,
            contents=prompt
        )
        return response.text

    def forecasting_reports(self, datos):
        prompt = f"""
            Generate a detailed financial forecasting report based on the company’s financial data provided.  
            The report should analyze trends and project financial outcomes for the upcoming months.  
            It should include the following sections:  

            1. **Trend Analysis:**  
                - Identify and explain observed trends in revenue and expenses over the past year.  
                - Highlight growth or decline in revenue and expenses, focusing on monthly and yearly variations.  
                - Use clear, concise text descriptions to outline trends without relying on visual charts or graphs.  

            2. **Future Projection (Forecasting):**  
                - Use the provided financial data to project revenue and expenses for the next 3, 6, and 12 months.  
                - Describe the methodology used for projections (e.g., historical averages, linear regression). Avoid in-depth descriptions of advanced models that may not be supported by the model's capabilities.  
                - Present projected figures in table format, showing the forecast period and estimated values.  
                - Example:  
                ```html
                <table border="1">  
                <tr><th>Period</th><th>Projected Revenue</th><th>Projected Expenses</th></tr>  
                <tr><td>Next 3 Months</td><td>$150,000</td><td>$120,000</td></tr>  
                </table>  

            3. **Revenue-Expense Relationship Analysis:**
                - Explain how revenue and expenses interact throughout the year.
                - Identify periods where expenses closely approach or exceed revenue.
                - Offer text-based insights on how to manage or optimize the balance between revenue and expenses.

            4. **External Factors (Optional):**
                - Mention any potential external factors that could influence projections (e.g., market trends, inflation, economic shifts).
                - Keep this section brief and general to avoid over-complexity.
            
            5. **Strategic Recommendations:**
                - Based on the trend and projection analysis, provide actionable recommendations for improving financial performance.
                - Suggest areas for reducing costs, increasing revenue, and capitalizing on growth opportunities.

            **Important Considerations:**

                - Structure the report in a professional yet accessible tone, making it suitable for non-expert readers and decision-makers.
                - Use headings, subheadings, and bullet points to enhance readability.
                - Avoid references to the report generation process or the use of charts. Focus on text and tables for presenting data.
                - Prepare the report in plain HTML, ready for PDF conversion, and ensure Latin-1 encoding.
                - Use simple page breaks with:
                    <div style="page-break-before: always;"></div>  

            The data to analyze is as follows:
            {datos}

            Generate the report with as much detail as possible, prioritizing clarity, professionalism, and a structured format.
        """

        response = self.client.models.generate_content(
            model=self.model_id,
            contents=prompt
        )
        return response.text

    def clean_content(self, contenido):
        contenido = re.sub(r"```html", "", contenido)
        contenido = contenido[:-4]
        return contenido

    def generate_pdf(self, contenido, nombre_archivo="report.pdf"):
        contenido = self.clean_content(contenido)
        HTML(string=contenido).write_pdf(nombre_archivo)

# Example usage
if __name__ == "__main__":
    document_maker = DocumentMaker(api_key=GOOGLE_API_KEY, model_id=MODEL_ID)
    datos = document_maker.load_data("finanzas_empresa.csv")

    monthly_year_report = document_maker.monthly_year_report(datos)
    document_maker.generate_pdf(monthly_year_report, "./docs/monthly_year_report.pdf")

    project_based = document_maker.project_based(datos)
    document_maker.generate_pdf(project_based, "./docs/project_based.pdf")

    forecasting = document_maker.forecasting_reports(datos)
    document_maker.generate_pdf(forecasting, "./docs/forecasting_report.pdf")

