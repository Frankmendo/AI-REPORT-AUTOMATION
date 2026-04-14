import pandas as pd

def process_file(filepath):
    try:
        # Leer archivo
        if filepath.endswith('.csv'):
            df = pd.read_csv(filepath, header=None)
        else:
            df = pd.read_excel(filepath, header=None)

        # Detectar la primera fila con datos reales (no vacía)
        header_row = None
        for i in range(len(df)):
            if df.iloc[i].notna().sum() > 2:
                header_row = i
                break

        if header_row is None:
            raise Exception("No se encontró encabezado válido")

       
        df.columns = df.iloc[header_row]

        
        df = df[(header_row + 1):]

       
        df = df.reset_index(drop=True)

        df = df.dropna(axis=1, how='all')

        
        cols = pd.Series(df.columns)
        for dup in cols[cols.duplicated()].unique():
            cols[cols[cols == dup].index] = [f"{dup}_{i}" if i != 0 else dup for i in range(sum(cols == dup))]
        df.columns = cols

        print("Columnas finales:", df.columns.tolist())

        return df

    except Exception as e:
        raise Exception(f"Error al leer archivo: {str(e)}")