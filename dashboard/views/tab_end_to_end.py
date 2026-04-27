import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime
from dateutil.relativedelta import relativedelta
from utils.helpers import MESES_PT, MESES_ABREV, formatar_moeda, format_mes_yy, calcular_atingimento, calcular_var_pct, str_to_float_pct
from components.funil_cards import render_card_topo, render_card_meio, render_card_fundo

def render_tab_end_to_end(f_mes, f_colab, df_topo, df_p_atual, df_pace_full, df_c_hist):
    mes_atual_dt = datetime.strptime(f_mes, "%Y-%m")
    mes_ant_dt = mes_atual_dt - relativedelta(months=1)
    label_var = f"Var % {MESES_ABREV[mes_atual_dt.month]} x {MESES_ABREV[mes_ant_dt.month]}"
    
    st.markdown(f"<h3 style='margin-bottom: 5px;'>Visão End-to-End | {MESES_PT[mes_atual_dt.month].capitalize()}</h3>", unsafe_allow_html=True)
    st.markdown("<p style='color: #6c757d; margin-bottom: 20px;'>Integração do engajamento de Carteira (CRM) com a performance comercial (Pace).</p>", unsafe_allow_html=True)
    
    # Preparação de Dados Topo (Ajustado para o novo formato)
    df_topo_f = df_topo.copy()
    if not df_topo_f.empty:
        # Agora aplicamos o filtro pelo mês selecionado na interface
        if "mes_referencia" in df_topo_f.columns:
            df_topo_f = df_topo_f[df_topo_f["mes_referencia"] == f_mes]
        
        # Filtro de colaborador entra com validação de segurança caso seja removido em definitivo do modelo
        if f_colab != "Todos" and "Colaborador" in df_topo_f.columns:
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
  
    # Preparação Dados Meio e Fundo
    row = df_p_atual.iloc[0] if not df_p_atual.empty else pd.Series()
    l_agendados = row.get("leads_agendados_realizado", 0)
    tx_agend = (l_agendados / leads_criados) if leads_criados > 0 else 0
    d_realizadas = row.get("demos_realizadas_realizado", 0)
    l_conquistados = row.get("leads_conquistados_realizado", 0)
    tx_conv_demos = (l_conquistados / d_realizadas) if d_realizadas > 0 else 0
    a_ativados = row.get("apps_ativados_realizado", 0)
    mult_cnpj = (a_ativados / l_conquistados) if l_conquistados > 0 else 0
    nmrr_sem_bpo = row.get("nmrr_sem_bpo_realizado", 0)
    nmrr_bpo = row.get("nmrr_bpo_realizado", 0)
    nmrr_total = nmrr_sem_bpo + nmrr_bpo
    tk_medio = (nmrr_sem_bpo / a_ativados) if a_ativados > 0 else 0

    c_topo, c_meio, c_fundo = st.columns(3)
    with c_topo:
        st.markdown(render_card_topo(carteira_atual, cart_reuniao, pct_cart_reuniao, qtd_reunioes, cart_indicando, pct_cart_indicando, cart_ativando, pct_cart_ativando, leads_por_contador, leads_criados), unsafe_allow_html=True)
    with c_meio:
        st.markdown(render_card_meio(l_agendados, tx_agend, d_realizadas), unsafe_allow_html=True)
    with c_fundo:
        st.markdown(render_card_fundo(l_conquistados, tx_conv_demos, a_ativados, mult_cnpj, tk_medio, nmrr_bpo, nmrr_sem_bpo, nmrr_total, formatar_moeda), unsafe_allow_html=True)
    
    st.divider()
    st.subheader("🏁 Monitoramento Diário (Pace Metas vs Realizado)")
    
    if not df_p_atual.empty:
        # Metas
        m_recebidos, m_demos, m_conq, m_apps = row.get("leads_agendados_meta", 0), row.get("demos_realizadas_meta", 0), row.get("leads_conquistados_meta", 0), row.get("apps_ativados_meta", 0)
        nmrr_padrao_meta, nmrr_bpo_meta, nmrr_total_meta = row.get("nmrr_sem_bpo_meta", 0), row.get("nmrr_bpo_meta", 0), row.get("nmrr_total_meta", 0)
        tx_conv_meta = (m_conq / m_demos) if m_demos > 0 else 0
        ind_mult_meta = (m_apps / m_conq) if m_conq > 0 else 0
        ticket_meta = (nmrr_padrao_meta / m_apps) if m_apps > 0 else 0

        tabela_pace = pd.DataFrame({
            "Métrica": ["Leads Recebidos (Agendados)", "Demos realizadas", "Leads conquistados", "Tx. Conv. Demos", "Apps Ativados", "Indice de Múltiplo", "Ticket Médio", "NMRR (Sem BPO)", "NMRR BPO", "NMRR Total"],
            "Realizado": [f"{int(l_agendados)}", f"{int(d_realizadas)}", f"{int(l_conquistados)}", f"{((l_conquistados/d_realizadas)*100 if d_realizadas > 0 else 0):.0f}%", f"{int(a_ativados)}", f"{mult_cnpj:.2f}".replace(".", ","), formatar_moeda(tk_medio), formatar_moeda(nmrr_sem_bpo), formatar_moeda(nmrr_bpo), formatar_moeda(nmrr_total)],
            "Meta": [f"{int(m_recebidos)}", f"{int(m_demos)}", f"{int(m_conq)}", f"{(tx_conv_meta*100):.0f}%", f"{int(m_apps)}", f"{ind_mult_meta:.2f}".replace(".", ","), formatar_moeda(ticket_meta), formatar_moeda(nmrr_padrao_meta), formatar_moeda(nmrr_bpo_meta), formatar_moeda(nmrr_total_meta)],
            "Ating. %": [f"{calcular_atingimento(l_agendados, m_recebidos):.0f}%", f"{calcular_atingimento(d_realizadas, m_demos):.0f}%", f"{calcular_atingimento(l_conquistados, m_conq):.0f}%", f"{calcular_atingimento(((l_conquistados/d_realizadas) if d_realizadas > 0 else 0), tx_conv_meta):.0f}%", f"{calcular_atingimento(a_ativados, m_apps):.0f}%", f"{calcular_atingimento(mult_cnpj, ind_mult_meta):.0f}%", f"{calcular_atingimento(tk_medio, ticket_meta):.0f}%", f"{calcular_atingimento(nmrr_sem_bpo, nmrr_padrao_meta):.0f}%", f"{calcular_atingimento(nmrr_bpo, nmrr_bpo_meta):.0f}%", f"{calcular_atingimento(nmrr_total, nmrr_total_meta):.0f}%"]
        })

        def style_atingimento(val):
            try:
                num = float(val.replace('%', ''))
                if num < 0: return 'background-color: #f8d7da; color: #721c24; text-align: center;'
                else: return 'background-color: #d4edda; color: #155724; text-align: center;'
            except: return ''

        c1, c2, c3 = st.columns([1, 6, 1])
        with c2:
            st.dataframe(tabela_pace.style.map(style_atingimento, subset=['Ating. %']).set_properties(**{'text-align': 'center'}, subset=['Realizado', 'Meta']), width="stretch", hide_index=True)
        
        st.divider()
        
        st.subheader("📊 Histórico Evolução Mensal (NMRR)")

        todos_meses = sorted(df_pace_full["mes_referencia"].unique())
        try:
            idx_mes = todos_meses.index(f_mes)
        except ValueError:
            idx_mes = -1
        
        meses_selecionados = todos_meses[max(0, idx_mes - 6) : idx_mes + 1] if idx_mes >= 0 else []

        if meses_selecionados:
            df_hist = df_pace_full[df_pace_full["mes_referencia"].isin(meses_selecionados)].copy()
            df_hist["nmrr_total_realizado"] = df_hist["nmrr_total_realizado"].fillna(0)
            
            pivot_hist = df_hist.pivot_table(index='mes_referencia', values='nmrr_total_realizado', aggfunc='sum').reindex(meses_selecionados).T
            pivot_hist.columns = [format_mes_yy(c) for c in pivot_hist.columns]
            pivot_hist.index = ["NMRR Total"]
            
            valores = pivot_hist.iloc[0].values
            val_atual = valores[-1] if len(valores) > 0 else 0
            val_ant = valores[-2] if len(valores) > 1 else 0
            val_6m_avg = np.mean(valores[:-1]) if len(valores) > 1 else 0
            
            var_mm = calcular_var_pct(val_atual, val_ant)
            var_6m = calcular_var_pct(val_atual, val_6m_avg)

            col_nome_atual = format_mes_yy(f_mes)
            mes_ant_str = meses_selecionados[-2] if len(meses_selecionados) > 1 else None
            col_nome_ant = format_mes_yy(mes_ant_str) if mes_ant_str else "Mês Ant."
            
            var_col_mm_name = f"Var% {col_nome_atual.split('/')[0]} x {col_nome_ant.split('/')[0]}"
            var_col_6m_name = f"Var% {col_nome_atual.split('/')[0]} x 6m"
            pivot_hist[var_col_mm_name] = f"{var_mm:.0f}%"
            pivot_hist[var_col_6m_name] = f"{var_6m:.0f}%"

            def style_hist_df(df_styled):
                # 1. Copia o DF
                df = df_styled.copy()

                # Identifica as colunas de valores (meses) ignorando as de variação
                value_cols = [c for c in df.columns if "Var%" not in c]

                # 2. Define o estilo de cor para as colunas de variação finais
                def style_var_cols(s):
                    val = str_to_float_pct(s)
                    if val >= 0:
                        return 'background-color: #d9ead3; color: #274e13; font-weight: bold;'
                    else:
                        return 'background-color: #f4cccc; color: #cc0000; font-weight: bold;'

                # 3. Cria o Styler garantindo alinhamento central
                styler = df.style.set_properties(**{'text-align': 'center'})

                # 4. Aplica o heatmap com a paleta RdYlGn (Red, Yellow, Green)
                # Os menores valores do período ficarão vermelhos, a média amarela e os maiores verdes.
                styler = styler.background_gradient(cmap='RdYlGn', subset=value_cols, axis=1)

                # 5. Formata a visualização para moeda via Styler
                styler = styler.format(lambda x: formatar_moeda(x) if pd.notnull(x) else formatar_moeda(0), subset=value_cols)

                # 6. Aplica os estilos das colunas fixas de Var%
                styler = styler.map(style_var_cols, subset=[var_col_mm_name, var_col_6m_name])

                return styler

            st.dataframe(style_hist_df(pivot_hist), use_container_width=True)
        else:
            st.info("Não há dados históricos suficientes para exibir a evolução mensal.")

        st.divider()
        st.subheader("Performance por Faixa de Faturamento")
        meses_4 = sorted(df_pace_full[df_pace_full["mes_referencia"] <= f_mes]["mes_referencia"].unique())[-4:]
        df_c_4m = df_c_hist[df_c_hist["mes_referencia"].isin(meses_4)]
        
        def render_cluster_table(nome_cluster, df_dados):
            st.markdown(f"<h5 style='background-color: #e69138; padding: 5px; color: white; display: inline-block; border-radius: 3px; margin-bottom: 0px;'>{nome_cluster}</h5>", unsafe_allow_html=True)
            grp = df_dados.groupby("mes_referencia").sum(numeric_only=True).reset_index()
            tabela_linhas, raw_data = [], []
            
            for m in meses_4:
                row_m = grp[grp["mes_referencia"] == m]
                dt_m = datetime.strptime(m, "%Y-%m")
                if not row_m.empty:
                    d = row_m.iloc[0]
                    ag, dm, cq, app, nm = int(d.get("total_leads", 0)), int(d.get("demos_realizadas", 0)), int(d.get("vendas_fechadas", 0)), int(d.get("vendas_fechadas", 0)), d.get("nmrr_total", 0)
                    tx, tk = (cq / dm * 100) if dm > 0 else 0, (nm / cq) if cq > 0 else 0
                else:
                    ag, dm, cq, tx, app, nm, tk = 0, 0, 0, 0, 0, 0, 0
                
                raw_data.append({"ag": ag, "dm": dm, "cq": cq, "tx": tx, "app": app, "nm": nm, "tk": tk})
                tabela_linhas.append({"Mês": MESES_PT[dt_m.month], "Agendamentos": str(ag), "Demos": str(dm), "Conquistas": str(cq), "Tx. Conv. Demos": f"{tx:.1f}%", "Apps": str(app), "NMRR": formatar_moeda(nm), "Ticket": formatar_moeda(tk)})
            
            df_tb = pd.DataFrame(tabela_linhas)
            if len(raw_data) >= 2:
                at, an = raw_data[-1], raw_data[-2]
                df_tb = pd.concat([df_tb, pd.DataFrame([{
                    "Mês": label_var,
                    "Agendamentos": f"{calcular_var_pct(at['ag'], an['ag']):.0f}%", "Demos": f"{calcular_var_pct(at['dm'], an['dm']):.0f}%",
                    "Conquistas": f"{calcular_var_pct(at['cq'], an['cq']):.0f}%", "Tx. Conv. Demos": f"{(at['tx'] - an['tx']):.1f}%",
                    "Apps": f"{calcular_var_pct(at['app'], an['app']):.0f}%", "NMRR": f"{calcular_var_pct(at['nm'], an['nm']):.0f}%",
                    "Ticket": f"{calcular_var_pct(at['tk'], an['tk']):.0f}%"
                }])], ignore_index=True)

            def style_cluster_var(row):
                styles = [''] * len(row)
                if row["Mês"] == label_var:
                    for i, col in enumerate(df_tb.columns):
                        if col == "Mês": styles[i] = 'background-color: #f3f3f3; font-weight: bold;'
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
            render_cluster_table(fx, df_c_4m[df_c_4m["faixa_faturamento"] == fx])
