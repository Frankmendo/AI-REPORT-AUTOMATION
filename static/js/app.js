// Estado global
const state = {
    file: null,
    filename: null,
    columns: [],
    numericColumns: [],
    textColumns: [],
    uniqueValues: {},
    totalRows: 0,
    chartType: 'bar',
    currency: '$',
    previewData: []
};

// Elementos
const uploadArea    = document.getElementById('uploadArea');
const fileInput     = document.getElementById('fileInput');
const fileSelected  = document.getElementById('fileSelected');
const uploadBtn     = document.getElementById('uploadBtn');

// Upload
uploadArea.addEventListener('click', () => fileInput.click());

uploadArea.addEventListener('dragover', (e) => {
    e.preventDefault();
    uploadArea.classList.add('dragover');
});

uploadArea.addEventListener('dragleave', () => uploadArea.classList.remove('dragover'));

uploadArea.addEventListener('drop', (e) => {
    e.preventDefault();
    uploadArea.classList.remove('dragover');
    if (e.dataTransfer.files[0]) handleFile(e.dataTransfer.files[0]);
});

fileInput.addEventListener('change', () => {
    if (fileInput.files[0]) handleFile(fileInput.files[0]);
});

function handleFile(file) {
    state.file = file;
    fileSelected.textContent = `📄 ${file.name}`;
    fileSelected.style.display = 'block';
    uploadBtn.disabled = false;
}

uploadBtn.addEventListener('click', async () => {
    showSpinner('Leyendo archivo...');
    const formData = new FormData();
    formData.append('file', state.file);

    try {
        const res  = await fetch('/preview', { method: 'POST', body: formData });
        const data = await res.json();

        if (data.error) { showError(data.error); return; }

        state.filename      = data.filename;
        state.columns       = data.columns;
        state.numericColumns = data.numeric_columns;
        state.textColumns   = data.text_columns || [];
        state.uniqueValues  = data.unique_values || {};
        state.totalRows     = data.rows;
        state.previewData   = data.preview_data;

        buildFilters();
        buildPreviewTable();
        buildPlotlyChart();
        goToSection(2);

    } catch (e) {
        showError('Error al leer el archivo.');
    } finally {
        hideSpinner();
    }
});

function buildFilters() {
    const list = document.getElementById('columnsList');
    list.innerHTML = '';

    // Columnas numéricas
    state.numericColumns.forEach(col => {
        const label = document.createElement('label');
        label.className = 'checkbox-item';
        label.innerHTML = `
            <input type="checkbox" value="${col}" checked data-type="numeric">
            ${col} <span style="color:#555;font-size:11px">#</span>
        `;
        list.appendChild(label);
    });

    // Columnas de texto
    state.textColumns.forEach(col => {
        const values = state.uniqueValues[col] || [];

        const wrapper = document.createElement('div');
        wrapper.style.cssText = 'background:#222;border-radius:8px;overflow:hidden;';

        const header = document.createElement('div');
        header.style.cssText = 'padding:8px 12px;cursor:pointer;display:flex;justify-content:space-between;align-items:center;font-size:13px;';
        header.innerHTML = `<span>${col} <span style="color:#555;font-size:11px">T</span></span><span class="arrow" style="color:#555;font-size:11px">▼</span>`;

        const dropdown = document.createElement('div');
        dropdown.style.cssText = 'padding:4px 8px 8px;display:none;flex-direction:column;gap:4px;';
        dropdown.dataset.col = col;

        values.forEach(val => {
            const label = document.createElement('label');
            label.className = 'checkbox-item';
            label.style.cssText = 'padding:6px 10px;font-size:12px;';
            label.innerHTML = `<input type="checkbox" value="${val}" data-col="${col}" data-type="text-filter" checked> ${val}`;
            dropdown.appendChild(label);
        });

        header.addEventListener('click', () => {
            const isOpen = dropdown.style.display === 'flex';
            dropdown.style.display = isOpen ? 'none' : 'flex';
            header.querySelector('.arrow').textContent = isOpen ? '▼' : '▲';
        });

        wrapper.appendChild(header);
        wrapper.appendChild(dropdown);
        list.appendChild(wrapper);
    });

    document.getElementById('rowStart').value = 0;
    document.getElementById('rowEnd').value   = state.totalRows;
    document.getElementById('rowEnd').max     = state.totalRows;
}

function buildPreviewTable() {
    const table = document.getElementById('previewTable');
    if (!state.previewData.length) return;

    const cols = Object.keys(state.previewData[0]);
    let html = '<thead><tr>' + cols.map(c => `<th>${c}</th>`).join('') + '</tr></thead>';
    html += '<tbody>';
    state.previewData.forEach(row => {
        html += '<tr>' + cols.map(c => `<td>${row[c]}</td>`).join('') + '</tr>';
    });
    html += '</tbody>';
    table.innerHTML = html;
}

function buildPlotlyChart() {
    const container = document.getElementById('plotlyChart');
    if (!state.numericColumns.length || !state.previewData.length) return;

    const selectedCols = [...document.querySelectorAll('#columnsList input:checked')].map(i => i.value);
    const cols = selectedCols.length ? selectedCols : [state.numericColumns[0]];

    const textCols = state.columns.filter(c => !state.numericColumns.includes(c));
    const labelCol = textCols.length ? textCols[0] : null;

    let filteredData = [...state.previewData];

    document.querySelectorAll('#columnsList input[data-type="text-filter"]').forEach(input => {
        if (!input.checked) {
            const col = input.dataset.col;
            const val = input.value;
            filteredData = filteredData.filter(r => r[col] != val);
        }
    });

    const labels = labelCol
        ? filteredData.map(r => r[labelCol])
        : filteredData.map((_, i) => `Fila ${i + 1}`);

    const layout = {
        paper_bgcolor: 'transparent',
        plot_bgcolor:  'transparent',
        font:   { color: '#aaa', size: 11 },
        margin: { t: 40, r: 10, b: 40, l: 50 },
        legend: { font: { color: '#aaa' } }
    };

    let traces = [];

    if (state.chartType === 'bar') {
        traces = cols.map(col => ({
            x: labels, y: filteredData.map(r => r[col]),
            name: col, type: 'bar'
        }));
    } else if (state.chartType === 'line') {
        traces = cols.map(col => ({
            x: labels, y: filteredData.map(r => r[col]),
            name: col, type: 'scatter', mode: 'lines+markers'
        }));
    } else if (state.chartType === 'pie') {
        const col = cols[0];
        traces = [{ labels, values: filteredData.map(r => r[col]), type: 'pie', name: col }];
    }

    Plotly.react(container, traces, layout, { displayModeBar: false });
}

// Tipo de gráfico
document.querySelectorAll('[data-type]').forEach(btn => {
    btn.addEventListener('click', () => {
        document.querySelectorAll('[data-type]').forEach(b => b.classList.remove('selected'));
        btn.classList.add('selected');
        state.chartType = btn.dataset.type;
        buildPlotlyChart();
    });
});

// Moneda
document.querySelectorAll('[data-currency]').forEach(btn => {
    btn.addEventListener('click', () => {
        console.log('moneda click:', btn.dataset.currency);
        document.querySelectorAll('[data-currency]').forEach(b => b.classList.remove('selected'));
        btn.classList.add('selected');
        state.currency = btn.dataset.currency;
    });
});

// Generar PDF
document.getElementById('generateBtn').addEventListener('click', async () => {
    showSpinner('Generando reporte PDF...');

    const selectedColumns = [...document.querySelectorAll('#columnsList input[data-type="numeric"]:checked')].map(i => i.value);

    const rowFilters = {};
    document.querySelectorAll('#columnsList input[data-type="text-filter"]').forEach(input => {
        const col = input.dataset.col;
        if (!rowFilters[col]) rowFilters[col] = [];
        if (input.checked) rowFilters[col].push(input.value);
    });

    const sections  = [...document.querySelectorAll('.sections-list input:checked')].map(i => i.value);
    const rowStart  = parseInt(document.getElementById('rowStart').value) || 0;
    const rowEnd    = parseInt(document.getElementById('rowEnd').value)   || state.totalRows;

    try {
        const res = await fetch('/generate', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                filename:   state.filename,
                columns:    selectedColumns,
                chart_type: state.chartType,
                row_range:  [rowStart, rowEnd],
                row_filters: rowFilters,
                sections:   sections,
                currency:   state.currency
            })
        });

        const data = await res.json();

        if (data.success) {
            document.getElementById('analysisText').textContent = data.analysis.summary;
            document.getElementById('downloadBtn').href = '/download/reporte.pdf';
            goToSection(3);
        } else {
            showError(data.error || 'Error al generar el reporte.');
        }
    } catch (e) {
        showError('Error al conectar con el servidor.');
    } finally {
        hideSpinner();
    }
});

// Volver
document.getElementById('backBtn').addEventListener('click', () => goToSection(1));

// Reiniciar
document.getElementById('restartBtn').addEventListener('click', () => {
    state.file     = null;
    state.filename = null;
    fileSelected.style.display = 'none';
    uploadBtn.disabled = true;
    fileInput.value = '';
    goToSection(1);
});

// Navegación
function goToSection(n) {
    document.getElementById('section-upload').style.display  = n === 1 ? 'block' : 'none';
    document.getElementById('section-filters').style.display = n === 2 ? 'block' : 'none';
    document.getElementById('section-result').style.display  = n === 3 ? 'block' : 'none';

    [1, 2, 3].forEach(i => {
        const el = document.getElementById(`step${i}`);
        el.className = 'step' + (i === n ? ' active' : i < n ? ' done' : '');
    });
}

function showSpinner(text) {
    document.getElementById('spinnerText').textContent = text;
    document.getElementById('spinner').classList.add('active');
}

function hideSpinner() {
    document.getElementById('spinner').classList.remove('active');
}

function showError(msg) {
    const toast = document.getElementById('errorToast');
    toast.textContent  = msg;
    toast.style.display = 'block';
    setTimeout(() => toast.style.display = 'none', 4000);
}