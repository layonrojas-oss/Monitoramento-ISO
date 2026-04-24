from datetime import datetime

MESES_PT = {
    1: "janeiro", 2: "fevereiro", 3: "março", 4: "abril",
    5: "maio", 6: "junho", 7: "julho", 8: "agosto",
    9: "setembro", 10: "outubro", 11: "novembro", 12: "dezembro"
}
MESES_ABREV = {
    1: "jan", 2: "fev", 3: "mar", 4: "abr",
    5: "mai", 6: "jun", 7: "jul", 8: "ago",
    9: "set", 10: "out", 11: "nov", 12: "dez"
}

def formatar_moeda(valor):
    return f"R$ {valor:,.0f}".replace(",", ".")

def categorizar_faixa(cluster_str):
    c = str(cluster_str).lower()
    if '180k' in c and 'até' in c or 'sem inform' in c or c == 'nan': return 'Micro'
    elif '180k' in c and '720k' in c: return 'Small'
    elif '720k' in c and '4,8m' in c: return 'Medium'
    elif '4,8m' in c and '35m' in c: return 'Enterprise'
    elif '35m' in c and 'acima' in c: return 'Key Account'
    return 'Small'

def calcular_var_pct(atual, anterior):
    if anterior and anterior > 0:
        return ((atual - anterior) / anterior) * 100
    if atual > 0 and (not anterior or anterior == 0):
        return 100.0
    return 0.0

def calcular_atingimento(real, meta):
    if meta > 0:
        return ((real / meta) - 1) * 100
    return 0.0

def str_to_float_pct(val_str):
    try:
        return float(str(val_str).replace('%', '').replace(',', '.'))
    except:
        return 0.0

def format_mes_yy(mes_str):
    try:
        dt = datetime.strptime(mes_str, "%Y-%m")
        return f"{MESES_ABREV[dt.month]}/{dt.strftime('%y')}"
    except:
        return mes_str
