# AI Report Automation

Genera reportes PDF profesionales desde archivos Excel o CSV con análisis estadístico e interpretación en lenguaje natural con IA.

---

## ¿Qué hace?

Sube tu archivo de datos, configura las opciones y obtén un PDF listo para presentar — sin necesidad de saber programación ni finanzas.

- **Carga** archivos Excel (.xlsx) o CSV hasta 16MB
- **Filtra** columnas, filas y valores específicos
- **Visualiza** tus datos con gráficos de barras, línea o pastel
- **Analiza** estadísticas automáticas (total, promedio, máximo, mínimo)
- **Detecta** anomalías en los datos
- **Genera** un resumen ejecutivo en lenguaje natural con IA
- **Descarga** el reporte en PDF

---

## Tecnologías

| Capa | Tecnología |
|------|------------|
| Backend | Python, Flask |
| Procesamiento | Pandas |
| Gráficos PDF | Matplotlib |
| Gráficos Web | Plotly.js |
| Generación PDF | fpdf2 |
| IA | HuggingFace — Meta Llama 3 8B |
| Frontend | HTML, CSS, JavaScript |

---

## Instalación local

### 1. Clonar el repositorio

```bash
git clone https://github.com/tu-usuario/ai-report-automation.git
cd ai-report-automation
```

### 2. Crear y activar entorno virtual

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Mac/Linux
source venv/bin/activate
```

### 3. Instalar dependencias

```bash
pip install -r requirements.txt
```

### 4. Configurar variables de entorno

Crea un archivo `.env` en la raíz del proyecto:

```
HF_API_KEY=hf_tu_token_aqui
```

Obtén tu token en [huggingface.co](https://huggingface.co) → Settings → Access Tokens.

### 5. Crear carpetas necesarias

```bash
mkdir uploads outputs
```

### 6. Ejecutar la aplicación

```bash
python app.py
```

Abre tu navegador en `http://127.0.0.1:5000`

---

## Estructura del proyecto

```
ai-report-automation/
├── app.py                  # Servidor Flask y rutas
├── processor.py            # Lectura y limpieza de archivos
├── ai_analyzer.py          # Estadísticas e integración con IA
├── visualizer.py           # Generación de gráficos
├── report_generator.py     # Construcción del PDF
├── templates/
│   └── index.html          # Interfaz web
├── static/
│   ├── css/
│   │   └── style.css       # Estilos
│   └── js/
│       └── app.js          # Lógica del frontend
├── uploads/                # Archivos subidos (temporal)
├── outputs/                # Reportes generados
├── .env                    # Variables de entorno (no subir a Git)
├── .gitignore
├── requirements.txt
└── README.md
```

---

## Uso

1. Sube tu archivo Excel o CSV
2. Selecciona las columnas a incluir
3. Elige el tipo de gráfico y la moneda
4. Ajusta el rango de filas si es necesario
5. Selecciona las secciones del PDF
6. Haz clic en **Generar PDF**
7. Descarga tu reporte

---

## Variables de entorno

| Variable | Descripción |
|----------|-------------|
| `HF_API_KEY` | Token de HuggingFace para el análisis con IA |

> Si no se configura el token, el sistema genera un resumen numérico como respaldo.

---

## Notas

- El análisis con IA requiere conexión a internet para llamar a la API de HuggingFace
- Archivos con formato monetario (`$`, comas) son procesados automáticamente
- Columnas como `Year`, `ID`, `Month Number` se excluyen del análisis estadístico automáticamente

---

## Autor

Frank — [GitHub](https://github.com/Frankmendo)