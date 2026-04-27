import streamlit as st
import pandas as pd
import os
import glob
from utils.helpers import categorizar_faixa

@st.cache_data
def load_data():
    # Sobe 3 níveis: utils -> dashboard -> MONITORAMENTO ISO
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    proc_dir = os.path.join(base_dir, "dados_processados")
    
    arquivos_pace = sorted(glob.glob(os.path.join(proc_dir, "pace_comercial_outbound_*.xlsx")))
    arquivos_esteira = sorted(glob.glob(os.path.join(proc_dir, "analise_gaps_esteira_*.xlsx")))
    arquivos_crm = sorted(glob.glob(os.path.join(proc_dir, "*analise_jornada_sc_iso_*.xlsx")))
    
    if not arquivos_pace or not arquivos_esteira:
        st.error(f"Arquivos de dados processados não encontrados em {proc_dir}")
        st.stop()
        
    df_pace_diario = pd.read_excel(arquivos_pace[-1], sheet_name="Base Completa")
    df_detalhado = pd.read_excel(arquivos_esteira[-1], sheet_name="Base Detalhada Funil")
    df_cluster = pd.read_excel(arquivos_esteira[-1], sheet_name="Análise por Cluster")
    
    if arquivos_crm:
        df_topo = pd.read_excel(arquivos_crm[-1], sheet_name="Topo do Funil")
    else:
        df_topo = pd.DataFrame()
    
    df_cluster["faixa_faturamento"] = df_cluster["cluster_faturamento"].apply(categorizar_faixa)
                
    return {"pace_diario": df_pace_diario, "detalhado": df_detalhado, "cluster": df_cluster, "topo": df_topo}

def apply_mtd_pace(df_diario, cut_day):
    df_cortado = df_diario[df_diario["dia_util"] <= cut_day].copy()
    grp = df_cortado.groupby("mes_referencia").sum(numeric_only=True).reset_index()
    if "nmrr_sem_bpo_realizado" in grp.columns and "nmrr_bpo_realizado" in grp.columns:
        grp["nmrr_total_realizado"] = grp["nmrr_sem_bpo_realizado"] + grp["nmrr_bpo_realizado"]
        grp["nmrr_total_meta"] = grp.get("nmrr_sem_bpo_meta", 0) + grp.get("nmrr_bpo_meta", 0)
    return grp

def apply_mtd_cluster(df_cluster, cut_day):
    if "dia_util" not in df_cluster.columns: return df_cluster.copy()
    df_c = df_cluster[df_cluster["dia_util"] <= cut_day].copy()
    cols = [c for c in ["mes_referencia", "cluster_faturamento", "faixa_faturamento"] if c in df_cluster.columns]
    return df_c.groupby(cols).sum(numeric_only=True).reset_index()

def apply_filters_detailed(df, f_mes, f_iso, f_2030, f_ipp, f_colab, f_tamanho):
    temp_df = df[df["mes_referencia"] <= f_mes].copy()
    
    if "origem_macro" in temp_df.columns:
        temp_df = temp_df[temp_df["origem_macro"] == "Outbound"]
        
    if f_iso != "Todos": temp_df = temp_df[temp_df["carteira_iso"] == f_iso]
    if f_2030 != "Todos": temp_df = temp_df[temp_df["plano_2030"] == f_2030]
    if "Todos" not in f_ipp and len(f_ipp) > 0: temp_df = temp_df[temp_df["ipp"].astype(str).isin(f_ipp)]
        
    if f_colab != "Todos":
        temp_df = temp_df[(temp_df["usuario_ec"] == f_colab) | (temp_df["usuario_sdr"] == f_colab) | (temp_df["usuario_ev"] == f_colab)]
        
    if f_tamanho != "Todos":
        temp_df["faixa"] = temp_df["cluster_faturamento"].apply(categorizar_faixa)
        temp_df = temp_df[temp_df["faixa"] == f_tamanho]
        
    return temp_df
