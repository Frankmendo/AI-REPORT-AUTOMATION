import os
from fpdf import FPDF
from datetime import datetime


def clean_for_pdf(text):
    return str(text).replace('€', 'EUR').replace('£', 'GBP').replace('₹', 'INR')


class ReportPDF(FPDF):
    def header(self):
        self.set_font('Helvetica', 'B', 14)
        self.set_fill_color(30, 30, 30)
        self.set_text_color(255, 255, 255)
        self.cell(0, 12, 'AI Report Automation', fill=True, align='C', new_x='LMARGIN', new_y='NEXT')
        self.ln(4)

    def footer(self):
        self.set_y(-15)
        self.set_font('Helvetica', 'I', 8)
        self.set_text_color(128, 128, 128)
        self.cell(0, 10, f'Generado el {datetime.now().strftime("%d/%m/%Y %H:%M")} - Pagina {self.page_no()}', align='C')


def generate_report(df, charts, analysis, output_folder, sections=None, currency='$'):
    if sections is None:
        sections = ['summary', 'stats', 'anomalies', 'charts']

    # SImbolo limpio para PDF
    currency_pdf = currency.replace('€', 'EUR').replace('£', 'GBP')

    def fmt_currency(val):
        return f"{currency_pdf} {val}" if currency_pdf else str(val)

    pdf = ReportPDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)

    # Título
    pdf.set_font('Helvetica', 'B', 16)
    pdf.set_text_color(30, 30, 30)
    pdf.ln(4)
    pdf.cell(0, 10, 'Reporte de Analisis de Datos', align='C', new_x='LMARGIN', new_y='NEXT')
    pdf.ln(6)

    # Resumen general
    if 'summary' in sections:
        pdf.set_font('Helvetica', 'B', 12)
        pdf.set_fill_color(240, 240, 240)
        pdf.set_text_color(30, 30, 30)
        pdf.cell(0, 8, 'Resumen General', fill=True, new_x='LMARGIN', new_y='NEXT')
        pdf.ln(2)
        pdf.set_font('Helvetica', '', 10)
        pdf.set_text_color(50, 50, 50)
        pdf.multi_cell(0, 6, clean_for_pdf(analysis.get('summary', 'Sin resumen disponible.')))
        pdf.ln(6)

    # Estadisticas por columna
    if 'stats' in sections and 'columnas' in analysis:
        pdf.set_font('Helvetica', 'B', 12)
        pdf.set_fill_color(240, 240, 240)
        pdf.set_text_color(30, 30, 30)
        pdf.cell(0, 8, 'Estadisticas por Columna', fill=True, new_x='LMARGIN', new_y='NEXT')
        pdf.ln(2)

        pdf.set_font('Helvetica', 'B', 9)
        pdf.set_fill_color(30, 30, 30)
        pdf.set_text_color(255, 255, 255)
        pdf.cell(60, 7, 'Columna', fill=True, border=1)
        pdf.cell(30, 7, 'Total', fill=True, border=1, align='C')
        pdf.cell(30, 7, 'Promedio', fill=True, border=1, align='C')
        pdf.cell(30, 7, 'Maximo', fill=True, border=1, align='C')
        pdf.cell(30, 7, 'Minimo', fill=True, border=1, align='C', new_x='LMARGIN', new_y='NEXT')

        pdf.set_font('Helvetica', '', 9)
        pdf.set_text_color(30, 30, 30)
        for col, stats in analysis['columnas'].items():
            pdf.set_fill_color(255, 255, 255)
            pdf.cell(60, 6, str(col), border=1)
            pdf.cell(30, 6, fmt_currency(stats['total']), border=1, align='C')
            pdf.cell(30, 6, fmt_currency(stats['promedio']), border=1, align='C')
            pdf.cell(30, 6, fmt_currency(stats['maximo']), border=1, align='C')
            pdf.cell(30, 6, fmt_currency(stats['minimo']), border=1, align='C', new_x='LMARGIN', new_y='NEXT')
        pdf.ln(6)

    # Anomalias
    if 'anomalies' in sections and analysis.get('anomalias'):
        pdf.set_font('Helvetica', 'B', 12)
        pdf.set_fill_color(240, 240, 240)
        pdf.set_text_color(30, 30, 30)
        pdf.cell(0, 8, 'Anomalias Detectadas', fill=True, new_x='LMARGIN', new_y='NEXT')
        pdf.ln(2)
        pdf.set_font('Helvetica', '', 10)
        for col, count in analysis['anomalias'].items():
            pdf.cell(0, 6, f'- {col}: {count} valor(es) fuera del rango normal', new_x='LMARGIN', new_y='NEXT')
        pdf.ln(6)

    # Graficos
    if 'charts' in sections:
        pdf.set_font('Helvetica', 'B', 12)
        pdf.set_fill_color(240, 240, 240)
        pdf.set_text_color(30, 30, 30)
        pdf.cell(0, 8, 'Graficos', fill=True, new_x='LMARGIN', new_y='NEXT')
        pdf.ln(4)

        for chart_path in charts:
            if chart_path.endswith('.png') and os.path.exists(chart_path):
                pdf.image(chart_path, x=15, w=130)
                pdf.ln(4)

    report_path = os.path.join(output_folder, 'reporte.pdf')
    pdf.set_display_mode(zoom='real')
    pdf.output(report_path)
    return report_path