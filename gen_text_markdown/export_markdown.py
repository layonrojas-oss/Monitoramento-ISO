import os
from datetime import datetime
import glob
import pandas as pd

def formatar_moeda(valor):
    return f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

def gerar_texto_markdown(data_ref, topo_dados, meio_dados, fundo_dados, metas):
    """
    Gera o conteúdo em Markdown combinando os dados do funil e o pace comercial.
    Os parâmetros devem ser dicionários extraídos dos dataframes processados.
    """
    
    md_content = f"""# Relatório Diário de Performance: Inside Sales Outbound
**Data de Referência:** {data_ref}
**Gerado em:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

---

## 1. Visão End-to-End (Produtividade da Esteira)

### 📊 Topo de Funil (Trabalho do EC)
* **Carteira Atual:** {topo_dados.get('carteira_atual', 0)} contadores
* **Carteira com Reunião:** {topo_dados.get('cart_reuniao', 0)} ({topo_dados.get('pct_cart_reuniao', 0):.1f}% da carteira)
* **Leads Indicados/Criados:** {topo_dados.get('leads_criados', 0)}
* **Média de Leads por Contador:** {topo_dados.get('leads_por_contador', 0):.2f}

### 🎯 Meio de Funil (Trabalho do SDR)
* **Leads Agendados:** {meio_dados.get('l_agendados', 0)}
* **Taxa de Agendamento:** {meio_dados.get('tx_agend', 0):.1f}% (Meta: {metas.get('tx_agend_meta', 0):.1f}%)
* **Demos Realizadas:** {meio_dados.get('d_realizadas', 0)}

### 💰 Fundo de Funil (Trabalho do EV)
* **Oportunidades Conquistadas:** {fundo_dados.get('l_conquistados', 0)}
* **Taxa de Conversão (Demos para Conquista):** {fundo_dados.get('tx_conv_demos', 0):.1f}%
* **Apps Ativados:** {fundo_dados.get('a_ativados', 0)}
* **Índice de Múltiplos CNPJs:** {fundo_dados.get('mult_cnpj', 0):.2f}

---

## 2. Monitoramento de Receita e Pace (NMRR)

* **Ticket Médio:** {formatar_moeda(fundo_dados.get('tk_medio', 0))}
* **NMRR Padrão (Sem BPO):** {formatar_moeda(fundo_dados.get('nmrr_sem_bpo', 0))}
* **NMRR BPO:** {formatar_moeda(fundo_dados.get('nmrr_bpo', 0))}
* **NMRR Total Realizado:** {formatar_moeda(fundo_dados.get('nmrr_total', 0))} (Meta: {formatar_moeda(metas.get('nmrr_total_meta', 0))})
* **Atingimento da Meta de Receita:** {fundo_dados.get('atingimento_nmrr', 0):.1f}%

---

## 3. Contexto Operacional para a IA
*Verificar se existem quebras bruscas na transição de leads criados pelo EC para agendamentos do SDR, ou problemas de conversão nas demos realizadas pelo EV.*
"""
    return md_content

def salvar_relatorio_md(conteudo, diretorio_saida="relatorios_diarios"):
    """
    Salva a string markdown em um arquivo .md físico.
    """
    if not os.path.exists(diretorio_saida):
        os.makedirs(diretorio_saida)
        
    data_hoje = datetime.now().strftime('%Y-%m-%d')
    nome_arquivo = f"report_iso_{data_hoje}.md"
    caminho_completo = os.path.join(diretorio_saida, nome_arquivo)
    
    with open(caminho_completo, "w", encoding="utf-8") as f:
        f.write(conteudo)
        
    return caminho_completo


def coletar_dados_topo(diretorio_processado="dados_processados"):
    """
    Procura o arquivo processado mais recente em `diretorio_processado` e tenta
    extrair a aba 'Topo do Funil' para compor o dicionário de topo.
    Retorna (data_ref, topo_dados) onde topo_dados contém chaves usadas pelo gerador.
    """
    padrao = os.path.join(diretorio_processado, "*.xlsx")
    arquivos = glob.glob(padrao)
    if not arquivos:
        return datetime.now().strftime('%Y-%m-%d'), {}

    # escolhe o arquivo mais recente por modificação
    arquivo = max(arquivos, key=os.path.getmtime)
    try:
        xls = pd.read_excel(arquivo, sheet_name=None, engine='openpyxl')
    except Exception:
        return datetime.now().strftime('%Y-%m-%d'), {}

    # tenta ler a aba 'Topo do Funil' (nome escrito no load_crm_iso.py)
    sheet_name = None
    for nome in xls.keys():
        if 'topo' in nome.lower():
            sheet_name = nome
            break

    if sheet_name is None:
        return datetime.now().strftime('%Y-%m-%d'), {}

    df_topo = xls[sheet_name]
    if df_topo.empty:
        return datetime.now().strftime('%Y-%m-%d'), {}

    # preferir a linha do mês mais recente disponível
    if 'mes_referencia' in df_topo.columns:
        # garante que escolhemos o mês mais recente (tratando como data YYYY-MM)
        try:
            df_topo['__dt'] = pd.to_datetime(df_topo['mes_referencia'], format='%Y-%m')
            row = df_topo.loc[df_topo['__dt'].idxmax()]
            data_ref = row.get('mes_referencia', datetime.now().strftime('%Y-%m-%d'))
        except Exception:
            df_topo = df_topo.sort_values('mes_referencia')
            row = df_topo.iloc[-1]
            data_ref = row.get('mes_referencia', datetime.now().strftime('%Y-%m-%d'))
    else:
        row = df_topo.iloc[0]
        data_ref = datetime.now().strftime('%Y-%m-%d')

    def g(col):
        return int(row[col]) if col in row.index and pd.notnull(row[col]) else 0

    carteira_atual = g('Carteira_Atual')
    cart_reuniao = g('Carteira_com_Reuniao')
    carteira_indicando = g('Carteira_Indicando')
    leads_criados = g('Leads_Criados')
    pct_cart_reuniao = (cart_reuniao / carteira_atual) if carteira_atual > 0 else 0
    leads_por_contador = (leads_criados / carteira_indicando) if carteira_indicando > 0 else 0

    topo_dados = {
        'carteira_atual': carteira_atual,
        'cart_reuniao': cart_reuniao,
        'pct_cart_reuniao': pct_cart_reuniao,
        'leads_criados': leads_criados,
        'leads_por_contador': leads_por_contador
    }

    return data_ref, topo_dados


def coletar_dados_pace(diretorio_processado="dados_processados"):
    """
    Procura pelo arquivo de pace mais recente e extrai métricas de Consolidad Mensal / Tracking Diário.
    Retorna (meio_dados, fundo_dados) como dicionários.
    """
    padrao = os.path.join(diretorio_processado, "pace_comercial_outbound_*.xlsx")
    arquivos = glob.glob(padrao)
    if not arquivos:
        # fallback: tenta qualquer xlsx que contenha 'pace'
        arquivos = [p for p in glob.glob(os.path.join(diretorio_processado, '*.xlsx')) if 'pace' in os.path.basename(p).lower()]
    if not arquivos:
        return {}, {}

    arquivo = max(arquivos, key=os.path.getmtime)
    try:
        xls = pd.ExcelFile(arquivo, engine='openpyxl')
    except Exception:
        return {}, {}

    # preferir 'Consolidado Mensal' ou 'Tracking Diário -'
    sheet = None
    for nome in xls.sheet_names:
        if 'consolidado' in nome.lower():
            sheet = nome
            break
    if sheet is None:
        for nome in xls.sheet_names:
            if 'tracking' in nome.lower() or 'base completa' in nome.lower():
                sheet = nome
                break

    if sheet is None:
        return {}, {}

    df = pd.read_excel(xls, sheet_name=sheet)
    if df.empty:
        return {}, {}

    # escolhe a linha do mês mais recente
    if 'mes_referencia' in df.columns:
        try:
            df['__dt'] = pd.to_datetime(df['mes_referencia'], format='%Y-%m')
            row = df.loc[df['__dt'].idxmax()]
        except Exception:
            row = df.iloc[-1]
    else:
        row = df.iloc[-1]

    meio = {
        'l_agendados': int(row.get('leads_agendados_realizado', 0)),
        'tx_agend': row.get('leads_agendados_realizado', 0) / row.get('leads_agendados_realizado', 1) if row.get('leads_agendados_realizado', 0) else 0,
        'd_realizadas': int(row.get('demos_realizadas_realizado', 0)),
    }

    fundo = {
        'l_conquistados': int(row.get('leads_conquistados_realizado', 0)),
        'tx_conv_demos': row.get('tx_conv_demos_realizado', 0),
        'a_ativados': int(row.get('apps_ativados_realizado', 0)),
        'mult_cnpj': row.get('indice_multiplo_realizado', 0),
        'tk_medio': row.get('ticket_medio_realizado', 0),
        'nmrr_sem_bpo': row.get('nmrr_sem_bpo_realizado', 0),
        'nmrr_bpo': row.get('nmrr_bpo_realizado', 0),
        'nmrr_total': row.get('nmrr_total_realizado', 0),
        'atingimento_nmrr': row.get('atingimento_nmrr_total_pct', row.get('atingimento_nmrr_erp_pct', 0))
    }

    return meio, fundo


def main():
    data_ref, topo = coletar_dados_topo()
    meio_pace, fundo_pace = coletar_dados_pace()

    # se pace retornou dados, usa-os; senão usa zeros
    meio = meio_pace if meio_pace else {'l_agendados': 0, 'tx_agend': 0, 'd_realizadas': 0}
    fundo = fundo_pace if fundo_pace else {'l_conquistados': 0, 'tx_conv_demos': 0, 'a_ativados': 0, 'mult_cnpj': 0, 'tk_medio': 0, 'nmrr_sem_bpo': 0, 'nmrr_bpo': 0, 'nmrr_total': 0, 'atingimento_nmrr': 0}
    metas = {'tx_agend_meta': 0, 'nmrr_total_meta': 0}

    conteudo = gerar_texto_markdown(data_ref, topo, meio, fundo, metas)
    caminho = salvar_relatorio_md(conteudo)
    print(f"Arquivo salvo em: {caminho}")


if __name__ == '__main__':
    main()

# Exemplo de Uso Integrado ao seu Streamlit:
# (Você pode rodar isso após compilar seus KPIs na função render_tab_end_to_end)
# caminho_do_arquivo = salvar_relatorio_md(gerar_texto_markdown(data_hoje, topo_dict, meio_dict, fundo_dict, metas_dict))