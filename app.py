import streamlit as st
import pandas as pd
from datetime import datetime
import os
import base64

# ================= PAGE CONFIG =================
st.set_page_config(
    page_title="Acompanhamento Financeiro – Diretoria",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ================= URLS GOOGLE SHEETS =================
URL_CONSOLIDADO = "https://docs.google.com/spreadsheets/d/e/2PACX-1vTch1qnnBn5iAKZ1koi_yHZDgLDs_JxRpXpr7VrnS5KMXDYHyzFX1ZRrEcyLRZ2J5K3y8DpIuUexAF6/pub?gid=1960898209&single=true&output=csv"
URL_PROJETOS = "https://docs.google.com/spreadsheets/d/e/2PACX-1vTch1qnnBn5iAKZ1koi_yHZDgLDs_JxRpXpr7VrnS5KMXDYHyzFX1ZRrEcyLRZ2J5K3y8DpIuUexAF6/pub?gid=116543323&single=true&output=csv"

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def get_base64_of_bin_file(path):
    if os.path.exists(path):
        with open(path, "rb") as f:
            return base64.b64encode(f.read()).decode()
    return ""

# ================= LOAD DATA =================
@st.cache_data(ttl=3600, show_spinner=False)
def load_consolidado():
    df = pd.read_csv(URL_CONSOLIDADO)
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

    # considerar apenas linhas com execução real
    df_valid = df[df["executado_acumulado"] > 0]

    # fallback se não houver execução
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
        "data_referencia": linha.get("data", "")
    }

@st.cache_data(ttl=3600, show_spinner=False)
def load_projetos():
    df = pd.read_csv(URL_PROJETOS)
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
    projetos = {}
    for projeto in df["projeto"].unique():
        df_p = df[df["projeto"] == projeto].copy()

        df_p["data"] = pd.to_datetime(df_p["data"], format="%d/%m/%Y", errors="coerce")
        df_p = df_p.dropna(subset=["data"])

        hoje = datetime.now()

        # linha de referência SEMPRE até hoje (para cálculos)
        df_ref = df_p[df_p["data"] <= hoje].sort_values("data")
        linha_ref = df_ref.iloc[-1]

        # última data com lançamento real (para exibição)
        df_valid = df_p[
            (df_p["data"] <= hoje) &
            (df_p["executado"].notna())
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

        projetos[projeto.lower().replace(" ", "_")] = {
            "meta_acumulado": meta,
            "executado_acumulado": executado,
            "percentual_execucao": percentual,
            "diferenca_meta": diferenca,
            "ultima_data_lancamento": ultima_data
        }
    return projetos

consolidado = load_consolidado()
projetos = load_projetos()

# ================= CSS PREMIUM (INALTERADO) =================
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
    padding-top: 3rem !important; 
    padding-bottom: 2rem !important;
    max-width: 1300px;
}

.card {
  background: linear-gradient(
    180deg,
    rgba(255,255,255,0.75),
    rgba(255,255,255,0.6)
  );
  backdrop-filter: blur(14px);
  border-radius: 20px;
  padding: 18px 32px;
  border: 1px solid var(--surface-border);
  box-shadow:
    0 1px 2px rgba(0,0,0,0.04),
    0 12px 32px rgba(0,0,0,0.10);
  margin-bottom: 24px; /* Reduzido levemente para o grid */
  transition: transform 0.35s ease, box-shadow 0.35s ease;
  width: 100%;
}

.card:hover {
  transform: translateY(-6px);
  box-shadow:
    0 6px 20px rgba(0,0,0,0.08),
    0 24px 48px rgba(0,0,0,0.16);
}

.card-title {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 18px;
  text-transform: uppercase;
  color: var(--blue-main);
  font-weight: 800;
  letter-spacing: 0.12em;
}

.card-date {
  font-size: 11px;
  font-weight: 600;
  color: var(--muted);
  letter-spacing: 0.04em;
}

.kpis {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); /* Ajustado para colunas menores */
  gap: 20px;
  margin-top: 22px;
}

.kpi-label {
  font-size: 11px;
  color: #94a3b8;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.04em;
}

.kpi-value {
  font-size: 24px; /* Reduzido levemente para caber melhor em 2 colunas */
  font-weight: 500;
  color: #020617;
  letter-spacing: -0.3px; 
}

.kpi-sub {
  font-size: 18px; /* Reduzido levemente */
  margin-top: 6px;
  font-weight: 600;
}
            
.progress {
  margin-top: 30px;
  height: 8px;
  background: linear-gradient(
    180deg,
    rgba(226,232,240,0.9),
    rgba(203,213,225,0.9)
  );
  border-radius: 999px;
  overflow: hidden;
}

.progress-bar {
  height: 100%;
  border-radius: 999px;
  transition: width 0.6s ease;
}

.fixed-header {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  z-index: 999;
  background: rgba(255,255,255,0.85);
  backdrop-filter: blur(10px);
  border-bottom: 1px solid rgba(226,232,240,0.9);
  box-shadow: 0 8px 30px rgba(0,0,0,0.08);
}

.fixed-header-inner {
  max-width: 2000px;
  margin: 0 auto;
  padding: 5px 24px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.header-left {
  display:flex;
  align-items:center;
  gap:14px;
}

.logo {
  height:45px;
  width: auto;
}

.company {
  font-size:26px;
  font-weight:800;
  color:var(--blue-main);
  letter-spacing:-0.6px;
}

.updated {
  font-size:12px;
  color:var(--muted);
}

header[data-testid="stHeader"] {
    display: none;
}
            
.section h2 {
  font-size: 30px;
  font-weight: 800;
  color: var(--blue-main);
  letter-spacing: -0.8px;
  margin-bottom: 6px;
}

.section-subtitle {
  font-size: 14px;
  color: var(--muted);
  margin-bottom: 24px;
}

/* Ajuste para remover margens do Streamlit entre os cards */
[data-testid="column"] {
    width: 100% !important;
}
            
/* ===== BOTÃO STREAMLIT CLARO (FORÇADO) ===== */
div.stButton > button {
  background: linear-gradient(180deg, #ffffff, #f1f5f9) !important;
  color: #1E3A8A !important;
  border: 1px solid #c7d2fe !important;
  border-radius: 999px !important;
  padding: 8px 16px !important;
  font-weight: 600 !important;
  box-shadow: 0 4px 12px rgba(0,0,0,0.08) !important;
  transition: all 0.25s ease;
}

div.stButton > button:hover {
  background: #eef2ff !important;
  border-color: #3b82f6 !important;
  transform: translateY(-1px);
}

div.stButton > button:active {
  transform: translateY(0);
  box-shadow: 0 2px 6px rgba(0,0,0,0.12) !important;
}
</style>
""", unsafe_allow_html=True)


# ================= HEADER =================
logo_base64 = get_base64_of_bin_file(os.path.join(BASE_DIR, "logo.png"))

st.markdown(f"""
<div class="fixed-header">
  <div class="fixed-header-inner">
    <div class="header-left">
      <img src="data:image/png;base64,{logo_base64}" class="logo">
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

def card_kpi(titulo, meta, executado, percentual, diferenca, data_ref):
    if percentual >= 100:
        color = "var(--green)"
        arrow = "▲"
    elif percentual < 70:
        color = "var(--red)"
        arrow = "▼"
    else:
        color = "var(--yellow)"
        arrow = "▲" if diferenca >= 0 else "▼"

    return f"""
    <div class="card" style="border-left:6px solid {color};">
      <div class="card-title">
        {titulo}
        <span class="card-date">Último lançamento: {data_ref}</span>
      </div>

      <div class="kpis">
        <div><div class="kpi-label">Meta acumulada</div><div class="kpi-value">{fmt_brl(meta)}</div></div>
        <div><div class="kpi-label">Executado</div><div class="kpi-value">{fmt_brl(executado)}</div></div>
        <div><div class="kpi-label">% Execução</div><div class="kpi-value">{percentual:.1f}%</div></div>
        <div><div class="kpi-label">Diferença</div><div class="kpi-sub" style="color:{color};">{arrow} {fmt_brl(abs(diferenca))}</div></div>
      </div>

      <div class="progress">
        <div class="progress-bar" style="width:{min(percentual,100)}%; background:{color};"></div>
      </div>
    </div>
    """

# ================= CONTROLE =================
c1, c2 = st.columns([1,5])
with c1:
    if st.button("🔄 Atualizar agora"):
        load_consolidado.clear()
        load_projetos.clear()
        st.rerun()
with c2:
    st.caption("Atualização automática a cada 1 hora")

# ================= CONSOLIDADO =================
st.markdown("""
<div class="section">
  <h2>Consolidado</h2>
  <p class="section-subtitle">Visão geral de todas as metas</p>
</div>
""", unsafe_allow_html=True)

st.markdown(card_kpi(
    "Consolidado Geral",
    consolidado["meta_acumulado"],
    consolidado["executado_acumulado"],
    consolidado["percentual_execucao"],
    consolidado["diferenca_meta"],
    consolidado["data_referencia"]
), unsafe_allow_html=True)

# ================= PROJETOS 2x2 =================
st.markdown("""
<div class="section">
  <h2>Projetos</h2>
  <p class="section-subtitle">Acompanhamento por projeto</p>
</div>
""", unsafe_allow_html=True)

col1, col2 = st.columns(2, gap="medium")
lista = list(projetos.items())

for i, (nome, p) in enumerate(lista):
    with col1 if i % 2 == 0 else col2:
        st.markdown(card_kpi(
            nome.replace("_"," ").title(),
            p["meta_acumulado"],
            p["executado_acumulado"],
            p["percentual_execucao"],
            p["diferenca_meta"],
            p["ultima_data_lancamento"]
        ), unsafe_allow_html=True)

# ================= FOOTER =================
st.markdown(
    '<div style="text-align:center;color:#9CA3AF;font-size:0.8rem;margin-top:3rem;">Desenvolvido por Casagrande para M&E Engenharia • 2026</div>',
    unsafe_allow_html=True
)
