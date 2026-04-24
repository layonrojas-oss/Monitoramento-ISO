# -*- coding: utf-8 -*-
import os
import pandas as pd
from datetime import datetime

def calcular_atingimento(realizado, meta):
    """Função auxiliar para calcular o percentual de atingimento, evitando divisão por zero."""
    if meta > 0:
        return round((realizado / meta) * 100, 2)
    return 0.0

def main():
    # =========================================================================
    # PASSO 1: Configuração de Diretórios e Leitura do Arquivo
    # =========================================================================
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    diretorio_bruto = os.path.join(base_dir, "dados_brutos")
    arquivo_bruto = "base_realizado_metas_iso.xlsx" # Exportação da nova CTE focada em ISO
    caminho_arquivo = os.path.join(diretorio_bruto, arquivo_bruto)
    
    diretorio_processado = os.path.join(base_dir, "dados_processados")
    os.makedirs(diretorio_processado, exist_ok=True)

    if not os.path.exists(caminho_arquivo):
        print(f"Erro: Arquivo não encontrado em {caminho_arquivo}.")
        print("Lembre-se de salvar o resultado da CTE de IS Outbound com este nome.")
        return

    print("Lendo a base de Realizado vs Metas (Inside Sales Outbound)...")
    df = pd.read_excel(caminho_arquivo, engine="openpyxl")

    # =========================================================================
    # PASSO 2: Tratamento de Dados e Totalizadores
    # =========================================================================
    # Preenchendo campos vazios com zero para evitar erros matemáticos
    df = df.fillna(0)
    
    # Validar as colunas essenciais vindas da CTE, agora incluindo data_referencia
    colunas_necessarias = ['mes_referencia', 'data_referencia', 'dia_util']
    for col in colunas_necessarias:
        if col not in df.columns:
            print(f"Erro: A base não contém a coluna '{col}'. Verifique a extração da CTE.")
            return
        
    # Converter para data e ordenar os dados para garantir cronologia correta
    df['data_referencia'] = pd.to_datetime(df['data_referencia'])
    df = df.sort_values(['data_referencia']).reset_index(drop=True)
    
    # Criando a linha de NMRR Total (Soma do ERP + BPO)
    df["nmrr_total_realizado"] = df["nmrr_sem_bpo_realizado"] + df["nmrr_bpo_realizado"]
    df["nmrr_total_meta"] = df["nmrr_sem_bpo_meta"] + df["nmrr_bpo_meta"]

    # =========================================================================
    # PASSO 3: Visão Mensal Consolidada (Fechamento e Pace)
    # =========================================================================
    print("Agrupando dados e calculando atingimentos mensais...")
    
    # Agrupamos pelo mês de referência para ter a visão executiva
    df_mensal = df.groupby("mes_referencia").agg({
        "dia_util": "max", # Maior dia útil registrado no mês (total de dias trabalhados)
        "leads_agendados_realizado": "sum", "leads_agendados_meta": "sum",
        "demos_realizadas_realizado": "sum", "demos_realizadas_meta": "sum",
        "leads_conquistados_realizado": "sum", "leads_conquistados_meta": "sum",
        "apps_ativados_realizado": "sum", "apps_ativados_meta": "sum",
        "nmrr_sem_bpo_realizado": "sum", "nmrr_sem_bpo_meta": "sum",
        "nmrr_bpo_realizado": "sum", "nmrr_bpo_meta": "sum",
        "nmrr_total_realizado": "sum", "nmrr_total_meta": "sum"
    }).reset_index()

    # Cálculo dos Gaps (A diferença em números absolutos)
    df_mensal["gap_nmrr_total"] = df_mensal["nmrr_total_realizado"] - df_mensal["nmrr_total_meta"]
    df_mensal["gap_demos"] = df_mensal["demos_realizadas_realizado"] - df_mensal["demos_realizadas_meta"]

    # KPIs Adicionais de Qualidade / Dashboard (Taxas de Conversão e Ticket)
    df_mensal["tx_conv_demos_realizado"] = df_mensal.apply(lambda r: (r["leads_conquistados_realizado"] / r["demos_realizadas_realizado"]) if r["demos_realizadas_realizado"] > 0 else 0, axis=1)
    df_mensal["tx_conv_demos_meta"] = df_mensal.apply(lambda r: (r["leads_conquistados_meta"] / r["demos_realizadas_meta"]) if r["demos_realizadas_meta"] > 0 else 0, axis=1)

    df_mensal["indice_multiplo_realizado"] = df_mensal.apply(lambda r: (r["apps_ativados_realizado"] / r["leads_conquistados_realizado"]) if r["leads_conquistados_realizado"] > 0 else 0, axis=1)
    df_mensal["indice_multiplo_meta"] = df_mensal.apply(lambda r: (r["apps_ativados_meta"] / r["leads_conquistados_meta"]) if r["leads_conquistados_meta"] > 0 else 0, axis=1)

    df_mensal["ticket_medio_realizado"] = df_mensal.apply(lambda r: (r["nmrr_sem_bpo_realizado"] / r["apps_ativados_realizado"]) if r["apps_ativados_realizado"] > 0 else 0, axis=1)
    df_mensal["ticket_medio_meta"] = df_mensal.apply(lambda r: (r["nmrr_sem_bpo_meta"] / r["apps_ativados_meta"]) if r["apps_ativados_meta"] > 0 else 0, axis=1)

    # Lista de métricas para calcular o % de atingimento dinamicamente
    metricas = [
        ("leads_agendados", "leads_agendados_realizado", "leads_agendados_meta"),
        ("demos_realizadas", "demos_realizadas_realizado", "demos_realizadas_meta"),
        ("leads_conquistados", "leads_conquistados_realizado", "leads_conquistados_meta"),
        ("apps_ativados", "apps_ativados_realizado", "apps_ativados_meta"),
        ("nmrr_erp", "nmrr_sem_bpo_realizado", "nmrr_sem_bpo_meta"),
        ("nmrr_bpo", "nmrr_bpo_realizado", "nmrr_bpo_meta"),
        ("nmrr_total", "nmrr_total_realizado", "nmrr_total_meta")
    ]

    # Aplicando a função para criar as colunas de percentual
    for nome, col_real, col_meta in metricas:
        df_mensal[f"atingimento_{nome}_pct"] = df_mensal.apply(
            lambda row: calcular_atingimento(row[col_real], row[col_meta]), axis=1
        )

    # Cálculo do Pace Comercial Diário (Média de entrega por dia útil)
    df_mensal["pace_nmrr_dia"] = (df_mensal["nmrr_total_realizado"] / df_mensal["dia_util"].replace(0, 1)).round(2)

    # =========================================================================
    # PASSO 4: Tracking Diário do Mês Atual (MTD)
    # =========================================================================
    print("Gerando tracking diário para o mês vigente...")
    mes_atual = df["mes_referencia"].max()
    df_mtd = df[df["mes_referencia"] == mes_atual].copy()
    
    # Ordena cronologicamente para o acompanhamento dia a dia através da data de referência
    df_mtd.sort_values("data_referencia", ascending=True, inplace=True)
    df_mtd["gap_nmrr_dia"] = df_mtd["nmrr_total_realizado"] - df_mtd["nmrr_total_meta"]

    # Adicionar acumulados ao longo do mês para facilitar a análise no Excel
    colunas_acumular = [
        "leads_agendados_realizado", "leads_agendados_meta",
        "demos_realizadas_realizado", "demos_realizadas_meta",
        "leads_conquistados_realizado", "leads_conquistados_meta",
        "apps_ativados_realizado", "apps_ativados_meta",
        "nmrr_sem_bpo_realizado", "nmrr_sem_bpo_meta",
        "nmrr_bpo_realizado", "nmrr_bpo_meta",
        "nmrr_total_realizado", "nmrr_total_meta"
    ]
    
    for col in colunas_acumular:
        df_mtd[f"{col}_acumulado"] = df_mtd[col].cumsum()

    # Remover horas das datas para formatação nativa amigável no Excel
    df['data_referencia'] = df['data_referencia'].dt.date
    df_mtd['data_referencia'] = df_mtd['data_referencia'].dt.date

    # =========================================================================
    # PASSO 5: Exportação para o Excel
    # =========================================================================
    nome_arquivo_saida = f"pace_comercial_outbound_{datetime.now():%Y_%m_%d}.xlsx"
    caminho_saida = os.path.join(diretorio_processado, nome_arquivo_saida)

    print("Salvando relatório...")
    with pd.ExcelWriter(caminho_saida, engine="openpyxl") as writer:
        df_mensal.to_excel(writer, index=False, sheet_name="Consolidado Mensal")
        df_mtd.to_excel(writer, index=False, sheet_name=f"Tracking Diário - {mes_atual}")   
        df.to_excel(writer, index=False, sheet_name="Base Completa")

    print(f"Sucesso! Relatório salvo em:\n{caminho_saida}")

if __name__ == "__main__":
    main()
