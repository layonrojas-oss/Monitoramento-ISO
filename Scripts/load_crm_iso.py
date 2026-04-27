# -*- coding: utf-8 -*-
import pandas as pd
import os
from datetime import datetime

diretorio_bruto = "dados_brutos"
nome_arquivo = "base_jornada_sc_iso.xlsx"
caminho_arquivo = os.path.join(diretorio_bruto, nome_arquivo)

# 1. Ajuste das colunas para refletir a nova CTE (agrupada por ano/mes)
colunas_selecionadas = [
    'ano',
    'mes',
    'carteira_atual',
    'carteira_ativando',
    'pct_carteira_ativando',
    'carteira_indicando',
    'pct_carteira_indicando',
    'leads_por_contador',
    'carteira_reuniao_realizada',
    'pct_carteira_reuniao_realizada',
    'qtd_reunioes'
]

try:
    if not os.path.exists(caminho_arquivo):
        raise FileNotFoundError(
            f"Arquivo nao encontrado: {caminho_arquivo}\n"
            f"Verifique se o arquivo '{nome_arquivo}' esta na pasta '{diretorio_bruto}'"
        )
    
    print("Carregando arquivo: " + caminho_arquivo)
    df = pd.read_excel(caminho_arquivo, usecols=colunas_selecionadas, engine='openpyxl')
    
    print("\nProcessando métricas da nova estrutura (CTE Jornada)...")
    
    # Criar a coluna 'mes_referencia' no formato YYYY-MM para o dashboard
    df['mes_referencia'] = df.apply(lambda x: f"{int(x['ano'])}-{int(x['mes']):02d}", axis=1)

    # Renomear as colunas para o padrão que o dashboard (tab_end_to_end) já espera
    df_renamed = df.rename(columns={
        'carteira_atual': 'Carteira_Atual',
        'carteira_reuniao_realizada': 'Carteira_com_Reuniao',
        'qtd_reunioes': 'Quantidade_Reunioes',
        'carteira_indicando': 'Carteira_Indicando',
        'carteira_ativando': 'Carteira_Ativando',
        # A CTE chama de leads_por_contador, mas representa a contagem total de leads (count distinct b.op_id)
        'leads_por_contador': 'Leads_Criados' 
    })
    
    # Preencher valores nulos com 0
    df_renamed.fillna(0, inplace=True)

    # Ordenar as colunas
    ordem_colunas_topo = [
        'mes_referencia', 
        'Carteira_Atual', 
        'Carteira_com_Reuniao', 
        'pct_carteira_reuniao_realizada', 
        'Quantidade_Reunioes',
        'Carteira_Indicando', 
        'pct_carteira_indicando', 
        'Leads_Criados',
        'Carteira_Ativando', 
        'pct_carteira_ativando'
    ]
    topo_funil = df_renamed[ordem_colunas_topo]

    # MÓDULO 2: Visão de Oportunidades não está mais presente na nova CTE.
    # Geramos um DataFrame vazio para manter compatibilidade com a exportação final.
    visao_geral_funil = pd.DataFrame(columns=[
        'Fase da última Oportunidade CRM', 'Total_Oportunidades', 'Total_NMRR_no_Mes', 'Total_Apps_Ativados_no_Mes'
    ])

    diretorio_processado = 'dados_processados'
    os.makedirs(diretorio_processado, exist_ok=True)
    nome_arquivo_saida = datetime.now().strftime('analise_jornada_sc_iso_%Y_%m_%d.xlsx')
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
    print(f"Total de Meses Processados: {len(df)}")
    print("="*60)

except Exception as e:
    print(f"ERRO: {e}")
