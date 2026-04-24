# -*- coding: utf-8 -*-

import pandas as pd
import os
from datetime import datetime

diretorio_bruto = "dados_brutos"
nome_arquivo = "2026_04_crm_jornada_sc_is_outbound.xlsx"
caminho_arquivo = os.path.join(diretorio_bruto, nome_arquivo)

# 1. Adicionadas as colunas necessárias para as métricas de TOPO DO FUNIL
colunas_selecionadas = [
    'CNPJ Contador',
    'Contabilidade',
    'Porte Faturamento',
    'Status da última Oportunidade CRM',
    'Fase da última Oportunidade CRM',
    'Tarefas Agendadas Realizadas no Mês Atual',
    'Reuniões Realizadas no Mês Atual', # Necessário para Topo
    'Leads no Mês',                     # Necessário para Topo
    'Apps Ativados no Mês',             # Necessário para Topo
    'NMRR no Mês',
    'MRR Geral',
    'Apps Ativados Geral',
    'Apps Ativos',
    'Colaborador',
    'Função',
    'Time Comercial'
]

try:
    if not os.path.exists(caminho_arquivo):
        raise FileNotFoundError(
            f"Arquivo nao encontrado: {caminho_arquivo}\n"
            f"Verifique se o arquivo '{nome_arquivo}' esta na pasta '{diretorio_bruto}'"
        )
    
    print("Carregando arquivo: " + caminho_arquivo)
    df = pd.read_excel(caminho_arquivo, usecols=colunas_selecionadas, engine='openpyxl')
    
    # Garantir que as colunas numéricas de topo de funil sejam tratadas como números (evitar erros de NaN ou texto)
    colunas_numericas = ['Reuniões Realizadas no Mês Atual', 'Leads no Mês', 'Apps Ativados no Mês']
    for col in colunas_numericas:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)

    print("\nCalculando métricas de Topo de Funil (Base Completa)...")
    
    # ==========================================
    # MÓDULO 1: TOPO DO FUNIL (Base Completa)
    # ==========================================
    # Agrupamento primário por Colaborador
    topo_funil = df.groupby('Colaborador').agg(
        Carteira_Atual=('CNPJ Contador', 'count'),
        Quantidade_Reunioes=('Reuniões Realizadas no Mês Atual', 'sum'),
        Leads_Criados=('Leads no Mês', 'sum'),
        Apps_Ativados=('Apps Ativados no Mês', 'sum')
    ).reset_index()

    # Contagem de quantas carteiras (CNPJs) tiveram pelo menos 1 ação no mês
    cart_reuniao = df[df['Reuniões Realizadas no Mês Atual'] > 0].groupby('Colaborador').size().reset_index(name='Carteira_com_Reuniao')
    cart_indicando = df[df['Leads no Mês'] > 0].groupby('Colaborador').size().reset_index(name='Carteira_Indicando')
    cart_ativando = df[df['Apps Ativados no Mês'] > 0].groupby('Colaborador').size().reset_index(name='Carteira_Ativando')

    # Mesclar as contagens no dataframe principal de Topo
    topo_funil = topo_funil.merge(cart_reuniao, on='Colaborador', how='left').fillna(0)
    topo_funil = topo_funil.merge(cart_indicando, on='Colaborador', how='left').fillna(0)
    topo_funil = topo_funil.merge(cart_ativando, on='Colaborador', how='left').fillna(0)

    # Calcular as taxas de conversão/engajamento de Topo (em %)
    topo_funil['% Cart. com Reunião'] = topo_funil['Carteira_com_Reuniao'] / topo_funil['Carteira_Atual']
    topo_funil['% Cart. Indicando'] = topo_funil['Carteira_Indicando'] / topo_funil['Carteira_Atual']
    topo_funil['% Cart. Ativando'] = topo_funil['Carteira_Ativando'] / topo_funil['Carteira_Atual']

    # Reordenar as colunas para o Excel ficar intuitivo
    ordem_colunas_topo = [
        'Colaborador', 'Carteira_Atual', 
        'Carteira_com_Reuniao', '% Cart. com Reunião', 'Quantidade_Reunioes',
        'Carteira_Indicando', '% Cart. Indicando', 'Leads_Criados',
        'Carteira_Ativando', '% Cart. Ativando', 'Apps_Ativados'
    ]
    topo_funil = topo_funil[ordem_colunas_topo]


    # ==========================================
    # MÓDULO 2: MEIO E FUNDO DO FUNIL (Apenas Oportunidades)
    # ==========================================
    # Remover linhas onde a fase da oportunidade é nula ou vazia para o funil de vendas.
    df_ops = df[df['Fase da última Oportunidade CRM'].notna()]
    df_ops = df_ops[df_ops['Fase da última Oportunidade CRM'].astype(str).str.strip() != '']
    
    agrupamento_fase = df_ops.groupby(['Colaborador', 'Fase da última Oportunidade CRM']).size()
    
    # Calcular a taxa de conversão de Qualificação para Apresentação.
    oportunidades_qualificacao = df_ops[df_ops['Fase da última Oportunidade CRM'] == '03. Qualificação']
    oportunidades_apresentacao = df_ops[df_ops['Fase da última Oportunidade CRM'] == '04. Apresentação']
    total_qualificacao = len(oportunidades_qualificacao)
    total_apresentacao = len(oportunidades_apresentacao)
    
    taxa_conversao = total_apresentacao / total_qualificacao if total_qualificacao > 0 else None

    # Consolidar a Visão Geral do Funil por fase
    visao_geral_funil = df_ops.groupby('Fase da última Oportunidade CRM').agg(
        Total_Oportunidades=('Fase da última Oportunidade CRM', 'size'),
        Total_NMRR_no_Mes=('NMRR no Mês', 'sum'),
        Total_Apps_Ativados_no_Mes=('Apps Ativados no Mês', 'sum')
    ).reset_index()

    total_fase_03 = visao_geral_funil.loc[visao_geral_funil['Fase da última Oportunidade CRM'] == '03. Qualificação', 'Total_Oportunidades']
    total_fase_04 = visao_geral_funil.loc[visao_geral_funil['Fase da última Oportunidade CRM'] == '04. Apresentação', 'Total_Oportunidades']
    
    total_fase_03 = int(total_fase_03.iloc[0]) if not total_fase_03.empty else 0
    total_fase_04 = int(total_fase_04.iloc[0]) if not total_fase_04.empty else 0
    
    taxa_conversao_geral = total_fase_04 / total_fase_03 if total_fase_03 > 0 else None

    # ==========================================
    # MÓDULO 3: EXPORTAÇÃO
    # ==========================================
    diretorio_processado = 'dados_processados'
    os.makedirs(diretorio_processado, exist_ok=True)
    nome_arquivo_saida = datetime.now().strftime('%Y_%m_Relatorio_Funil_IS.xlsx')
    caminho_saida = os.path.join(diretorio_processado, nome_arquivo_saida)
    
    with pd.ExcelWriter(caminho_saida, engine='openpyxl') as writer:
        # Aba Primária: Topo do Funil
        topo_funil.to_excel(writer, index=False, sheet_name='Topo do Funil')
        # Aba Secundária: Visão de Oportunidades
        visao_geral_funil.to_excel(writer, index=False, sheet_name='Visão Geral de Fases')
        
    print(f"\nRelatório salvo em: {caminho_saida}")
    print("\n" + "="*60)
    print("CONSOLIDAÇÃO CONCLUÍDA COM SUCESSO")
    print("="*60)
    print(f"Total de Linhas Analisadas (Base Completa): {len(df)}")
    print(f"Total de Oportunidades Ativas: {len(df_ops)}")
    if taxa_conversao is not None:
        print(f"Taxa de Conversão Geral (03 para 04): {taxa_conversao_geral:.2%}")
    print("="*60)

except Exception as e:
    print(f"ERRO: {e}")
