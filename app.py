import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import numpy as np

# =========================
# CONFIGURAÇÃO DA PÁGINA
# =========================
st.set_page_config(
    page_title="Dashboard Financeiro - Diretoria",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# =========================
# CACHE DE DADOS
# =========================
@st.cache_data(ttl=3600)
def load_data():
    URL_CONSOLIDADO = "https://docs.google.com/spreadsheets/d/e/2PACX-1vTch1qnnBn5iAKZ1koi_yHZDgLDs_JxRpXpr7VrnS5KMXDYHyzFX1ZRrEcyLRZ2J5K3y8DpIuUexAF6/pub?gid=1960898209&single=true&output=csv"
    URL_PROJETOS = "https://docs.google.com/spreadsheets/d/e/2PACX-1vTch1qnnBn5iAKZ1koi_yHZDgLDs_JxRpXpr7VrnS5KMXDYHyzFX1ZRrEcyLRZ2J5K3y8DpIuUexAF6/pub?gid=116543323&single=true&output=csv"

    df = pd.read_csv(URL_CONSOLIDADO)
    df_proj = pd.read_csv(URL_PROJETOS)

    df["Data"] = pd.to_datetime(df["Data"], dayfirst=True)
    df_proj["Data"] = pd.to_datetime(df_proj["Data"], dayfirst=True)

    cols_num = ["Meta", "Executado", "Meta acumulado", "Executado acumulado"]
    for c in cols_num:
        df[c] = df[c].astype(str).str.replace(",", ".", regex=False).astype(float) * 1000
        df_proj[c] = df_proj[c].astype(str).str.replace(",", ".", regex=False).astype(float) * 1000

    return df, df_proj


# =========================
# BOTÃO ATUALIZAR AGORA
# =========================
col_refresh, col_time = st.columns([1, 4])
with col_refresh:
    if st.button("🔄 Atualizar agora"):
        st.cache_data.clear()
        st.experimental_rerun()

with col_time:
    st.caption(f"Última atualização: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")

# =========================
# CARREGAMENTO
# =========================
df, df_proj = load_data()

st.success("Dados carregados com sucesso")

st.write("Próximo passo: migrar os KPIs e o visual.")