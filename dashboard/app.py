import streamlit as st
import os

from utils.data_loader import load_data, apply_mtd_pace, apply_mtd_cluster, apply_filters_detailed
from views.tab_end_to_end import render_tab_end_to_end
from views.tab_gaps import render_tab_gaps
from views.tab_visual import render_tab_visual

# 1. Configuração Inicial
st.set_page_config(page_title="Dashboard ISO | Operações", layout="wide")

def load_local_css(file_name):
    if os.path.exists(file_name):
        with open(file_name) as f:
            st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

# Carrega o CSS criado na pasta assets
load_local_css('assets/style.css')

# 2. Carrega Dados Brutos
data = load_data()

# 3. Sidebar (Filtros Globais)
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

# 4. Aplica Filtros aos Datasets
df_pace_full = apply_mtd_pace(data["pace_diario"], f_dia_util)
df_p_atual = df_pace_full[df_pace_full["mes_referencia"] == f_mes]

df_c_raw = apply_filters_detailed(data["cluster"], f_mes, f_iso, f_2030, f_ipp, f_colab, f_tamanho) if "cluster_faturamento" in data["cluster"].columns else data["cluster"]
df_c_hist = apply_mtd_cluster(df_c_raw, f_dia_util)
df_det_mes = apply_filters_detailed(data["detalhado"], f_mes, f_iso, f_2030, f_ipp, f_colab, f_tamanho)
df_det_mes = df_det_mes[df_det_mes["mes_referencia"] == f_mes]

# 5. Interface Principal
st.title("🚀 Reportologia Inside Sales Outbound")
tab1, tab2, tab3 = st.tabs(["🎯 Visão End-to-End & Pace", "🔍 Análise de Gaps (Linha a Linha)", "📊 Funil Visual"])

with tab1:
    render_tab_end_to_end(f_mes, f_colab, data["topo"], df_p_atual, df_pace_full, df_c_hist)

with tab2:
    render_tab_gaps(f_mes, f_dia_util, data["detalhado"], f_iso, f_2030, f_ipp, f_colab, f_tamanho)

with tab3:
    render_tab_visual(f_mes, df_det_mes)
