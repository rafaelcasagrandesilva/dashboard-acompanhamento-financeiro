import streamlit as st
import pandas as pd
from datetime import datetime
import os
import base64

# ================= PAGE CONFIG =================
st.set_page_config(
    page_title="Acompanhamento Financeiro – Diretoria",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ================= URLS GOOGLE SHEETS =================
URL_CONSOLIDADO = "https://docs.google.com/spreadsheets/d/e/2PACX-1vTch1qnnBn5iAKZ1koi_yHZDgLDs_JxRpXpr7VrnS5KMXDYHyzFX1ZRrEcyLRZ2J5K3y8DpIuUexAF6/pub?gid=1960898209&single=true&output=csv"
URL_PROJETOS = "https://docs.google.com/spreadsheets/d/e/2PACX-1vTch1qnnBn5iAKZ1koi_yHZDgLDs_JxRpXpr7VrnS5KMXDYHyzFX1ZRrEcyLRZ2J5K3y8DpIuUexAF6/pub?gid=116543323&single=true&output=csv"

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def get_base64_of_bin_file(path):
    if os.path.exists(path):
        try:
            with open(path, "rb") as f:
                return base64.b64encode(f.read()).decode()
        except Exception:
            return ""
    return ""

def clean_columns(df):
    """Limpa e padroniza os nomes das colunas do DataFrame."""
    df.columns = (
        df.columns
        .str.strip()
        .str.lower()
        .str.replace("%", "percentual", regex=False)
        .str.replace("ç", "c", regex=False)
        .str.replace("ã", "a", regex=False)
        .str.replace("á", "a", regex=False)
        .str.replace("é", "e", regex=False)
        .str.replace("í", "i", regex=False)
        .str.replace("ó", "o", regex=False)
        .str.replace("ú", "u", regex=False)
        .str.replace(" ", "_", regex=False)
    )
    # Remove colunas fantasmas que o Google Sheets às vezes exporta
    df = df.loc[:, ~df.columns.str.contains('^unnamed')]
    return df

# ================= LOAD DATA =================
@st.cache_data(ttl=3600, show_spinner="Carregando dados...")
def load_consolidado():
    try:
        df = pd.read_csv(URL_CONSOLIDADO)
        df = clean_columns(df)
        
        # Converte colunas para numérico garantindo que não haverá erro de string
        for col in ["executado_acumulado", "meta_acumulado"]:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)

        # Considerar apenas linhas com execução real
        df_valid = df[df["executado_acumulado"] > 0]
        
        # Fallback se não houver execução
        linha = df_valid.iloc[-1] if not df_valid.empty else df.iloc[-1]

        meta = float(linha.get("meta_acumulado", 0)) * 1000
        executado = float(linha.get("executado_acumulado", 0)) * 1000
        percentual = (executado / meta * 100) if meta > 0 else 0
        diferenca = executado - meta

        return {
            "meta_acumulado": meta,
            "executado_acumulado": executado,
            "percentual_execucao": percentual,
            "diferenca_meta": diferenca,
            "data_referencia": linha.get("data", "N/A")
        }
    except Exception as e:
        st.error(f"Erro ao carregar consolidado: {e}")
        return None

@st.cache_data(ttl=3600, show_spinner="Carregando projetos...")
def load_projetos():
    try:
        df = pd.read_csv(URL_PROJETOS)
        df = clean_columns(df)
        
        # Converte colunas para numérico
        for col in ["executado_acumulado", "meta_acumulado", "executado"]:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)

        projetos = {}
        if "projeto" not in df.columns:
            return {}

        for projeto in df["projeto"].unique():
            if pd.isna(projeto): continue
            
            df_p = df[df["projeto"] == projeto].copy()
            df_p["data"] = pd.to_datetime(df_p["data"], format="%d/%m/%Y", errors="coerce")
            df_p = df_p.dropna(subset=["data"])

            hoje = datetime.now()

            # Linha de referência até hoje
            df_ref = df_p[df_p["data"] <= hoje].sort_values("data")
            
            if df_ref.empty:
                linha_ref = df_p.sort_values("data").iloc[0]
            else:
                linha_ref = df_ref.iloc[-1]

            # Última data com lançamento real
            df_valid = df_p[
                (df_p["data"] <= hoje) &
                (df_p["executado"] > 0)
            ]

            ultima_data = (
                df_valid["data"].max().strftime("%d/%m/%Y")
                if not df_valid.empty
                else linha_ref["data"].strftime("%d/%m/%Y")
            )

            meta = float(linha_ref.get("meta_acumulado", 0)) * 1000
            executado = float(linha_ref.get("executado_acumulado", 0)) * 1000
            percentual = (executado / meta * 100) if meta > 0 else 0
            diferenca = executado - meta

            projetos[projeto] = {
                "meta_acumulado": meta,
                "executado_acumulado": executado,
                "percentual_execucao": percentual,
                "diferenca_meta": diferenca,
                "ultima_data_lancamento": ultima_data
            }
        return projetos
    except Exception as e:
        st.error(f"Erro ao carregar projetos: {e}")
        return {}

# Chamada das funções de carga
consolidado = load_consolidado()
projetos = load_projetos()

# ================= CSS PREMIUM =================
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');

:root {
  --green: #16a34a;
  --yellow: #f59e0b;
  --red: #b91c1c;
  --blue-main: #1E3A8A;
  --muted: #64748b;
  --bg-gradient: linear-gradient(180deg, #f5f7fb 0%, #eef2ff 100%);
  --surface-border: rgba(255,255,255,0.35);
}

html, body, [data-testid="stAppViewContainer"] {
  background: var(--bg-gradient) !important;
  font-family: Inter, sans-serif;
  color: #020617;
}

.block-container {
    padding-top: 5rem !important; 
    padding-bottom: 2rem !important;
    max-width: 1300px;
}

.card {
  background: linear-gradient(
    180deg,
    rgba(255,255,255,0.85),
    rgba(255,255,255,0.7)
  );
  backdrop-filter: blur(14px);
  border-radius: 20px;
  padding: 24px;
  border: 1px solid var(--surface-border);
  box-shadow: 0 10px 25px rgba(0,0,0,0.05);
  margin-bottom: 24px;
  transition: transform 0.3s ease;
  width: 100%;
}

.card:hover {
  transform: translateY(-5px);
  box-shadow: 0 15px 35px rgba(0,0,0,0.1);
}

.card-title {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 16px;
  text-transform: uppercase;
  color: var(--blue-main);
  font-weight: 800;
  letter-spacing: 0.1em;
  margin-bottom: 15px;
}

.card-date {
  font-size: 10px;
  font-weight: 600;
  color: var(--muted);
}

.kpis {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 15px;
}

.kpi-item {
  display: flex;
  flex-direction: column;
}

.kpi-label {
  font-size: 10px;
  color: #94a3b8;
  font-weight: 600;
  text-transform: uppercase;
  margin-bottom: 4px;
}

.kpi-value {
  font-size: 20px;
  font-weight: 700;
  color: #1e293b;
}

.kpi-sub {
  font-size: 16px;
  font-weight: 700;
}

.progress-container {
  margin-top: 20px;
  height: 8px;
  background: #e2e8f0;
  border-radius: 10px;
  overflow: hidden;
}

.progress-bar {
  height: 100%;
  border-radius: 10px;
}

.fixed-header {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  z-index: 1000;
  background: rgba(255,255,255,0.9);
  backdrop-filter: blur(10px);
  border-bottom: 1px solid #e2e8f0;
  padding: 10px 0;
}

.fixed-header-inner {
  max-width: 1300px;
  margin: 0 auto;
  padding: 0 20px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.header-left {
  display:flex;
  align-items:center;
  gap:12px;
}

.logo {
  height:35px;
}

.company {
  font-size:20px;
  font-weight:800;
  color:var(--blue-main);
}

.updated {
  font-size:11px;
  color:var(--muted);
}

header[data-testid="stHeader"] {
    display: none;
}

.section h2 {
  font-size: 24px;
  font-weight: 800;
  color: var(--blue-main);
  margin-bottom: 4px;
}

.section-subtitle {
  font-size: 13px;
  color: var(--muted);
  margin-bottom: 20px;
}

div.stButton > button {
  background: white !important;
  color: var(--blue-main) !important;
  border: 1px solid #e2e8f0 !important;
  border-radius: 8px !important;
  font-weight: 600 !important;
}
</style>
""", unsafe_allow_html=True)

# ================= HEADER =================
logo_base64 = get_base64_of_bin_file(os.path.join(BASE_DIR, "logo.png"))

st.markdown(f"""
<div class="fixed-header">
  <div class="fixed-header-inner">
    <div class="header-left">
      {"<img src='data:image/png;base64," + logo_base64 + "' class='logo'>" if logo_base64 else ""}
      <div class="company">M&E Engenharia</div>
    </div>
    <div class="updated">
      Atualizado em {datetime.now().strftime('%d/%m/%Y %H:%M')}
    </div>
  </div>
</div>
""", unsafe_allow_html=True)

# ================= CARD COMPONENT =================
def fmt_brl(valor):
    try:
        return f"R$ {valor:,.0f}".replace(",", "X").replace(".", ",").replace("X", ".")
    except Exception:
        return "R$ 0"

def render_card(titulo, meta, executado, percentual, diferenca, data_ref):
    if percentual >= 100:
        color = "var(--green)"
        arrow = "▲"
    elif percentual < 70:
        color = "var(--red)"
        arrow = "▼"
    else:
        color = "var(--yellow)"
        arrow = "▲" if diferenca >= 0 else "▼"

    st.markdown(f"""
    <div class="card" style="border-left: 6px solid {color}">
        <div class="card-title">
            {titulo}
            <span class="card-date">Ref: {data_ref}</span>
        </div>
        <div class="kpis">
            <div class="kpi-item">
                <div class="kpi-label">Meta Acumulada</div>
                <div class="kpi-value">{fmt_brl(meta)}</div>
            </div>
            <div class="kpi-item">
                <div class="kpi-label">Executado</div>
                <div class="kpi-value">{fmt_brl(executado)}</div>
            </div>
            <div class="kpi-item">
                <div class="kpi-label">% Execução</div>
                <div class="kpi-value">{percentual:.1f}%</div>
            </div>
            <div class="kpi-item">
                <div class="kpi-label">Diferença</div>
                <div class="kpi-sub" style="color:{color}">{arrow} {fmt_brl(abs(diferenca))}</div>
            </div>
        </div>
        <div class="progress-container">
            <div class="progress-bar" style="width:{min(percentual, 100)}%; background:{color}"></div>
        </div>
    </div>
    """, unsafe_allow_html=True)

# ================= CONTROLE =================
c1, c2 = st.columns([1,5])
with c1:
    if st.button("🔄 Atualizar"):
        st.cache_data.clear()
        st.rerun()
with c2:
    st.caption("Dados sincronizados com Google Sheets")

# ================= CONSOLIDADO =================
if consolidado:
    st.markdown('<div class="section"><h2>Consolidado</h2><p class="section-subtitle">Visão geral da diretoria</p></div>', unsafe_allow_html=True)
    render_card(
        "Geral",
        consolidado["meta_acumulado"],
        consolidado["executado_acumulado"],
        consolidado["percentual_execucao"],
        consolidado["diferenca_meta"],
        consolidado["data_referencia"]
    )

# ================= PROJETOS =================
if projetos:
    st.markdown('<div class="section"><h2>Projetos</h2><p class="section-subtitle">Acompanhamento individual</p></div>', unsafe_allow_html=True)
    cols = st.columns(2)
    for i, (nome, p) in enumerate(projetos.items()):
        with cols[i % 2]:
            render_card(
                nome.title(),
                p["meta_acumulado"],
                p["executado_acumulado"],
                p["percentual_execucao"],
                p["diferenca_meta"],
                p["ultima_data_lancamento"]
            )
else:
    st.warning("Nenhum projeto encontrado ou erro no carregamento.")

# ================= FOOTER =================
st.markdown(
    '<div style="text-align:center;color:#9CA3AF;font-size:0.8rem;margin-top:3rem;padding-bottom:2rem;">M&E Engenharia • 2026</div>',
    unsafe_allow_html=True
)