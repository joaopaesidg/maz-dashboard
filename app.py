import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import sys
import os

sys.path.insert(0, os.path.dirname(__file__))
from src.data_loader import load_data
from src.kpis import calcular_kpis, STATUS_CONCLUIDO

# ── Configuração da página ──────────────────────────────────────────
st.set_page_config(
    page_title="MAZ | Pagamentos",
    page_icon="🏛️",
    layout="wide"
)

# ── Carga de dados ──────────────────────────────────────────────────
@st.cache_data(ttl=300)
def get_data():
    return load_data("data/pagamentos_maz.xlsx")

try:
    df_compras, df_pagamentos = get_data()
except FileNotFoundError:
    st.error("❌ Planilha não encontrada! Certifique-se que o arquivo está em: data/pagamentos_maz.xlsx")
    st.stop()

kpis = calcular_kpis(df_compras, df_pagamentos)

# ── Cabeçalho ───────────────────────────────────────────────────────
st.title("🏛️ MAZ | Museu das Amazônias")
st.subheader("Painel de Acompanhamento de Pagamentos")
st.divider()

# ── Filtros na barra lateral ────────────────────────────────────────
st.sidebar.header("🔍 Filtros")

todos_fornecedores = sorted(df_pagamentos["Fornecedor"].dropna().unique().tolist())
fornecedores_sel = st.sidebar.multiselect("Fornecedor", options=todos_fornecedores)

todos_status = sorted(df_pagamentos["Status"].dropna().unique().tolist())
status_sel = st.sidebar.multiselect("Status", options=todos_status)

df_view = df_pagamentos.copy()
if fornecedores_sel:
    df_view = df_view[df_view["Fornecedor"].isin(fornecedores_sel)]
if status_sel:
    df_view = df_view[df_view["Status"].isin(status_sel)]

st.sidebar.divider()
st.sidebar.caption(f"📋 {len(df_pagamentos)} parcelas no total")

# ── KPI Cards — Linha 1 ─────────────────────────────────────────────
c1, c2, c3, c4 = st.columns(4)
c1.metric("💼 Orçamento Total", f"R$ {kpis['orcamento_total']:,.0f}".replace(",", "."))
c2.metric("✅ Total Pago", f"R$ {kpis['total_pago']:,.0f}".replace(",", "."))
c3.metric("🔄 Em Andamento", f"R$ {kpis['total_andamento']:,.0f}".replace(",", "."))
c4.metric("💰 Saldo Disponível", f"R$ {kpis['saldo_disponivel']:,.0f}".replace(",", "."),
          delta=f"{kpis['perc_executado']:.1f}% executado")

st.divider()

# ── KPI Cards — Linha 2 ─────────────────────────────────────────────
c5, c6, c7, c8 = st.columns(4)
c5.metric("📊 % Executado", f"{kpis['perc_executado']:.1f}%")
c6.metric("⚠️ Vencem em 30 dias", kpis['contratos_vencendo'])
c7.metric("🔴 Contratos Vencidos", kpis['contratos_vencidos'])
c8.metric("📋 Parcelas Pendentes", kpis['parcelas_pendentes'])

st.divider()

# ── Gráficos — Linha 1 ──────────────────────────────────────────────
col_esq, col_dir = st.columns([3, 2])

with col_esq:
    st.subheader("📊 Gargalos por Status (R$)")
    df_status = df_view.groupby("Status")["Valor"].sum().reset_index()
    df_status = df_status.sort_values("Valor", ascending=True)

    mapa_cores = {
        "Pago": "#2ecc71",
        "Contrato/Template quitado": "#27ae60",
        "Aprovado": "#3498db",
        "Em aprovação": "#f1c40f",
        "NF em análise": "#f39c12",
        "Aguardando emissão de NF/DANFE": "#e67e22",
        "Aguardando Requisição de Pagamento": "#e67e22",
        "Aguardando informações": "#e67e22",
        "Atendimento Compras/Financeiro": "#e74c3c",
        "Contrato/Template em aberto": "#c0392b",
        "Contrato/Template vencido": "#922b21",
    }

    fig1 = px.bar(
        df_status, x="Valor", y="Status", orientation="h",
        text=df_status["Valor"].apply(lambda v: f"R$ {v:,.0f}".replace(",", ".")),
        color="Status", color_discrete_map=mapa_cores,
    )
    fig1.update_traces(textposition="outside")
    fig1.update_layout(showlegend=False, height=420)
    st.plotly_chart(fig1, use_container_width=True)

with col_dir:
    st.subheader("🥧 Execução Orçamentária")
    fig2 = go.Figure(go.Pie(
        labels=["Pago", "Em Andamento", "Saldo Disponível"],
        values=[max(kpis["total_pago"], 0), max(kpis["total_andamento"], 0), max(kpis["saldo_disponivel"], 0)],
        hole=0.45,
        marker_colors=["#2ecc71", "#f39c12", "#95a5a6"],
        textinfo="label+percent",
    ))
    fig2.update_layout(height=420)
    st.plotly_chart(fig2, use_container_width=True)

# ── Gráfico — Linha 2 ───────────────────────────────────────────────
st.subheader("🏢 Volume por Fornecedor")
df_forn = df_view.groupby("Fornecedor")["Valor"].sum().reset_index()
df_forn = df_forn.sort_values("Valor", ascending=False).head(15)
fig3 = px.bar(
    df_forn, x="Fornecedor", y="Valor",
    text=df_forn["Valor"].apply(lambda v: f"R$ {v:,.0f}".replace(",", ".")),
    color="Valor", color_continuous_scale="Blues",
)
fig3.update_traces(textposition="outside")
fig3.update_layout(showlegend=False, height=380)
st.plotly_chart(fig3, use_container_width=True)

st.divider()

# ── Tabela Detalhada ────────────────────────────────────────────────
st.subheader("📋 Detalhamento de Parcelas")

def highlight_status(row):
    cores = {
        "Pago": "background-color: #d5f5e3",
        "Contrato/Template quitado": "background-color: #d5f5e3",
        "Contrato/Template vencido": "background-color: #fadbd8",
        "Em aprovação": "background-color: #fef9e7",
        "Aguardando emissão de NF/DANFE": "background-color: #fdebd0",
    }
    cor = cores.get(row["Status"], "")
    return [cor] * len(row)

colunas = ["Fornecedor", "Descritivo", "Valor", "Status", "Data pgto", "Doc Fiscal", "Dias vencimento", "Observações"]
colunas_existentes = [c for c in colunas if c in df_view.columns]
st.dataframe(
    df_view[colunas_existentes].style.apply(highlight_status, axis=1),
    use_container_width=True, height=400,
)

st.divider()
st.caption("IDG — Instituto de Desenvolvimento e Gestão | MAZ | Museu das Amazônias")
