import os
import time
import pandas as pd
import traceback
from flask import Flask, render_template, request, jsonify, send_file
from processor import process_file
from visualizer import generate_charts
from ai_analyzer import analyze_data
from report_generator import generate_report
from werkzeug.utils import secure_filename
import tempfile
import json
import math
from dotenv import load_dotenv
load_dotenv()


app = Flask(__name__)

UPLOAD_FOLDER = tempfile.gettempdir()
OUTPUT_FOLDER = 'outputs'

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['OUTPUT_FOLDER'] = OUTPUT_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

ALLOWED_EXTENSIONS = {'csv', 'xlsx'}


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/preview', methods=['POST'])
def preview_file():

    t0 = time.time()

    if 'file' not in request.files:
        return jsonify({'error': 'No se encontró archivo'}), 400

    file = request.files['file']

    if file.filename == '':
        return jsonify({'error': 'Nombre de archivo vacío'}), 400

    if not allowed_file(file.filename):
        return jsonify({'error': 'Solo CSV o Excel'}), 400

    filename = secure_filename(file.filename)
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    
    t0 = time.time()
    file.save(filepath)
    print(f"Solo file.save(): {time.time() - t0:.2f}s")


    try:
        print("📥 Procesando archivo...")
        df = process_file(filepath)

        if df is None or df.empty:
            return jsonify({'error': 'Archivo vacío o mal estructurado'}), 400
        
        for col in df.columns:
            if df[col].dtype == object:
                cleaned = df[col].astype(str).str.replace(r'[\$,]', '', regex=True).str.strip()
                converted = pd.to_numeric(cleaned, errors='coerce')
                if converted.notna().sum() > len(df) * 0.5:
                    df[col] = converted

        # LIMPIAR COLUMNAS
        df.columns = df.columns.astype(str).str.strip()

        # LIMPIAR ESPACIOS EN DATOS
        for col in df.columns:
            try:
                df[col] = df[col].astype(str).str.strip()
            except:
                pass

        print("\n=== DATAFRAME ===")
        print(df.head())

        print("\n=== COLUMNAS ===")
        print(df.columns.tolist())

        print("\n=== DTYPES ANTES ===")
        print(df.dtypes)

        # DETECCION INTELIGENTE DE COLUMNAS NUMERICAS
        for col in df.columns:
            converted = pd.to_numeric(df[col], errors='coerce')

            # Si más del 50% son números → convertir
            if converted.notna().sum() > len(df) * 0.5:
                df[col] = converted

        print("\n=== DTYPES DESPUÉS ===")
        print(df.dtypes)

        numeric_cols = df.select_dtypes(include='number').columns.tolist()
        text_cols = [c for c in df.columns if c not in numeric_cols]

        print("\nNUMÉRICAS:", numeric_cols)
        print("TEXTO:", text_cols)

        if len(numeric_cols) == 0:
            return jsonify({
                'error': 'No se detectaron columnas numéricas válidas. Revisa el formato del archivo.'
            }), 400

        # VALORES UNICOS PARA FILTROS

        unique_values = {}
        for col in text_cols:
            try:
                vals = df[col].dropna().unique().tolist()
                unique_values[col] = [v for v in vals if v == v][:50] 
            except:
                unique_values[col] = []

        preview = {
            'columns': df.columns.tolist(),
            'numeric_columns': numeric_cols,
            'text_columns': text_cols,
            'unique_values': unique_values,
            'rows': int(len(df)),
            'preview_data': df.head(5).to_dict(orient='records'),
            'filename': filename
        }

        print(f"\nTiempo total: {time.time() - t0:.2f}s")

        clean_preview = []
        for row in preview['preview_data']:
            clean_row = {}
            for k, v in row.items():
                if isinstance(v, float) and math.isnan(v):
                    clean_row[k] = None
                else:
                    clean_row[k] = v
            clean_preview.append(clean_row)
        preview['preview_data'] = clean_preview

        #json
        try:
            json.dumps(preview)
            print("JSON OK")
        except Exception as e:
            print(f"JSON ERROR: {e}")

        return jsonify(preview)

    except Exception as e:
        print("\n❌ ERROR COMPLETO:")
        traceback.print_exc()

        return jsonify({
            'error': f'Error al procesar: {str(e)}'
        }), 500


@app.route('/generate', methods=['POST'])
def generate():
    data = request.get_json()

    filename = data.get('filename')
    selected_columns = data.get('columns', [])
    chart_type = data.get('chart_type', 'bar')
    row_range = data.get('row_range', None)
    row_filters = data.get('row_filters', {})
    sections = data.get('sections', ['summary', 'stats', 'anomalies', 'charts'])

    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    df = process_file(filepath)

    # LIMPIEZA CONSISTENTE
    df.columns = df.columns.astype(str).str.strip()
    for col in df.columns:
        if df[col].dtype == "object":
            df[col] = df[col].astype(str).str.strip()

    # DETECTAR NUMERICOS
    for col in df.columns:
        converted = pd.to_numeric(df[col], errors='coerce')
        if converted.notna().sum() > len(df) * 0.5:
            df[col] = converted

    # Filtrar filas por valores
    if row_filters:
        for col, values in row_filters.items():
            if col in df.columns and values:
                df = df[df[col].astype(str).isin(values)]

    # Filtrar columnas
    if selected_columns:
        text_cols = [c for c in df.columns if c not in df.select_dtypes(include='number').columns]
        df = df[text_cols + [c for c in selected_columns if c in df.columns]]

    # Rango de filas
    if row_range:
        df = df.iloc[row_range[0]:row_range[1]]

    EXCLUDE_FROM_CHARTS = ['year', 'month number', 'month', 'año', 'id']
    numeric_cols = df.select_dtypes(include='number').columns.tolist()
    chart_cols = [c for c in numeric_cols if c.lower().strip() not in EXCLUDE_FROM_CHARTS]
    df_chart = df[df.select_dtypes(exclude='number').columns.tolist() + chart_cols]

    t1 = time.time()
    charts = generate_charts(df_chart, OUTPUT_FOLDER, chart_type) if 'charts' in sections else []
    print(f"Charts: {time.time() - t1:.2f}s")

    t2 = time.time()
    lang = data.get('lang', 'es')
    currency = data.get('currency', '$')
    analysis = analyze_data(df, lang=lang, currency=currency)
    print(f"Analyze: {time.time() - t2:.2f}s")

    t3 = time.time()
    currency = data.get('currency', '$')
    report_path = generate_report(df, charts, analysis, OUTPUT_FOLDER, sections, currency)
    print(f"Report: {time.time() - t3:.2f}s")

    return jsonify({
        'success': True,
        'report': report_path,
        'analysis': analysis
    })


@app.route('/download/<filename>')
def download_file(filename):
    filepath = os.path.join(OUTPUT_FOLDER, filename)
    return send_file(filepath, as_attachment=True)


if __name__ == '__main__':
    app.run(debug=True)