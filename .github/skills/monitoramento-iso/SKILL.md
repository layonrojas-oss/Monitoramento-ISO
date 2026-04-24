---
name: monitoramento-iso-pipeline
description: "Use this skill to build, revisar ou corrigir o pipeline de dados local para Inside Sales Outbound usando Python e pandas."
---

# Monitoramento ISO Pipeline Skill

## Objetivo
Ajude o usuário a criar e manter um pipeline de processamento de dados local que:
- leia arquivos brutos de `dados_brutos/`
- gere arquivos exportados em `dados_processados/`
- calcule conversões entre etapas do funil
- identifique gargalos de produtividade por SDR, EC e EV
- sempre grave o arquivo sugerido e informe o comando para executar

## Regras de Negócio
- O foco principal é conversão de funil e produtividade da equipe.
- Os dados brutos ficam em `dados_brutos/`.
- Os resultados processados devem ir para `dados_processados/`.
- Colunas principais a validar e usar frequentemente:
  - `CNPJ Contador`
  - `Contabilidade`
  - `Porte Faturamento`
  - `Status da última Oportunidade CRM`
  - `Fase da última Oportunidade CRM`
  - `Tarefas Agendadas Realizadas no Mês Atual`
  - `Reuniões Realizadas no Mês Atual`
  - `NMRR no Mês`
  - `MRR Geral`
  - `Apps Ativados Geral`
  - `Apps Ativados no Mês`
  - `Apps Ativos`
  - `Colaborador`
  - `Função`
  - `Time Comercial`

## Workflow
1. Identifique o arquivo de origem em `dados_brutos/`.
2. Verifique se o arquivo existe; se não existir, informe claramente o problema.
3. Leia os dados usando `pandas`, aplicando parsing consistente de datas e tratamento de valores ausentes.
4. Valide a presença das colunas principais. Se faltarem colunas, explique quais e por quê.
5. Normalize nomes de colunas e valores relevantes para evitar erros futuros.
6. Calcule métricas de conversão de funil e produtividade com agregações claras:
   - taxas de conversão entre etapas do funil
   - atividades realizadas por colaborador e time
   - resultados de SDR, EC e EV
7. Exporte os dados transformados para `dados_processados/` usando formatos claros (`csv` ou `parquet`).
8. Inclua comentários ou explicações breves no código para cada etapa.
9. Sempre finalize indicando o arquivo salvo e o comando exato para rodar.

## Critérios de Qualidade
- Código em Python limpo e idiomático, usando `pandas`.
- Tratamento de erro explícito para arquivo ausente e colunas faltantes.
- Explicações breves no estilo de comentários ou docstrings.
- Resultados confiáveis e fáceis de revisar.
- Nome do arquivo a ser salvo e comando de execução claramente indicados.

## Exemplo de Prompt de Uso
- "Ajude-me a criar um script que leia os dados brutos de `dados_brutos/`, calcule conversões de funil e salve em `dados_processados/` usando pandas."
- "Revisar e corrigir `Scripts/load_crm_data.py` para garantir que valide as colunas principais e salve um arquivo processado." 
- "Crie um pipeline de transformação que identifique gargalos de produtividade por `Time Comercial` e `Função`."

## Notas
- Sempre confirme se o usuário quer `csv` ou `parquet` ao exportar resultados.
- Se o usuário pedir apenas análise, ainda proponha um script de execução que grave saídas em `dados_processados/`.
- Use este skill para projetos workspace-scoped no repositório `Monitoramento ISO`. 
