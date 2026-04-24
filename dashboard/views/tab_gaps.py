import streamlit as st
import pandas as pd

def render_tab_gaps(f_mes, f_dia_util, df_detalhado, f_iso, f_2030, f_ipp, f_colab, f_tamanho):
    from utils.data_loader import apply_filters_detailed
    st.header(f"Governança Operacional - Monitoramento de Gaps ({f_mes})")
    
    df_det_mtd = df_detalhado.copy()
    cut = f_dia_util
    
    if "dia_util_criacao" in df_det_mtd.columns: df_det_mtd.loc[df_det_mtd["dia_util_criacao"] > cut, "leads_criados"] = 0
    if "dia_util_demo" in df_det_mtd.columns: df_det_mtd.loc[df_det_mtd["dia_util_demo"] > cut, ["demo_agendada", "demo_realizada"]] = 0
    if "dia_util_ativacao" in df_det_mtd.columns:
        df_det_mtd.loc[df_det_mtd["dia_util_ativacao"] > cut, ["leads_conquistados", "apps_ativados", "nmrr_gerado"]] = 0
        if "apps_erp" in df_det_mtd.columns: df_det_mtd.loc[df_det_mtd["dia_util_ativacao"] > cut, ["apps_erp", "apps_bpo", "nmrr_erp", "nmrr_bpo"]] = 0

    df_det_f = apply_filters_detailed(df_det_mtd, f_mes, f_iso, f_2030, f_ipp, f_colab, f_tamanho)
    df_det_mes = df_det_f[df_det_f["mes_referencia"] == f_mes]

    st.markdown("##### Performance do Fluxo no Mês")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Leads Recebidos", int(df_det_mes["leads_criados"].sum()))
    c2.metric("Demos Agendadas", int(df_det_mes["demo_agendada"].sum()))
    c3.metric("Demos Realizadas", int(df_det_mes["demo_realizada"].sum()))
    c4.metric("Vendas Fechadas", int(df_det_mes["leads_conquistados"].sum()))
    
    st.divider()
    st.subheader("🔍 Detalhamento Linha a Linha (Análise de Gargalos)")
    
    filtro_gap = st.radio("Selecione a Visão Estratégica de Funil:", [
        "Todos os Leads", "🛑 Gargalo SDR (Leads assumidos sem Demo Agendada)",
        "🛑 Gargalo EV (Demos agendadas que não foram Realizadas)",
        "🛑 Gargalo de Fechamento (Demos Realizadas que não viraram Venda)", "✅ Sucesso (Vendas Conquistadas)"
    ], horizontal=True)

    if "SDR" in filtro_gap: df_view = df_det_mes[(df_det_mes["leads_criados"] > 0) & (df_det_mes["demo_agendada"] == 0)]
    elif "EV" in filtro_gap: df_view = df_det_mes[(df_det_mes["demo_agendada"] > 0) & (df_det_mes["demo_realizada"] == 0)]
    elif "Fechamento" in filtro_gap: df_view = df_det_mes[(df_det_mes["demo_realizada"] > 0) & (df_det_mes["leads_conquistados"] == 0)]
    elif "Sucesso" in filtro_gap: df_view = df_det_mes[df_det_mes["leads_conquistados"] > 0]
    else: df_view = df_det_mes

    cols_display = [c for c in ["lead_id", "cnpj", "usuario_ec", "usuario_sdr", "usuario_ev", "status", "fase", "cluster_faturamento", "leads_criados", "demo_agendada", "demo_realizada", "leads_conquistados", "nmrr_gerado"] if c in df_view.columns]
    
    if not df_view.empty: st.dataframe(df_view[cols_display], width="stretch", hide_index=True)
    else: st.success("Não foram encontrados leads com essa característica no período!")
