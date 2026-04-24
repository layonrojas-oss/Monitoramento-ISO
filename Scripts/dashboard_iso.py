import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import os
import glob
from datetime import datetime
from dateutil.relativedelta import relativedelta

st.set_page_config(page_title="Dashboard ISO | Operações", layout="wide")

st.markdown("""
    <style>
    .metric-row { font-size: 14px; font-weight: bold; }
    div[data-testid="metric-container"] {
        background-color: #f8f9fa; border: 1px solid #e9ecef; padding: 5%; border-radius: 5px;
    }
    .stDataFrame table th {
        text-align: center !important;
        background-color: #003366 !important;
        color: white !important;
    }
    
    /* ESTILOS CUSTOMIZADOS PARA OS CARDS DO FUNIL E2E */
    .funnel-card {
        background-color: #ffffff;
        border-radius: 12px;
        padding: 20px;
        box-shadow: 0 4px 10px rgba(0,0,0,0.08);
        height: 100%;
        display: flex;
        flex-direction: column;
    }
    .funnel-card-topo { border-top: 6px solid #003366; }
    .funnel-card-meio { border-top: 6px solid #fd7e14; }
    .funnel-card-fundo { border-top: 6px solid #198754; }
    
    .funnel-title { margin: 0 0 5px 0; font-size: 18px; font-weight: bold; }
    .funnel-subtitle { color: #6c757d; font-size: 13px; margin: 0 0 15px 0; }
    
    .funnel-highlight {
        padding: 12px;
        border-radius: 8px;
        text-align: center;
        margin-top: auto;
    }
    .funnel-highlight-title { font-size: 12px; font-weight: bold; margin-bottom: 5px; letter-spacing: 0.5px;}
    .funnel-highlight-value { font-size: 28px; font-weight: bold; }
    
    .e2e-table { width: 100%; border-collapse: collapse; font-size: 14px; margin-bottom: 15px;}
    .e2e-table td { padding: 8px 0; border-bottom: 1px solid #f1f3f5; }
    .e2e-table tr:last-child td { border-bottom: none; }
    .e2e-label { color: #495057; }
    .e2e-val { text-align: right; font-weight: 600; color: #212529; }
    .e2e-sub { font-size: 11px; font-weight: normal; margin-left: 5px; }
    </style>
""", unsafe_allow_html=True)

# --- Dicionários
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

# --- 1. FUNÇÕES AUXILIARES ---
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

# --- 2. CARREGAMENTO ---
@st.cache_data
def load_data():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    proc_dir = os.path.join(base_dir, "dados_processados")
    
    arquivos_pace = sorted(glob.glob(os.path.join(proc_dir, "pace_comercial_outbound_*.xlsx")))
    arquivos_esteira = sorted(glob.glob(os.path.join(proc_dir, "analise_gaps_esteira_*.xlsx")))
    arquivos_crm = sorted(glob.glob(os.path.join(proc_dir, "*_Relatorio_Funil_IS.xlsx")))
    
    if not arquivos_pace or not arquivos_esteira:
        st.error("Arquivos de dados processados não encontrados.")
        st.stop()
        
    df_pace_diario = pd.read_excel(arquivos_pace[-1], sheet_name="Base Completa")
    df_detalhado = pd.read_excel(arquivos_esteira[-1], sheet_name="Base Detalhada Funil")
    df_cluster = pd.read_excel(arquivos_esteira[-1], sheet_name="Análise por Cluster")
    
    if arquivos_crm:
        df_topo = pd.read_excel(arquivos_crm[-1], sheet_name="Topo do Funil")
    else:
        df_topo = pd.DataFrame()
    
    df_cluster["faixa_faturamento"] = df_cluster["cluster_faturamento"].apply(categorizar_faixa)
                
    return {"pace_diario": df_pace_diario, "detalhado": df_detalhado, "cluster": df_cluster, "topo": df_topo}

data = load_data()

# --- 3. SIDEBAR: FILTROS ---
with st.sidebar:
    st.header("⚙️ Filtros Globais")
    
    meses_disp = sorted(data["pace_diario"]["mes_referencia"].unique(), reverse=True)
    f_mes = st.selectbox("Mês de Referência", meses_disp)
    
    st.divider()
    st.subheader("Filtro de Pace (MTD)")
    max_du = int(data["pace_diario"]["dia_util"].max()) if "dia_util" in data["pace_diario"].columns else 22
    if max_du == 0: max_du = 22
    f_dia_util = st.slider("Dia Útil MTD (Corte de Análise)", 1, max_du, max_du)
    
    st.divider()
    st.subheader("Filtros de Segmentação")
    f_tamanho = st.selectbox("Tamanho do Lead", ["Todos", "Micro", "Small", "Medium", "Enterprise", "Key Account"])
    
    opt_iso = ["Todos"] + list(data["detalhado"]["carteira_iso"].unique())
    f_iso = st.selectbox("Carteira ISO", opt_iso)
    
    opt_2030 = ["Todos"] + list(data["detalhado"]["plano_2030"].unique())
    f_2030 = st.selectbox("Plano 2030", opt_2030)
    
    opt_ipp = ["Todos"] + sorted([str(x) for x in data["detalhado"]["ipp"].dropna().unique()])
    f_ipp = st.multiselect("IPP", opt_ipp, default="Todos")
    
    st.divider()
    st.subheader("Filtros de Operação")
    todos_colabs = set(data["detalhado"]["usuario_ec"].dropna()) | set(data["detalhado"]["usuario_sdr"].dropna()) | set(data["detalhado"]["usuario_ev"].dropna())
    f_colab = st.selectbox("Colaborador (EC/SDR/EV)", ["Todos"] + sorted(list(todos_colabs)))

# --- 4. LÓGICA DE FILTRAGEM ---
def apply_mtd_pace(df_diario, cut_day):
    df_cortado = df_diario[df_diario["dia_util"] <= cut_day].copy()
    grp = df_cortado.groupby("mes_referencia").sum(numeric_only=True).reset_index()
    if "nmrr_sem_bpo_realizado" in grp.columns and "nmrr_bpo_realizado" in grp.columns:
        grp["nmrr_total_realizado"] = grp["nmrr_sem_bpo_realizado"] + grp["nmrr_bpo_realizado"]
        grp["nmrr_total_meta"] = grp.get("nmrr_sem_bpo_meta", 0) + grp.get("nmrr_bpo_meta", 0)
    return grp

def apply_mtd_cluster(df_cluster, cut_day):
    if "dia_util" not in df_cluster.columns: return df_cluster.copy()
    df_c = df_cluster[df_cluster["dia_util"] <= cut_day].copy()
    cols = [c for c in ["mes_referencia", "cluster_faturamento", "faixa_faturamento"] if c in df_cluster.columns]
    return df_c.groupby(cols).sum(numeric_only=True).reset_index()

def apply_filters_detailed(df):
    temp_df = df[df["mes_referencia"] <= f_mes].copy()
    
    if "origem_macro" in temp_df.columns:
        temp_df = temp_df[temp_df["origem_macro"] == "Outbound"]
        
    if f_iso != "Todos": temp_df = temp_df[temp_df["carteira_iso"] == f_iso]
    if f_2030 != "Todos": temp_df = temp_df[temp_df["plano_2030"] == f_2030]
    if "Todos" not in f_ipp and len(f_ipp) > 0: temp_df = temp_df[temp_df["ipp"].astype(str).isin(f_ipp)]
        
    if f_colab != "Todos":
        temp_df = temp_df[(temp_df["usuario_ec"] == f_colab) | (temp_df["usuario_sdr"] == f_colab) | (temp_df["usuario_ev"] == f_colab)]
        
    if f_tamanho != "Todos":
        temp_df["faixa"] = temp_df["cluster_faturamento"].apply(categorizar_faixa)
        temp_df = temp_df[temp_df["faixa"] == f_tamanho]
        
    return temp_df

# Aplicar consolidações
df_pace_full = apply_mtd_pace(data["pace_diario"], f_dia_util)
df_p_atual = df_pace_full[df_pace_full["mes_referencia"] == f_mes]

df_c_raw = apply_filters_detailed(data["cluster"]) if "cluster_faturamento" in data["cluster"].columns else data["cluster"]
df_c_hist = apply_mtd_cluster(df_c_raw, f_dia_util)

mes_atual_dt = datetime.strptime(f_mes, "%Y-%m")
mes_ant_dt = mes_atual_dt - relativedelta(months=1)
label_var = f"Var % {MESES_ABREV[mes_atual_dt.month]} x {MESES_ABREV[mes_ant_dt.month]}"

# --- 5. RENDERIZAÇÃO: PAINÉIS ---
st.title("🚀 Reportologia Inside Sales Outbound")
tab1, tab2, tab3 = st.tabs([
    "🎯 Visão End-to-End & Pace", 
    "🔍 Análise de Gaps (Linha a Linha)", 
    "📊 Funil Visual"
])

# =========================================================================
# TAB 1: VISÃO GERAL (END-TO-END) + PACE
# =========================================================================
with tab1:
    
    st.markdown(f"<h3 style='margin-bottom: 5px;'>Visão End-to-End | {MESES_PT[mes_atual_dt.month].capitalize()}</h3>", unsafe_allow_html=True)
    st.markdown("<p style='color: #6c757d; margin-bottom: 20px;'>Integração do engajamento de Carteira (CRM) com a performance comercial (Pace).</p>", unsafe_allow_html=True)
    
    # --- PREPARAÇÃO DE DADOS ---
    df_topo_f = data["topo"].copy()
    if not df_topo_f.empty and f_colab != "Todos":
        if "Colaborador" in df_topo_f.columns:
            df_topo_f = df_topo_f[df_topo_f["Colaborador"] == f_colab]
            
    carteira_atual = df_topo_f['Carteira_Atual'].sum() if not df_topo_f.empty else 0
    cart_reuniao = df_topo_f['Carteira_com_Reuniao'].sum() if not df_topo_f.empty else 0
    pct_cart_reuniao = (cart_reuniao / carteira_atual) if carteira_atual > 0 else 0
    qtd_reunioes = df_topo_f['Quantidade_Reunioes'].sum() if not df_topo_f.empty else 0
    cart_indicando = df_topo_f['Carteira_Indicando'].sum() if not df_topo_f.empty else 0
    pct_cart_indicando = (cart_indicando / carteira_atual) if carteira_atual > 0 else 0
    cart_ativando = df_topo_f['Carteira_Ativando'].sum() if not df_topo_f.empty else 0
    pct_cart_ativando = (cart_ativando / carteira_atual) if carteira_atual > 0 else 0
    leads_criados = df_topo_f['Leads_Criados'].sum() if not df_topo_f.empty else 0
    leads_por_contador = (leads_criados / cart_indicando) if cart_indicando > 0 else 0
    
    row = df_p_atual.iloc[0] if not df_p_atual.empty else pd.Series()
    l_agendados = row.get("leads_agendados_realizado", 0)
    tx_agend = (l_agendados / leads_criados) if leads_criados > 0 else 0
    d_realizadas = row.get("demos_realizadas_realizado", 0)
    l_conquistados = row.get("leads_conquistados_realizado", 0)
    tx_conv_demos = (l_conquistados / l_agendados) if l_agendados > 0 else 0
    a_ativados = row.get("apps_ativados_realizado", 0)
    mult_cnpj = (a_ativados / l_conquistados) if l_conquistados > 0 else 0
    nmrr_sem_bpo = row.get("nmrr_sem_bpo_realizado", 0)
    nmrr_bpo = row.get("nmrr_bpo_realizado", 0)
    nmrr_total = nmrr_sem_bpo + nmrr_bpo
    tk_medio = (nmrr_total / a_ativados) if a_ativados > 0 else 0

    c_topo, c_meio, c_fundo = st.columns(3)

    # --- HTML DO TOPO SEM ESPAÇOS NA IDENTAÇÃO ---
    with c_topo:
        html_topo = f"""<div class="funnel-card funnel-card-topo">
<div class="funnel-title" style="color: #003366;">🏔️ TOPO</div>
<div class="funnel-subtitle">Engajamento de Carteira</div>

<div style="background: #f4f6f9; padding: 12px; border-radius: 8px; margin-bottom: 15px; display: flex; justify-content: space-between; align-items: center;">
<span style="color: #495057; font-weight: bold; font-size: 13px;">CARTEIRA ATUAL</span>
<span style="font-size: 20px; font-weight: 800; color: #003366;">{int(carteira_atual)}</span>
</div>

<div style="margin-bottom: 15px;">
<div style="display: flex; justify-content: space-between; padding: 8px 0; border-bottom: 1px solid #f1f3f5; font-size: 14px;">
<span style="color: #495057;">💼 Com Reunião</span>
<span style="font-weight: 600; color: #212529;">{int(cart_reuniao)} <span style="font-size: 11px; font-weight: normal; color: #003366; margin-left: 4px;">({pct_cart_reuniao:.0%})</span></span>
</div>
<div style="display: flex; justify-content: space-between; padding: 8px 0; border-bottom: 1px solid #f1f3f5; font-size: 14px;">
<span style="color: #495057;">🤝 Reuniões Feitas</span>
<span style="font-weight: 600; color: #212529;">{int(qtd_reunioes)}</span>
</div>
<div style="display: flex; justify-content: space-between; padding: 8px 0; border-bottom: 1px solid #f1f3f5; font-size: 14px;">
<span style="color: #495057;">📣 Indicando</span>
<span style="font-weight: 600; color: #212529;">{int(cart_indicando)} <span style="font-size: 11px; font-weight: normal; color: #003366; margin-left: 4px;">({pct_cart_indicando:.0%})</span></span>
</div>
<div style="display: flex; justify-content: space-between; padding: 8px 0; border-bottom: 1px solid #f1f3f5; font-size: 14px;">
<span style="color: #495057;">🚀 Ativando</span>
<span style="font-weight: 600; color: #212529;">{int(cart_ativando)} <span style="font-size: 11px; font-weight: normal; color: #003366; margin-left: 4px;">({pct_cart_ativando:.0%})</span></span>
</div>
<div style="display: flex; justify-content: space-between; padding: 8px 0; font-size: 14px;">
<span style="color: #495057;">📈 Leads / Contador</span>
<span style="font-weight: 600; color: #212529;">{leads_por_contador:.1f}</span>
</div>
</div>

<div class="funnel-highlight" style="background: #e3f2fd; border: 1px solid #b6effb;">
<div class="funnel-highlight-title" style="color: #0056b3;">LEADS CRIADOS</div>
<div class="funnel-highlight-value" style="color: #003366;">{int(leads_criados)}</div>
</div>
</div>"""
        st.markdown(html_topo, unsafe_allow_html=True)


    # --- HTML DO MEIO SEM ESPAÇOS NA IDENTAÇÃO ---
    with c_meio:
        html_meio = f"""<div class="funnel-card funnel-card-meio">
<div class="funnel-title" style="color: #fd7e14;">🔄 MEIO</div>
<div class="funnel-subtitle">Qualificação (SDR)</div>

<div style="background: #fdf5eb; padding: 12px; border-radius: 8px; margin-bottom: 25px; text-align: center; border: 1px solid #f9dec5;">
<div style="color: #9c4f00; font-size: 12px; font-weight: bold; margin-bottom: 5px;">LEADS AGENDADOS</div>
<div style="font-size: 28px; font-weight: 800; color: #fd7e14;">{int(l_agendados)}</div>
</div>

<div style="text-align: center; margin: 30px 0;">
<div style="font-size: 13px; color: #6c757d; font-weight: bold; letter-spacing: 0.5px;">TAXA DE AGENDAMENTO</div>
<div style="font-size: 32px; font-weight: 900; color: #fd7e14; margin: 5px 0;">{tx_agend:.0%}</div>
<div style="font-size: 11px; color: #adb5bd;">(Leads Criados → Agendados)</div>
</div>

<div class="funnel-highlight" style="background: #fff3cd; border: 1px solid #ffe69c;">
<div class="funnel-highlight-title" style="color: #997404;">DEMOS REALIZADAS</div>
<div class="funnel-highlight-value" style="color: #fd7e14;">{int(d_realizadas)}</div>
</div>
</div>"""
        st.markdown(html_meio, unsafe_allow_html=True)


    # --- HTML DO FUNDO SEM ESPAÇOS NA IDENTAÇÃO ---
    with c_fundo:
        html_fundo = f"""<div class="funnel-card funnel-card-fundo">
<div class="funnel-title" style="color: #198754;">💰 FUNDO</div>
<div class="funnel-subtitle">Fechamento (EV)</div>

<div style="display: flex; gap: 10px; margin-bottom: 15px;">
<div style="flex: 1; background: #f4f6f9; padding: 10px; border-radius: 8px; text-align: center;">
<div style="color: #6c757d; font-size: 11px; font-weight: bold;">VENDAS</div>
<div style="font-size: 22px; font-weight: 800; color: #212529;">{int(l_conquistados)}</div>
</div>
<div style="flex: 1; background: #f4f6f9; padding: 10px; border-radius: 8px; text-align: center;">
<div style="color: #6c757d; font-size: 11px; font-weight: bold;">TX. CONVERSÃO</div>
<div style="font-size: 22px; font-weight: 800; color: #198754;">{tx_conv_demos:.0%}</div>
</div>
</div>

<div style="margin-bottom: 15px;">
<div style="display: flex; justify-content: space-between; padding: 8px 0; border-bottom: 1px solid #f1f3f5; font-size: 14px;">
<span style="color: #495057;">⚙️ Apps Ativados</span>
<span style="font-weight: 600; color: #212529;">{int(a_ativados)}</span>
</div>
<div style="display: flex; justify-content: space-between; padding: 8px 0; border-bottom: 1px solid #f1f3f5; font-size: 14px;">
<span style="color: #495057;">🏢 Múltiplos CNPJs</span>
<span style="font-weight: 600; color: #212529;">{mult_cnpj:.2f}</span>
</div>
<div style="display: flex; justify-content: space-between; padding: 8px 0; border-bottom: 1px solid #f1f3f5; font-size: 14px;">
<span style="color: #495057;">🏷️ Ticket Médio</span>
<span style="font-weight: 600; color: #198754;">{formatar_moeda(tk_medio)}</span>
</div>
<div style="display: flex; justify-content: space-between; padding: 8px 0; font-size: 14px;">
<span style="color: #495057;">📦 BPO / FULL</span>
<span style="font-weight: 600; color: #212529; font-size: 12px;">{formatar_moeda(nmrr_bpo)} <span style="font-weight:normal; color:#ccc;">/</span> {formatar_moeda(nmrr_sem_bpo)}</span>
</div>
</div>

<div class="funnel-highlight" style="background: #d1e7dd; border: 1px solid #a3cfbb;">
<div class="funnel-highlight-title" style="color: #0f5132;">NMRR TOTAL</div>
<div class="funnel-highlight-value" style="color: #198754;">{formatar_moeda(nmrr_total)}</div>
</div>
</div>"""
        st.markdown(html_fundo, unsafe_allow_html=True)

    
    st.divider()
    
    # ---------------------------------------------------------
    # BLOCO ANTIGO: PACE METAS VS REALIZADO
    # ---------------------------------------------------------
    st.subheader("🏁 Monitoramento Diário (Pace Metas vs Realizado)")
    
    if not df_p_atual.empty:
        m_recebidos = row.get("leads_agendados_meta", 0)
        m_demos = row.get("demos_realizadas_meta", 0)
        m_conq = row.get("leads_conquistados_meta", 0)
        m_apps = row.get("apps_ativados_meta", 0)
        nmrr_padrao_meta = row.get("nmrr_sem_bpo_meta", 0)
        nmrr_bpo_meta = row.get("nmrr_bpo_meta", 0)
        nmrr_total_meta = row.get("nmrr_total_meta", 0)
        
        tx_conv_meta = (m_conq / m_demos) if m_demos > 0 else 0
        ind_mult_meta = (m_apps / m_conq) if m_conq > 0 else 0
        ticket_meta = (nmrr_total_meta / m_apps) if m_apps > 0 else 0

        tabela_pace = pd.DataFrame({
            "Métrica": [
                "Leads Recebidos (Agendados)", "Demos realizadas", "Leads conquistados", 
                "Tx. Conv. Demos", "Apps Ativados", "Indice de Múltiplo", 
                "Ticket Médio", "NMRR (Sem BPO)", "NMRR BPO", "NMRR Total"
            ],
            "Realizado": [
                f"{int(l_agendados)}", f"{int(d_realizadas)}", f"{int(l_conquistados)}",
                f"{((l_conquistados/d_realizadas)*100 if d_realizadas > 0 else 0):.0f}%", f"{int(a_ativados)}", f"{mult_cnpj:.2f}".replace(".", ","),
                formatar_moeda(tk_medio), formatar_moeda(nmrr_sem_bpo), 
                formatar_moeda(nmrr_bpo), formatar_moeda(nmrr_total)
            ],
            "Meta": [
                f"{int(m_recebidos)}", f"{int(m_demos)}", f"{int(m_conq)}",
                f"{(tx_conv_meta*100):.0f}%", f"{int(m_apps)}", f"{ind_mult_meta:.2f}".replace(".", ","),
                formatar_moeda(ticket_meta), formatar_moeda(nmrr_padrao_meta),
                formatar_moeda(nmrr_bpo_meta), formatar_moeda(nmrr_total_meta)
            ],
            "Ating. %": [
                f"{calcular_atingimento(l_agendados, m_recebidos):.0f}%",
                f"{calcular_atingimento(d_realizadas, m_demos):.0f}%",
                f"{calcular_atingimento(l_conquistados, m_conq):.0f}%",
                f"{calcular_atingimento(((l_conquistados/d_realizadas) if d_realizadas > 0 else 0), tx_conv_meta):.0f}%",
                f"{calcular_atingimento(a_ativados, m_apps):.0f}%",
                f"{calcular_atingimento(mult_cnpj, ind_mult_meta):.0f}%",
                f"{calcular_atingimento(tk_medio, ticket_meta):.0f}%",
                f"{calcular_atingimento(nmrr_sem_bpo, nmrr_padrao_meta):.0f}%",
                f"{calcular_atingimento(nmrr_bpo, nmrr_bpo_meta):.0f}%",
                f"{calcular_atingimento(nmrr_total, nmrr_total_meta):.0f}%"
            ]
        })

        def style_atingimento(val):
            try:
                num = float(val.replace('%', ''))
                if num < 0: return 'background-color: #f8d7da; color: #721c24; text-align: center;'
                else: return 'background-color: #d4edda; color: #155724; text-align: center;'
            except:
                return ''

        c1, c2, c3 = st.columns([1, 6, 1])
        with c2:
            st.dataframe(
                tabela_pace.style.map(style_atingimento, subset=['Ating. %'])
                                 .set_properties(**{'text-align': 'center'}, subset=['Realizado', 'Meta']),
                width="stretch", hide_index=True
            )
        
        # =========================================================
        # NOVO BLOCO: PERFORMANCE HISTÓRICA MENSAL (GRADIENTE)
        # =========================================================
        st.divider()
        
        def format_mes_yy(mes_str):
            try:
                dt = datetime.strptime(mes_str, "%Y-%m")
                return f"{MESES_ABREV[dt.month]}/{dt.strftime('%y')}"
            except:
                return mes_str

        # Obter os últimos 7 meses disponíveis (Mês atual + 6 meses anteriores)
        todos_meses = sorted(df_pace_full["mes_referencia"].unique())
        try:
            idx_mes = todos_meses.index(f_mes)
        except ValueError:
            idx_mes = -1

        if idx_mes >= 0:
            inicio_idx = max(0, idx_mes - 6)
            meses_selecionados = todos_meses[inicio_idx : idx_mes + 1]
        else:
            meses_selecionados = [f_mes]

        # Resgatar valores reais
        dict_valores = {}
        for m in meses_selecionados:
            val = df_pace_full[df_pace_full["mes_referencia"] == m]["nmrr_total_realizado"].sum()
            dict_valores[m] = val

        val_atual = dict_valores.get(f_mes, 0)
        mes_ant = todos_meses[idx_mes - 1] if idx_mes > 0 else None
        val_ant = dict_valores.get(mes_ant, 0) if mes_ant else 0

        meses_6m = todos_meses[max(0, idx_mes - 6) : idx_mes] if idx_mes > 0 else []
        val_6m_avg = np.mean([dict_valores.get(x, 0) for x in meses_6m]) if len(meses_6m) > 0 else 0

        var_mm = (val_atual / val_ant - 1) if val_ant > 0 else (1 if val_atual > 0 else 0)
        var_6m = (val_atual / val_6m_avg - 1) if val_6m_avg > 0 else (1 if val_atual > 0 else 0)

        col_nome_atual = format_mes_yy(f_mes)
        col_nome_ant = format_mes_yy(mes_ant) if mes_ant else "Mês Ant."

        nome_col_varmm = f"{col_nome_atual.split('/')[0]} x {col_nome_ant.split('/')[0]}"
        nome_col_var6m = f"{col_nome_atual.split('/')[0]} x últimos 6 meses"

        vals_only = [dict_valores[m] for m in meses_selecionados]
        min_v = min(vals_only) if vals_only else 0
        max_v = max(vals_only) if vals_only else 0

        # Lógica matemática do mapa de calor (RdYlGn - Vermelho, Amarelo e Verde)
        def get_color_gradient(val, min_val, max_val):
            if max_val == min_val: return "#ffeb84"
            norm = (val - min_val) / (max_val - min_val)
            if norm < 0.5:
                pct = norm * 2
                r = int(248 + (255 - 248) * pct)
                g = int(105 + (235 - 105) * pct)
                b = int(107 + (132 - 107) * pct)
            else:
                pct = (norm - 0.5) * 2
                r = int(255 + (99 - 255) * pct)
                g = int(235 + (190 - 235) * pct)
                b = int(132 + (123 - 132) * pct)
            return f"rgb({r}, {g}, {b})"

        html_th_meses = ""
        html_td_meses = ""
        for m in meses_selecionados:
            c_name = format_mes_yy(m)
            v = dict_valores[m]
            bg_color = get_color_gradient(v, min_v, max_v)
            html_th_meses += f'<th style="padding: 6px 12px; border: 1px solid #000; text-align: center;">{c_name}</th>\n'
            html_td_meses += f'<td style="padding: 6px 12px; border: 1px solid #000; text-align: center; background-color: {bg_color}; color: #000;">{formatar_moeda(v)}</td>\n'

        bg_varmm = "#ffffff" if var_mm == 0 else ("#63be7b" if var_mm > 0 else "#f8696b")
        bg_var6m = "#ffffff" if var_6m == 0 else ("#63be7b" if var_6m > 0 else "#f8696b")

        html_hist = f"""<div style="margin-bottom: 20px; font-family: sans-serif;">
<div style="background-color: #ffc107; padding: 4px 15px; display: inline-block; font-weight: bold; color: #000; border-top-left-radius: 4px; border-top-right-radius: 4px; font-size: 15px;">
Inside Sales
</div>
<table style="width: 100%; border-collapse: collapse; text-align: center; border: 1px solid #000;">
<thead>
<tr style="background-color: #003366; color: #fff; font-size: 14px;">
<th style="padding: 6px 12px; text-align: left; border: 1px solid #000; font-weight: normal;">NMRR</th>
{html_th_meses}
<th style="padding: 6px 12px; border: 1px solid #000; border-left: 4px solid #fff; text-align: center;">{nome_col_varmm}</th>
<th style="padding: 6px 12px; border: 1px solid #000; border-left: 4px solid #fff; text-align: center;">{nome_col_var6m}</th>
</tr>
</thead>
<tbody>
<tr>
<td style="padding: 6px 12px; text-align: left; border: 1px solid #000; background-color: #fff; color: #000;">Outbound</td>
{html_td_meses}
<td style="padding: 6px 12px; border: 1px solid #000; border-left: 4px solid #fff; background-color: {bg_varmm}; color: #000; text-align: center;">{var_mm:.0%}</td>
<td style="padding: 6px 12px; border: 1px solid #000; border-left: 4px solid #fff; background-color: {bg_var6m}; color: #000; text-align: center;">{var_6m:.0%}</td>
</tr>
</tbody>
</table>
</div>"""
        st.markdown(html_hist, unsafe_allow_html=True)
            
        # seção de faixa faturamento
        st.divider()
        st.subheader("Performance por Faixa de Faturamento")
        meses_4 = sorted(df_pace_full[df_pace_full["mes_referencia"] <= f_mes]["mes_referencia"].unique())[-4:]
        df_c_4m = df_c_hist[df_c_hist["mes_referencia"].isin(meses_4)]
        
        def render_cluster_table(nome_cluster, df_dados):
            st.markdown(f"<h5 style='background-color: #e69138; padding: 5px; color: white; display: inline-block; border-radius: 3px; margin-bottom: 0px;'>{nome_cluster}</h5>", unsafe_allow_html=True)
            grp = df_dados.groupby("mes_referencia").sum(numeric_only=True).reset_index()
            tabela_linhas = []
            raw_data = [] 
            
            for m in meses_4:
                row_m = grp[grp["mes_referencia"] == m]
                dt_m = datetime.strptime(m, "%Y-%m")
                nome_mes = MESES_PT[dt_m.month]
                if not row_m.empty:
                    d = row_m.iloc[0]
                    ag = int(d.get("total_leads", 0))
                    dm = int(d.get("demos_realizadas", 0))
                    cq = int(d.get("vendas_fechadas", 0))
                    tx = (cq / dm * 100) if dm > 0 else 0
                    app = int(d.get("vendas_fechadas", 0))
                    nm = d.get("nmrr_total", 0)
                    tk = (nm / cq) if cq > 0 else 0
                else:
                    ag, dm, cq, tx, app, nm, tk = 0, 0, 0, 0, 0, 0, 0
                
                raw_data.append({"ag": ag, "dm": dm, "cq": cq, "tx": tx, "app": app, "nm": nm, "tk": tk})
                tabela_linhas.append({
                    "Mês": nome_mes, "Agendamentos": str(ag), "Demos": str(dm),
                    "Conquistas": str(cq), "Tx. Conv. Demos": f"{tx:.1f}%",
                    "Apps": str(app), "NMRR": formatar_moeda(nm), "Ticket": formatar_moeda(tk)
                })
            
            df_tb = pd.DataFrame(tabela_linhas)
            if len(raw_data) >= 2:
                at = raw_data[-1]
                an = raw_data[-2]
                linha_var = {
                    "Mês": label_var,
                    "Agendamentos": f"{calcular_var_pct(at['ag'], an['ag']):.0f}%",
                    "Demos": f"{calcular_var_pct(at['dm'], an['dm']):.0f}%",
                    "Conquistas": f"{calcular_var_pct(at['cq'], an['cq']):.0f}%",
                    "Tx. Conv. Demos": f"{(at['tx'] - an['tx']):.1f}%",
                    "Apps": f"{calcular_var_pct(at['app'], an['app']):.0f}%",
                    "NMRR": f"{calcular_var_pct(at['nm'], an['nm']):.0f}%",
                    "Ticket": f"{calcular_var_pct(at['tk'], an['tk']):.0f}%"
                }
                df_tb = pd.concat([df_tb, pd.DataFrame([linha_var])], ignore_index=True)

            def style_cluster_var(row):
                styles = [''] * len(row)
                if row["Mês"] == label_var:
                    for i, col in enumerate(df_tb.columns):
                        if col == "Mês":
                            styles[i] = 'background-color: #f3f3f3; font-weight: bold;'
                        else:
                            val = str_to_float_pct(row[col])
                            if val < -10: styles[i] = 'background-color: #f4cccc; color: #cc0000; text-align: center;'
                            elif val < 0: styles[i] = 'background-color: #fff2cc; color: #b45f06; text-align: center;'
                            else: styles[i] = 'background-color: #d9ead3; color: #274e13; text-align: center;'
                else:
                    for i, col in enumerate(df_tb.columns):
                        if col != "Mês": styles[i] = 'text-align: center;'
                return styles
            
            st.dataframe(df_tb.style.apply(style_cluster_var, axis=1), width="stretch", hide_index=True)

        for fx in ["Micro", "Small", "Medium", "Enterprise", "Key Account"]:
            df_fx = df_c_4m[df_c_4m["faixa_faturamento"] == fx]
            render_cluster_table(fx, df_fx)

# =========================================================================
# TAB 2: MONITORAMENTO DE GAPS (Linhas)
# =========================================================================
with tab2:
    st.header(f"Governança Operacional - Monitoramento de Gaps ({f_mes})")
    
    df_det_mtd = data["detalhado"].copy()
    
    cut = f_dia_util
    if "dia_util_criacao" in df_det_mtd.columns:
        df_det_mtd.loc[df_det_mtd["dia_util_criacao"] > cut, "leads_criados"] = 0
        
    if "dia_util_demo" in df_det_mtd.columns:
        df_det_mtd.loc[df_det_mtd["dia_util_demo"] > cut, ["demo_agendada", "demo_realizada"]] = 0
        
    if "dia_util_ativacao" in df_det_mtd.columns:
        df_det_mtd.loc[df_det_mtd["dia_util_ativacao"] > cut, ["leads_conquistados", "apps_ativados", "nmrr_gerado"]] = 0
        if "apps_erp" in df_det_mtd.columns:
            df_det_mtd.loc[df_det_mtd["dia_util_ativacao"] > cut, ["apps_erp", "apps_bpo", "nmrr_erp", "nmrr_bpo"]] = 0

    df_det_f = apply_filters_detailed(df_det_mtd)
    df_det_mes = df_det_f[df_det_f["mes_referencia"] == f_mes]

    leads_c = df_det_mes["leads_criados"].sum()
    agend = df_det_mes["demo_agendada"].sum()
    real = df_det_mes["demo_realizada"].sum()
    vendas = df_det_mes["leads_conquistados"].sum()

    st.markdown("##### Performance do Fluxo no Mês")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Leads Recebidos", int(leads_c))
    c2.metric("Demos Agendadas", int(agend))
    c3.metric("Demos Realizadas", int(real))
    c4.metric("Vendas Fechadas", int(vendas))
    
    st.divider()
    st.subheader("🔍 Detalhamento Linha a Linha (Análise de Gargalos)")
    
    filtro_gap = st.radio("Selecione a Visão Estratégica de Funil:", [
        "Todos os Leads",
        "🛑 Gargalo SDR (Leads assumidos sem Demo Agendada)",
        "🛑 Gargalo EV (Demos agendadas que não foram Realizadas)",
        "🛑 Gargalo de Fechamento (Demos Realizadas que não viraram Venda)",
        "✅ Sucesso (Vendas Conquistadas)"
    ], horizontal=True)

    if filtro_gap == "🛑 Gargalo SDR (Leads assumidos sem Demo Agendada)":
        df_view = df_det_mes[(df_det_mes["leads_criados"] > 0) & (df_det_mes["demo_agendada"] == 0)]
    elif filtro_gap == "🛑 Gargalo EV (Demos agendadas que não foram Realizadas)":
        df_view = df_det_mes[(df_det_mes["demo_agendada"] > 0) & (df_det_mes["demo_realizada"] == 0)]
    elif filtro_gap == "🛑 Gargalo de Fechamento (Demos Realizadas que não viraram Venda)":
        df_view = df_det_mes[(df_det_mes["demo_realizada"] > 0) & (df_det_mes["leads_conquistados"] == 0)]
    elif filtro_gap == "✅ Sucesso (Vendas Conquistadas)":
        df_view = df_det_mes[df_det_mes["leads_conquistados"] > 0]
    else:
        df_view = df_det_mes

    cols_display = [
        "lead_id", "cnpj", "usuario_ec", "usuario_sdr", "usuario_ev",
        "status", "fase", "cluster_faturamento", 
        "leads_criados", "demo_agendada", "demo_realizada", "leads_conquistados", "nmrr_gerado"
    ]
    cols_display = [c for c in cols_display if c in df_view.columns]

    if not df_view.empty:
        st.dataframe(df_view[cols_display], width="stretch", hide_index=True)
    else:
        st.success("Não foram encontrados leads com essa característica no período!")

# =========================================================================
# TAB 3: FUNIL VISUAL
# =========================================================================
with tab3:
    st.header("📊 Funil Visual - Meio e Fundo de Funil")
    st.markdown(f"Análise visual das taxas de conversão operacionais para o mês de **{f_mes}**.")
    
    val_criados = df_det_mes["leads_criados"].sum()
    val_agend = df_det_mes["demo_agendada"].sum()
    val_reais = df_det_mes["demo_realizada"].sum()
    val_vendas = df_det_mes["leads_conquistados"].sum()

    tx_agendamento = (val_agend / val_criados * 100) if val_criados > 0 else 0
    tx_realizacao = (val_reais / val_agend * 100) if val_agend > 0 else 0
    tx_fechamento = (val_vendas / val_reais * 100) if val_reais > 0 else 0

    c1, c2 = st.columns([1.5, 1])

    with c1:
        st.subheader("Funil de Conversão (MoFu → BoFu)")
        fig_funnel = go.Figure(go.Funnel(
            y=["Leads Criados", "Demos Agendadas", "Demos Realizadas", "Vendas Fechadas"],
            x=[val_criados, val_agend, val_reais, val_vendas],
            textinfo="value+percent initial",
            marker={"color": ["#003366", "#fd7e14", "#2ca02c", "#198754"]}
        ))
        fig_funnel.update_layout(margin=dict(t=30, b=10, l=10, r=10), height=350)
        st.plotly_chart(fig_funnel, use_container_width=True)

    with c2:
        st.subheader("Termômetros de Saúde")
        fig_gauge = go.Figure()

        fig_gauge.add_trace(go.Indicator(
            mode="gauge+number",
            value=tx_agendamento,
            number={'suffix': "%", 'font': {'size': 24}},
            title={'text': "Tx. Agendamento<br>(SDR)", 'font': {'size': 14}},
            domain={'x': [0, 1], 'y': [0.7, 1]},
            gauge={'axis': {'range': [0, 100]}, 'bar': {'color': "#fd7e14"}}
        ))

        fig_gauge.add_trace(go.Indicator(
            mode="gauge+number",
            value=tx_realizacao,
            number={'suffix': "%", 'font': {'size': 24}},
            title={'text': "Tx. Realização<br>(Show Rate)", 'font': {'size': 14}},
            domain={'x': [0, 1], 'y': [0.35, 0.65]},
            gauge={'axis': {'range': [0, 100]}, 'bar': {'color': "#2ca02c"}}
        ))

        fig_gauge.add_trace(go.Indicator(
            mode="gauge+number",
            value=tx_fechamento,
            number={'suffix': "%", 'font': {'size': 24}},
            title={'text': "Tx. Fechamento<br>(EV)", 'font': {'size': 14}},
            domain={'x': [0, 1], 'y': [0, 0.3]},
            gauge={'axis': {'range': [0, 100]}, 'bar': {'color': "#198754"}}
        ))
        
        fig_gauge.update_layout(margin=dict(t=20, b=20, l=20, r=20), height=350)
        st.plotly_chart(fig_gauge, use_container_width=True)

    st.divider()

    st.subheader("🏆 Ranking de Eficiência por Colaborador")
    col_rank_sdr, col_rank_ev = st.columns(2)

    with col_rank_sdr:
        st.markdown("**Top SDRs por Agendamento (Meio de Funil)**")
        df_rank_sdr = df_det_mes.groupby("usuario_sdr").agg(
            leads_assumidos=("leads_criados", "sum"),
            agendados=("demo_agendada", "sum")
        ).reset_index()
        df_rank_sdr["taxa_conversao"] = np.where(df_rank_sdr["leads_assumidos"] > 0, 
                                                 (df_rank_sdr["agendados"] / df_rank_sdr["leads_assumidos"]) * 100, 0)
        df_rank_sdr = df_rank_sdr[df_rank_sdr["leads_assumidos"] > 0].sort_values("taxa_conversao", ascending=True)

        fig_bar_sdr = px.bar(
            df_rank_sdr, x="taxa_conversao", y="usuario_sdr", orientation='h',
            text=df_rank_sdr["taxa_conversao"].apply(lambda x: f"{x:.1f}%"),
            color="taxa_conversao", color_continuous_scale="Oranges",
            labels={"taxa_conversao": "Taxa de Agendamento (%)", "usuario_sdr": "SDR"}
        )
        fig_bar_sdr.update_traces(textposition='outside')
        fig_bar_sdr.update_layout(coloraxis_showscale=False, margin=dict(t=20, l=10, r=20, b=20), height=300)
        st.plotly_chart(fig_bar_sdr, use_container_width=True)

    with col_rank_ev:
        st.markdown("**Top EVs por Fechamento (Fundo de Funil)**")
        df_rank_ev = df_det_mes.groupby("usuario_ev").agg(
            demos_feitas=("demo_realizada", "sum"),
            vendas=("leads_conquistados", "sum")
        ).reset_index()
        df_rank_ev["taxa_conversao"] = np.where(df_rank_ev["demos_feitas"] > 0, 
                                                (df_rank_ev["vendas"] / df_rank_ev["demos_feitas"]) * 100, 0)
        df_rank_ev = df_rank_ev[df_rank_ev["demos_feitas"] > 0].sort_values("taxa_conversao", ascending=True)

        fig_bar_ev = px.bar(
            df_rank_ev, x="taxa_conversao", y="usuario_ev", orientation='h',
            text=df_rank_ev["taxa_conversao"].apply(lambda x: f"{x:.1f}%"),
            color="taxa_conversao", color_continuous_scale="Greens",
            labels={"taxa_conversao": "Taxa de Fechamento (%)", "usuario_ev": "EV"}
        )
        fig_bar_ev.update_traces(textposition='outside')
        fig_bar_ev.update_layout(coloraxis_showscale=False, margin=dict(t=20, l=10, r=20, b=20), height=300)
        st.plotly_chart(fig_bar_ev, use_container_width=True)
