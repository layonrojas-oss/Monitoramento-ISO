# -*- coding: utf-8 -*-
import os
import pandas as pd
import numpy as np
from datetime import datetime

def calc_dia_util(d):
    """Calcula o dia útil do mês referente à data do evento (MTD)"""
    if pd.isnull(d): return 0
    try:
        return np.busday_count(d.replace(day=1).date(), d.date()) + 1
    except:
        return 0

def main():
    # =========================================================================
    # PASSO 1: Configuração de Diretórios e Arquivos
    # =========================================================================
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    diretorio_bruto = os.path.join(base_dir, "dados_brutos")
    arquivo_bruto = "base_detalhada_iso.xlsx" # Arquivo com resultado detalhado da nova CTE
    caminho_arquivo = os.path.join(diretorio_bruto, arquivo_bruto)
    
    diretorio_processado = os.path.join(base_dir, "dados_processados")
    os.makedirs(diretorio_processado, exist_ok=True)

    if not os.path.exists(caminho_arquivo):
        print(f"Erro: Arquivo não encontrado em {caminho_arquivo}.")
        return

    # =========================================================================
    # PASSO 2: Leitura e Tratamento Inicial dos Dados
    # =========================================================================
    print("Lendo a base de dados detalhada. Isso pode levar alguns segundos...")
    df = pd.read_excel(caminho_arquivo, engine="openpyxl")

    # Mapeando evento temporal MTD
    df['data_evento'] = pd.to_datetime(df['data_evento'], errors='coerce')
    df['dia_util'] = df['data_evento'].apply(calc_dia_util)
    
   
    if 'mes_ref' in df.columns:
        df['mes_referencia'] = pd.to_datetime(df['mes_ref'], errors='coerce').dt.strftime('%Y-%m')
    else:
        df['mes_referencia'] = df['data_evento'].dt.strftime('%Y-%m')

        # =========================================================================
    # PASSO 3: Pivotar o Empilhamento para a Visão Linha a Linha
    # =========================================================================
    print("Processando visão de funil linha a linha...")
    
    
    base_cols = [
        'cnpj', 'origem', 'status', 'fase', 'opportunity_value', 'cluster_faturamento',
        'time', 'contabilidades_consultoria', 'contador_cnpj', 'contador_time_nome',
        'carteira_iso', 'ipp', 'plano_2030', 'cohort_demo', 
        'usuario_ec', 'usuario_sdr', 'usuario_ev',
        'apps_erp', 'apps_bpo', 'nmrr_erp', 'nmrr_bpo',
        'created_at', 'data_primeira_demo', 'data_ativacao' # <-- Datas adicionadas
    ]
    base_cols = [c for c in base_cols if c in df.columns]

    df_metrics = df.pivot_table(
        index=['lead_id', 'mes_referencia'],
        columns='metrica',
        values='valor_metrica',
        aggfunc='sum',
        fill_value=0
    ).reset_index()

    expected_metrics = ['leads_criados', 'demo_agendada', 'demo_realizada', 'leads_conquistados', 'apps_ativados', 'nmrr_gerado']
    for m in expected_metrics:
        if m not in df_metrics.columns:
            df_metrics[m] = 0

    df_base_info = df.groupby(['lead_id', 'mes_referencia'])[base_cols].first().reset_index()
    df_detalhado = pd.merge(df_base_info, df_metrics, on=['lead_id', 'mes_referencia'], how='left')

    
    df_detalhado['dia_util_criacao'] = pd.to_datetime(df_detalhado['created_at'], errors='coerce').apply(calc_dia_util)
    df_detalhado['dia_util_demo'] = pd.to_datetime(df_detalhado['data_primeira_demo'], errors='coerce').apply(calc_dia_util)
    df_detalhado['dia_util_ativacao'] = pd.to_datetime(df_detalhado['data_ativacao'], errors='coerce').apply(calc_dia_util)

    
    df_detalhado['apps_erp'] = np.where(df_detalhado['leads_conquistados'] > 0, df_detalhado.get('apps_erp', 0), 0)
    df_detalhado['apps_bpo'] = np.where(df_detalhado['leads_conquistados'] > 0, df_detalhado.get('apps_bpo', 0), 0)
    df_detalhado['nmrr_erp'] = np.where(df_detalhado['leads_conquistados'] > 0, df_detalhado.get('nmrr_erp', 0), 0)
    df_detalhado['nmrr_bpo'] = np.where(df_detalhado['leads_conquistados'] > 0, df_detalhado.get('nmrr_bpo', 0), 0)

    for col in ['carteira_iso', 'plano_2030', 'ipp']:
        if col in df_detalhado.columns:
            df_detalhado[col] = df_detalhado[col].fillna('N/A')


    # =========================================================================
    # PASSO 4: Re-Agrupamento para Manter os Gráficos Atuais do Dashboard
    # =========================================================================
    gap_ec = df_detalhado[df_detalhado["usuario_ec"].notna()].groupby(
        ["mes_referencia", "usuario_ec", "carteira_iso", "plano_2030", "ipp"]
    ).agg(
        total_leads=("leads_criados", "sum"),
        leads_com_demo=("demo_realizada", "sum"),
        vendas_fechadas=("leads_conquistados", "sum"),
        nmrr_gerado=("nmrr_gerado", "sum")
    ).reset_index()

    gap_sdr = df_detalhado[df_detalhado["usuario_sdr"].notna()].groupby(
        ["mes_referencia", "usuario_sdr", "carteira_iso", "plano_2030", "ipp"]
    ).agg(
        leads_recebidos=("leads_criados", "sum"),
        demos_agendadas=("demo_agendada", "sum"),
        demos_realizadas=("demo_realizada", "sum")
    ).reset_index()

    gap_ev = df_detalhado[df_detalhado["usuario_ev"].notna()].groupby(
        ["mes_referencia", "usuario_ev", "carteira_iso", "plano_2030", "ipp"]
    ).agg(
        demos_realizadas=("demo_realizada", "sum"),
        vendas_fechadas=("leads_conquistados", "sum"),
        apps_erp=("apps_erp", "sum"),
        apps_bpo=("apps_bpo", "sum"),
        nmrr_erp=("nmrr_erp", "sum"),
        nmrr_bpo=("nmrr_bpo", "sum"),
        nmrr_total=("nmrr_gerado", "sum")
    ).reset_index()

    gap_cluster = df_detalhado.groupby(["mes_referencia", "cluster_faturamento"], dropna=False).agg(
        total_leads=("leads_criados", "sum"),
        demos_realizadas=("demo_realizada", "sum"),
        vendas_fechadas=("leads_conquistados", "sum"),
        nmrr_total=("nmrr_gerado", "sum")
    ).reset_index()

    # =========================================================================
    # PASSO 5: Exportação Completa
    # =========================================================================
    nome_arquivo_saida = f"analise_gaps_esteira_{datetime.now():%Y_%m_%d}.xlsx"
    caminho_saida = os.path.join(diretorio_processado, nome_arquivo_saida)

    print("Salvando relatório gerencial detalhado...")
    with pd.ExcelWriter(caminho_saida, engine="openpyxl") as writer:
        df_detalhado.to_excel(writer, index=False, sheet_name="Base Detalhada Funil")
        gap_ec.to_excel(writer, index=False, sheet_name="Gap e Produtividade EC")
        gap_sdr.to_excel(writer, index=False, sheet_name="Gap e Produtividade SDR")
        gap_ev.to_excel(writer, index=False, sheet_name="Gap e Produtividade EV")
        gap_cluster.to_excel(writer, index=False, sheet_name="Análise por Cluster")

    print(f"Sucesso! Relatório detalhado consolidado e salvo em: {caminho_saida}")

if __name__ == "__main__":
    main()
