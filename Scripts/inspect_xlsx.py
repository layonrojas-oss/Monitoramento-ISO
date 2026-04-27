import pandas as pd
import sys

files = [
    'dados_processados/analise_jornada_sc_iso_2026_04_27.xlsx',
    'dados_processados/pace_comercial_outbound_2026_04_27.xlsx',
]
for f in files:
    print('\nFILE:', f)
    try:
        x = pd.ExcelFile(f, engine='openpyxl')
        print('  sheets:', x.sheet_names)
        for s in x.sheet_names:
            df = pd.read_excel(x, sheet_name=s)
            print('  sheet:', s)
            print('    cols:', df.columns.tolist())
            print('    rows:', min(5, len(df)))
            if len(df)>0:
                print('    head:', df.head(1).to_dict(orient='records'))
    except Exception as e:
        print('  ERRO:', e)
        sys.exit(1)
print('\nDone')
