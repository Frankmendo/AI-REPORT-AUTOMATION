import os
import pandas as pd
from huggingface_hub import InferenceClient

def generate_ai_summary(stats, anomalies, total_filas, total_columnas, lang='es', currency='$'):
    api_key = os.getenv('HF_API_KEY')
    print(f"API KEY encontrada: {bool(api_key)}")
    if not api_key:
        return None

    lang_instruction = "en español" if lang == 'es' else "in English"
    currency_name = {'$': 'dólares', 'S/': 'soles', '€': 'euros', '': ''}.get(currency, currency)

    stats_text = '\n'.join([
        f"- {col}: total {s['total']}, promedio {s['promedio']}, max {s['maximo']}, min {s['minimo']}"
        for col, s in stats.items()
    ])

    anomaly_text = ''
    if anomalies:
        anomaly_text = f"\nAnomalías detectadas en: {', '.join(anomalies.keys())}."

    prompt = f"""Eres un analista de datos financieros. Analiza estas estadísticas y escribe un resumen {lang_instruction} de 3-4 oraciones. Usa el símbolo {currency} delante de todos los números monetarios. Menciona los números más importantes y lo que significan para el negocio.

Datos del archivo: {total_filas} filas, {total_columnas} columnas.
Estadísticas:
{stats_text}
{anomaly_text}

Escribe el resumen mencionando los valores concretos más relevantes:"""

    try:
        os.environ['CURL_CA_BUNDLE'] = ''
        os.environ['REQUESTS_CA_BUNDLE'] = ''
        os.environ['HF_HUB_DISABLE_SSL_VERIFICATION'] = '1'

        client = InferenceClient(
            model="meta-llama/Meta-Llama-3-8B-Instruct",
            token=api_key
        )
        response = client.chat_completion(
            messages=[{"role": "user", "content": prompt}],
            max_tokens=300,
            temperature=0.5
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"HuggingFace error: {e}")
        return None


def analyze_data(df, lang='es', currency='$'):
    analysis = {}
    numeric_cols = df.select_dtypes(include='number').columns.tolist()

    EXCLUDE_FROM_ANALYSIS = ['year', 'month number', 'id', 'año']
    numeric_cols = [c for c in numeric_cols
                    if c.lower().strip() not in EXCLUDE_FROM_ANALYSIS]

    if len(numeric_cols) == 0:
        return {'summary': 'No se encontraron columnas numericas para analizar.'}

    analysis['total_filas'] = int(len(df))
    analysis['total_columnas'] = int(len(df.columns))
    analysis['columnas_numericas'] = numeric_cols

    def fmt(n):
        if n == int(n):
            return f"{int(n):,}"
        return f"{round(n, 2):,}"

    col_analysis = {}
    for col in numeric_cols:
        col_analysis[col] = {
            'total':    fmt(df[col].sum()),
            'promedio': fmt(round(float(df[col].mean()), 2)),
            'maximo':   fmt(df[col].max()),
            'minimo':   fmt(df[col].min()),
        }
    analysis['columnas'] = col_analysis

    anomalies = {}
    for col in numeric_cols:
        mean = df[col].mean()
        std = df[col].std()
        outliers = df[(df[col] > mean + 3*std) | (df[col] < mean - 3*std)]
        if len(outliers) > 0:
            anomalies[col] = int(len(outliers))
    analysis['anomalias'] = anomalies

    summary_parts = []
    for col, stats in col_analysis.items():
        summary_parts.append(
            f"{col}: total {stats['total']}, "
            f"promedio {stats['promedio']}, "
            f"max {stats['maximo']}, min {stats['minimo']}"
        )

    fallback_summary = (
        f"El archivo tiene {analysis['total_filas']} filas y "
        f"{analysis['total_columnas']} columnas.\n\n" +
        '\n'.join(summary_parts) +
        ('.\n\n' + f"Anomalias en: {', '.join(anomalies.keys())}." if anomalies else '.')
    )

    ai_summary = generate_ai_summary(
        col_analysis, anomalies,
        analysis['total_filas'], analysis['total_columnas'],
        lang=lang, currency=currency
    )

    analysis['summary'] = ai_summary if ai_summary else fallback_summary

    return analysis