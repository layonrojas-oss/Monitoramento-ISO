import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import numpy as np

def render_tab_visual(f_mes, df_det_mes):
    st.header("📊 Funil Visual - Meio e Fundo de Funil")
    st.markdown(f"Análise visual das taxas de conversão operacionais para o mês de **{f_mes}**.")
    
    val_criados, val_agend, val_reais, val_vendas = df_det_mes["leads_criados"].sum(), df_det_mes["demo_agendada"].sum(), df_det_mes["demo_realizada"].sum(), df_det_mes["leads_conquistados"].sum()
    tx_agendamento = (val_agend / val_criados * 100) if val_criados > 0 else 0
    tx_realizacao = (val_reais / val_agend * 100) if val_agend > 0 else 0
    tx_fechamento = (val_vendas / val_reais * 100) if val_reais > 0 else 0

    c1, c2 = st.columns([1.5, 1])
    with c1:
        st.subheader("Funil de Conversão (MoFu → BoFu)")
        fig_funnel = go.Figure(go.Funnel(y=["Leads Criados", "Demos Agendadas", "Demos Realizadas", "Vendas Fechadas"], x=[val_criados, val_agend, val_reais, val_vendas], textinfo="value+percent initial", marker={"color": ["#003366", "#fd7e14", "#2ca02c", "#198754"]}))
        fig_funnel.update_layout(margin=dict(t=30, b=10, l=10, r=10), height=350)
        st.plotly_chart(fig_funnel, use_container_width=True)

    with c2:
        st.subheader("Termômetros de Saúde")
        fig_gauge = go.Figure()
        fig_gauge.add_trace(go.Indicator(mode="gauge+number", value=tx_agendamento, number={'suffix': "%", 'font': {'size': 24}}, title={'text': "Tx. Agendamento<br>(SDR)", 'font': {'size': 14}}, domain={'x': [0, 1], 'y': [0.7, 1]}, gauge={'axis': {'range': [0, 100]}, 'bar': {'color': "#fd7e14"}}))
        fig_gauge.add_trace(go.Indicator(mode="gauge+number", value=tx_realizacao, number={'suffix': "%", 'font': {'size': 24}}, title={'text': "Tx. Realização<br>(Show Rate)", 'font': {'size': 14}}, domain={'x': [0, 1], 'y': [0.35, 0.65]}, gauge={'axis': {'range': [0, 100]}, 'bar': {'color': "#2ca02c"}}))
        fig_gauge.add_trace(go.Indicator(mode="gauge+number", value=tx_fechamento, number={'suffix': "%", 'font': {'size': 24}}, title={'text': "Tx. Fechamento<br>(EV)", 'font': {'size': 14}}, domain={'x': [0, 1], 'y': [0, 0.3]}, gauge={'axis': {'range': [0, 100]}, 'bar': {'color': "#198754"}}))
        fig_gauge.update_layout(margin=dict(t=20, b=20, l=20, r=20), height=350)
        st.plotly_chart(fig_gauge, use_container_width=True)

    st.divider()
    st.subheader("🏆 Ranking de Eficiência por Colaborador")
    col_rank_sdr, col_rank_ev = st.columns(2)

    with col_rank_sdr:
        st.markdown("**Top SDRs por Agendamento**")
        df_rank_sdr = df_det_mes.groupby("usuario_sdr").agg(leads_assumidos=("leads_criados", "sum"), agendados=("demo_agendada", "sum")).reset_index()
        df_rank_sdr["taxa_conversao"] = np.where(df_rank_sdr["leads_assumidos"] > 0, (df_rank_sdr["agendados"] / df_rank_sdr["leads_assumidos"]) * 100, 0)
        df_rank_sdr = df_rank_sdr[df_rank_sdr["leads_assumidos"] > 0].sort_values("taxa_conversao", ascending=True)
        fig_bar_sdr = px.bar(df_rank_sdr, x="taxa_conversao", y="usuario_sdr", orientation='h', text=df_rank_sdr["taxa_conversao"].apply(lambda x: f"{x:.1f}%"), color="taxa_conversao", color_continuous_scale="Oranges", labels={"taxa_conversao": "Taxa de Agendamento (%)", "usuario_sdr": "SDR"})
        fig_bar_sdr.update_traces(textposition='outside')
        fig_bar_sdr.update_layout(coloraxis_showscale=False, margin=dict(t=20, l=10, r=20, b=20), height=300)
        st.plotly_chart(fig_bar_sdr, use_container_width=True)

    with col_rank_ev:
        st.markdown("**Top EVs por Fechamento**")
        df_rank_ev = df_det_mes.groupby("usuario_ev").agg(demos_feitas=("demo_realizada", "sum"), vendas=("leads_conquistados", "sum")).reset_index()
        df_rank_ev["taxa_conversao"] = np.where(df_rank_ev["demos_feitas"] > 0, (df_rank_ev["vendas"] / df_rank_ev["demos_feitas"]) * 100, 0)
        df_rank_ev = df_rank_ev[df_rank_ev["demos_feitas"] > 0].sort_values("taxa_conversao", ascending=True)
        fig_bar_ev = px.bar(df_rank_ev, x="taxa_conversao", y="usuario_ev", orientation='h', text=df_rank_ev["taxa_conversao"].apply(lambda x: f"{x:.1f}%"), color="taxa_conversao", color_continuous_scale="Greens", labels={"taxa_conversao": "Taxa de Fechamento (%)", "usuario_ev": "EV"})
        fig_bar_ev.update_traces(textposition='outside')
        fig_bar_ev.update_layout(coloraxis_showscale=False, margin=dict(t=20, l=10, r=20, b=20), height=300)
        st.plotly_chart(fig_bar_ev, use_container_width=True)
