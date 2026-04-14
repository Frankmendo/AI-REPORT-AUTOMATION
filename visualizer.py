import os
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

def generate_charts(df, output_folder, chart_type='bar'):
    charts = []
    numeric_cols = df.select_dtypes(include='number').columns.tolist()
    text_cols = df.select_dtypes(exclude='number').columns.tolist()

    if not numeric_cols:
        return charts

    try:
        if chart_type == 'pie':
            fig, ax = plt.subplots(figsize=(6, 4))
        else:
            fig, ax = plt.subplots(figsize=(7, 3.5))

        fig.patch.set_facecolor('#ffffff')
        ax.set_facecolor('#f9f9f9')

        x_col = text_cols[0] if text_cols else None

        if x_col and len(df) > 10:
            df_plot = df.groupby(x_col)[numeric_cols].sum().reset_index()
        else:
            df_plot = df

        x_labels = df_plot[x_col].astype(str).tolist() if x_col else list(range(len(df_plot)))

        if chart_type == 'bar':
            x = range(len(x_labels))
            width = 0.8 / max(len(numeric_cols), 1)
            for i, col in enumerate(numeric_cols):
                offset = (i - len(numeric_cols)/2 + 0.5) * width
                ax.bar([xi + offset for xi in x], df_plot[col], width=width, label=col)
            ax.set_xticks(range(len(x_labels)))
            ax.set_xticklabels(x_labels, rotation=45, ha='right', fontsize=8)
            if len(numeric_cols) > 1:
                ax.legend(fontsize=8)

        elif chart_type == 'line':
            for col in numeric_cols:
                ax.plot(x_labels, df_plot[col], marker='o', markersize=3, label=col)
            ax.set_xticks(range(len(x_labels)))
            ax.set_xticklabels(x_labels, rotation=45, ha='right', fontsize=8)
            if len(numeric_cols) > 1:
                ax.legend(fontsize=8)

        elif chart_type == 'pie':
            col = numeric_cols[0]
            ax.set_facecolor('#ffffff') 
            wedges, texts, autotexts = ax.pie(
                df_plot[col],
                labels=None,
                autopct='%1.1f%%',
                pctdistance=0.75,
                startangle=90,
                radius=0.85
            )
            for t in autotexts:
                t.set_fontsize(7)

            fig.legend(
                wedges,
                x_labels,
                loc='center right',
                fontsize=7,
                frameon=False,
                bbox_to_anchor=(1.0, 0.5)
            )

        ax.set_title('Análisis de datos', fontsize=11, pad=10)
        plt.tight_layout()

        filepath = os.path.join(output_folder, 'chart_main.png')
        plt.savefig(filepath, dpi=100, bbox_inches='tight')
        plt.close(fig)
        charts.append(filepath)

    except Exception as e:
        print("Error generando gráficos:", str(e))
        plt.close('all')

    return charts