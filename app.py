
from pathlib import Path

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

# ==========================================================
# SKU PROFITABILITY INTELLIGENCE
# ==========================================================

ROOT = Path(__file__).resolve().parent
DATA_DIR = ROOT / "data"

BG = "#F3F6FA"
WHITE = "#FFFFFF"
NAVY = "#14263D"
TEXT = "#172B42"
MUTED = "#526579"
BLUE = "#3979A8"
GREEN = "#16805D"
GREEN_BG = "#E4F5EC"
RED = "#C83E4D"
RED_BG = "#FCE8EA"
AMBER = "#A66B08"
AMBER_BG = "#FFF3D6"
BORDER = "#D8E2ED"
TABLE_HEADER = "#E8F0F8"
TABLE_ALT = "#F1F4F8"

st.set_page_config(
    page_title="SKU Profitability Intelligence",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ==========================================================
# ESTILO VISUAL GLOBAL
# ==========================================================

st.markdown(
    f"""
    <style>
    :root {{ color-scheme: light; }}
    html, body, .stApp,
    [data-testid="stAppViewContainer"],
    [data-testid="stMain"],
    [data-testid="stMainBlockContainer"] {{
        background-color: {BG} !important;
        color: {TEXT} !important;
    }}
    .block-container {{
        padding-top: 1.35rem;
        padding-bottom: 2.5rem;
        max-width: 100%;
    }}
    [data-testid="stSidebar"] {{
        background-color: {NAVY} !important;
        border-right: 1px solid #243B54;
    }}
    [data-testid="stSidebar"] * {{ color: #FFFFFF; }}
    [data-testid="stSidebar"] input,
    [data-testid="stSidebar"] textarea {{
        color: {TEXT} !important;
        background-color: #FFFFFF !important;
        border-radius: 8px !important;
    }}
    [data-testid="stSidebar"] [data-baseweb="select"] > div {{
        background-color: #FFFFFF !important;
    }}
    [data-testid="stSidebar"] [data-baseweb="select"] * {{
        color: {TEXT} !important;
    }}
    [data-testid="stSidebar"] [data-baseweb="tag"] {{
        background-color: #EAF0F6 !important;
    }}
    h1, h2, h3, h4, p, label {{ color: {TEXT}; }}
    [data-testid="stMarkdownContainer"] {{ color: {TEXT}; }}
    [data-testid="stCaptionContainer"],
    [data-testid="stCaptionContainer"] p {{
        color: {MUTED} !important;
    }}
    .hero {{
        background: linear-gradient(115deg, {NAVY}, #285675);
        color: #FFFFFF;
        padding: 25px 28px;
        border-radius: 14px;
        margin-bottom: 18px;
        box-shadow: 0 4px 16px rgba(20,38,61,.08);
    }}
    .hero h1 {{
        color: #FFFFFF !important;
        font-size: 28px;
        font-weight: 700;
        margin: 0;
    }}
    .hero p {{
        color: #E6EEF6 !important;
        margin: 7px 0 0;
        font-size: 14px;
    }}
    div[data-testid="stMetric"] {{
        background-color: {WHITE} !important;
        border: 1px solid {BORDER} !important;
        border-radius: 12px !important;
        padding: 14px 16px !important;
        min-height: 105px;
        box-shadow: 0 2px 8px rgba(20,38,61,.035);
    }}
    [data-testid="stMetricLabel"],
    [data-testid="stMetricLabel"] * {{
        color: {MUTED} !important;
        font-size: .84rem !important;
    }}
    [data-testid="stMetricValue"],
    [data-testid="stMetricValue"] * {{
        color: {TEXT} !important;
        font-size: 1.35rem !important;
    }}
    [data-testid="stMetricDelta"] {{ font-size: .78rem !important; }}
    [data-testid="stDataFrame"] {{
        background: {WHITE} !important;
        border: 1px solid {BORDER} !important;
        border-radius: 10px !important;
        overflow: hidden !important;
        box-shadow: 0 2px 8px rgba(20,38,61,.035);
    }}
    [data-testid="stDataFrame"] > div {{
        background: {WHITE} !important;
        border-radius: 10px !important;
    }}
    [data-testid="stDataFrame"] canvas {{ border-radius: 8px; }}
    .stApp table {{
        width: 100% !important;
        background-color: {WHITE} !important;
        color: {TEXT} !important;
        border-collapse: collapse !important;
        border: 1px solid {BORDER} !important;
    }}
    .stApp table thead tr th {{
        background-color: {TABLE_HEADER} !important;
        color: {NAVY} !important;
        border: 1px solid {BORDER} !important;
        font-weight: 600 !important;
    }}
    .stApp table tbody tr td,
    .stApp table tbody tr th {{
        color: {TEXT} !important;
        background-color: {WHITE} !important;
        border: 1px solid {BORDER} !important;
    }}
    .stApp table tbody tr:nth-child(even) td,
    .stApp table tbody tr:nth-child(even) th {{
        background-color: {TABLE_ALT} !important;
    }}
    .stApp table th *, .stApp table td * {{
        color: inherit !important;
        background-color: transparent !important;
    }}
    [data-testid="stTable"],
    [data-testid="stTable"] > div {{
        background-color: {WHITE} !important;
    }}
    .stButton > button, .stDownloadButton > button,
    [data-testid="stDownloadButton"] button {{
        background-color: {WHITE} !important;
        color: {NAVY} !important;
        border: 1px solid {BORDER} !important;
        border-radius: 9px !important;
        font-weight: 600 !important;
        min-height: 40px;
        padding: .45rem 1rem;
        box-shadow: none !important;
    }}
    .stButton > button *, .stDownloadButton > button *,
    [data-testid="stDownloadButton"] button * {{
        color: {NAVY} !important;
        fill: {NAVY} !important;
    }}
    .stButton > button:hover, .stDownloadButton > button:hover,
    [data-testid="stDownloadButton"] button:hover {{
        background-color: {TABLE_HEADER} !important;
        border-color: #B7C9DB !important;
    }}
    .stButton > button:focus, .stDownloadButton > button:focus {{
        outline: 2px solid #8DB8D8 !important;
        outline-offset: 2px;
    }}
    [data-testid="stMain"] input,
    [data-testid="stMain"] textarea {{
        color: {TEXT} !important;
        background-color: {WHITE} !important;
        border-color: {BORDER} !important;
        border-radius: 8px !important;
    }}
    [data-testid="stMain"] [data-baseweb="select"] > div {{
        background-color: {WHITE} !important;
        border-color: {BORDER} !important;
        border-radius: 8px !important;
    }}
    [data-testid="stMain"] [data-baseweb="select"] * {{
        color: {TEXT} !important;
    }}
    [data-testid="stMain"] [data-baseweb="tag"] {{
        background-color: #EAF0F6 !important;
        color: {TEXT} !important;
    }}
    [data-testid="stExpander"] {{
        background-color: {WHITE} !important;
        border: 1px solid {BORDER} !important;
        border-radius: 10px !important;
    }}
    [data-testid="stExpander"] details,
    [data-testid="stExpander"] summary {{
        background-color: {WHITE} !important;
    }}
    [data-testid="stAlert"] {{ border-radius: 10px !important; }}
    hr {{ border-color: {BORDER} !important; }}
    .insight {{
        background-color: {WHITE};
        border: 1px solid {BORDER};
        border-left: 4px solid {BLUE};
        padding: 15px 18px;
        border-radius: 9px;
        margin: 12px 0;
        color: {TEXT};
        box-shadow: 0 2px 8px rgba(20,38,61,.025);
    }}
    .insight b {{ color: {NAVY}; }}
    .small-note {{ color: {MUTED}; font-size: 12px; }}
    [data-testid="stMain"] [data-baseweb="input"],
    [data-testid="stMain"] [data-baseweb="textarea"] {{
        background-color: {WHITE} !important;
    }}
    [data-testid="stMain"] footer {{ background-color: {BG} !important; }}
    </style>
    """,
    unsafe_allow_html=True,
)

# ==========================================================
# FORMATAÇÃO BRASILEIRA
# ==========================================================

def is_missing(value):
    try:
        return bool(pd.isna(value))
    except (TypeError, ValueError):
        return False


def money(value):
    if is_missing(value):
        return "—"

    value = float(value)
    sign = "-" if value < 0 else ""
    value = abs(value)

    if value >= 1_000_000_000:
        formatted = f"{value / 1_000_000_000:,.2f} bi"
    elif value >= 1_000_000:
        formatted = f"{value / 1_000_000:,.2f} mi"
    else:
        formatted = f"{value:,.2f}"

    formatted = formatted.replace(",", "X").replace(".", ",").replace("X", ".")
    return f"{sign}R$ {formatted}"


def number(value):
    if is_missing(value):
        return "—"
    return f"{float(value):,.0f}".replace(",", ".")


def percent(value):
    if is_missing(value):
        return "—"
    return f"{float(value) * 100:,.1f}%".replace(",", "X").replace(".", ",").replace("X", ".")


def percentage_points(value):
    if is_missing(value):
        return "—"
    return f"{float(value):,.2f} p.p.".replace(",", "X").replace(".", ",").replace("X", ".")


def csv_bytes(data):
    return data.to_csv(
        index=False,
        sep=";",
        decimal=",",
        encoding="utf-8-sig",
    ).encode("utf-8-sig")


def download_csv(data, label, filename, key):
    st.download_button(
        label=f"⬇️  {label}",
        data=csv_bytes(data),
        file_name=filename,
        mime="text/csv",
        key=key,
        type="secondary",
    )


# ==========================================================
# FORMATAÇÃO AUTOMÁTICA DE TABELAS
# ==========================================================

MONEY_WORDS = (
    "receita", "lucro", "custo", "preço", "preco",
    "impacto", "efeito", "residual", "exposição", "exposicao", "gap receita",
    "gap lucro", "valor financeiro", "orçamento financeiro",
    "orcamento financeiro",
)

PERCENT_WORDS = (
    "margem", "recorrência", "recorrencia",
    "percentual", "percentagem", "desconto_pct",
    "desconto (%)", "taxa (%)", "(%)",
)

COUNT_WORDS = (
    "quantidade", "volume", "skus", "quantidade_skus",
    "registros", "duplicidades", "células vazias",
    "celulas vazias", "meses analisados",
)


def table_formatters(df):
    """Escolhe o formato visual com base no nome e no tipo de cada coluna."""
    formatters = {}

    for col in df.columns:
        name = str(col).strip().lower()

        if not pd.api.types.is_numeric_dtype(df[col]):
            continue

        if any(word in name for word in PERCENT_WORDS):
            # Colunas de margem já armazenadas como proporção.
            if "margem_real" in name or "margem_orcada" in name:
                formatters[col] = lambda x: percent(x)
            elif "recorrencia_gap" in name:
                formatters[col] = lambda x: percent(x)
            else:
                # Desvio de margem em p.p. não é percentual relativo.
                if "p.p." in name or "pontos percentuais" in name:
                    formatters[col] = lambda x: percentage_points(x)
                elif "gap margem" in name or "desvio_margem_pp" in name:
                    formatters[col] = lambda x: percentage_points(x)
                else:
                    # Percentuais armazenados de 0 a 100.
                    formatters[col] = lambda x: (
                        "—" if is_missing(x)
                        else f"{float(x):,.1f}%".replace(",", "X").replace(".", ",").replace("X", ".")
                    )
            continue

        if any(word in name for word in MONEY_WORDS):
            formatters[col] = lambda x: money(x)
            continue

        if any(word in name for word in COUNT_WORDS):
            formatters[col] = lambda x: number(x)
            continue

    return formatters


def style_table(df):
    styler = df.style.set_properties(
        **{
            "background-color": WHITE,
            "color": TEXT,
            "border-color": BORDER,
        }
    )

    def zebra(data):
        mask = np.broadcast_to(
            (np.arange(len(data)) % 2 == 1)[:, None],
            data.shape,
        )
        styles = np.where(
            mask,
            f"background-color: {TABLE_ALT}; color: {TEXT};",
            "",
        )
        return pd.DataFrame(styles, index=data.index, columns=data.columns)

    styler = styler.apply(zebra, axis=None)

    if df.empty:
        return styler

    def style_column(series):
        col = str(series.name).lower()

        if "prioridade" in col or "status" in col:
            def status_color(value):
                value = str(value).lower()

                if "alta" in value or "crítico" in value or "critico" in value:
                    return f"background-color: {RED_BG}; color: #A52736; font-weight: 600;"
                if "média" in value or "media" in value or "investigar" in value:
                    return f"background-color: {AMBER_BG}; color: #855500; font-weight: 600;"
                if "monitorar" in value or "oportunidade" in value or "ok" in value:
                    return f"background-color: {GREEN_BG}; color: #126747; font-weight: 600;"
                return ""

            return series.map(status_color)

        if not pd.api.types.is_numeric_dtype(series):
            return pd.Series("", index=series.index)

        is_gap = any(
            word in col
            for word in ("desvio", "gap", "impacto", "exposição", "exposicao")
        )

        if is_gap:
            return series.map(
                lambda value: (
                    f"background-color: {RED_BG}; color: #A52736;"
                    if pd.notna(value) and value < 0
                    else (
                        f"background-color: {GREEN_BG}; color: #126747;"
                        if pd.notna(value) and value > 0
                        else ""
                    )
                )
            )

        return pd.Series("", index=series.index)

    relevant = [
        col for col in df.columns
        if pd.api.types.is_numeric_dtype(df[col])
        or any(word in str(col).lower() for word in ("prioridade", "status"))
    ]

    if relevant:
        styler = styler.apply(style_column, subset=relevant)

    # Formata os números na apresentação sem alterar os dados originais.
    formatters = table_formatters(df)
    if formatters:
        styler = styler.format(formatters, na_rep="—", thousands=".", decimal=",")

    return styler


def show_table(df, height=400, key=None, column_config=None):
    # Usa o Styler para exibir números formatados e preserva os dados originais.
    st.dataframe(
        style_table(df),
        width="stretch",
        height=height,
        hide_index=True,
        column_config=column_config or {},
        key=key,
    )


def money_config(columns):
    return {
        col: st.column_config.NumberColumn(
            col,
            format="R$ %.2f",
        )
        for col in columns
    }


def style_plot(fig, height=370, percent_axis=False, money_axis=False):
    fig.update_layout(
        height=height,
        paper_bgcolor=WHITE,
        plot_bgcolor=WHITE,
        font=dict(family="Arial, sans-serif", size=12, color=TEXT),
        title_font=dict(size=17, color=TEXT),
        margin=dict(l=15, r=15, t=55, b=15),
        legend_title_text="",
        hoverlabel=dict(bgcolor=WHITE, font_color=TEXT),
    )

    fig.update_xaxes(
        showgrid=False,
        zerolinecolor=BORDER,
        tickfont=dict(color=TEXT),
        title_font=dict(color=TEXT),
    )

    fig.update_yaxes(
        gridcolor="#E7ECF2",
        zerolinecolor=BORDER,
        tickfont=dict(color=TEXT),
        title_font=dict(color=TEXT),
    )

    if percent_axis:
        fig.update_yaxes(tickformat=".1%")
    if money_axis:
        fig.update_yaxes(tickprefix="R$ ", tickformat=",.2f")

    return fig


# ==========================================================
# CARREGAMENTO E VALIDAÇÃO DOS DADOS
# ==========================================================

@st.cache_data
def load_data():
    """Carrega o histórico completo ou recompõe a base a partir dos CSVs publicados."""
    path = DATA_DIR / "historico_skus.csv"

    # Localmente, prioriza o arquivo completo quando ele estiver disponível.
    if path.is_file():
        data = pd.read_csv(path, sep=";")
    else:
        # No Streamlit Cloud, usa as seis partes versionadas no GitHub.
        partes = [
            DATA_DIR / f"historico_skus_{i}.csv"
            for i in range(1, 7)
        ]
        ausentes = [parte.name for parte in partes if not parte.is_file()]

        if ausentes:
            raise FileNotFoundError(
                "Não foi possível localizar o histórico de SKUs. "
                "Arquivos ausentes na pasta data: " + ", ".join(ausentes)
            )

        # Cada arquivo é lido com seu cabeçalho e as linhas são reunidas.
        data = pd.concat(
            [pd.read_csv(parte, sep=";") for parte in partes],
            ignore_index=True,
        )

        # Se as partes tiverem sido divididas com o cabeçalho repetido,
        # remove eventuais linhas de cabeçalho que aparecerem como dados.
        if "mes" in data.columns:
            data = data[data["mes"].astype(str).str.strip().str.lower() != "mes"].copy()

    required = [
        "mes", "sku_id", "familia", "segmento",
        "receita_liquida_real", "receita_liquida_orcada",
        "lucro_bruto_real", "lucro_bruto_orcado",
        "quantidade_real", "quantidade_orcada",
        "custo_unitario_real", "custo_unitario_orcado",
        "preco_liquido_unitario", "preco_liquido_orcado_unitario",
        "custo_produtos_real", "custo_produtos_orcado",
    ]

    missing = [col for col in required if col not in data.columns]
    if missing:
        raise ValueError("Estão faltando colunas na base: " + ", ".join(missing))

    data["mes"] = pd.to_datetime(data["mes"], errors="coerce")

    text_cols = {"mes", "sku_id", "familia", "segmento", "cenario_simulado"}

    for col in data.columns:
        if col not in text_cols:
            data[col] = pd.to_numeric(data[col], errors="coerce")

    data = data.dropna(subset=["mes", "sku_id"]).copy()

    data["desvio_receita"] = (
        data["receita_liquida_real"] - data["receita_liquida_orcada"]
    )
    data["desvio_lucro"] = (
        data["lucro_bruto_real"] - data["lucro_bruto_orcado"]
    )

    data["margem_real_calc"] = np.where(
        data["receita_liquida_real"] != 0,
        data["lucro_bruto_real"] / data["receita_liquida_real"],
        np.nan,
    )
    data["margem_orcada_calc"] = np.where(
        data["receita_liquida_orcada"] != 0,
        data["lucro_bruto_orcado"] / data["receita_liquida_orcada"],
        np.nan,
    )
    data["desvio_margem_pp_calc"] = (
        data["margem_real_calc"] - data["margem_orcada_calc"]
    ) * 100

    if "desconto_pct" not in data.columns:
        data["desconto_pct"] = np.nan

    # Margem de contribuição: lucro bruto menos custos variáveis adicionais.
    # Não é margem líquida; despesas fixas, financeiras e impostos não estão
    # necessariamente representados nesta base sintética.
    if "custo_variavel_adicional_real" in data.columns:
        if "margem_contribuicao_real" not in data.columns:
            data["margem_contribuicao_real"] = (
                data["lucro_bruto_real"] - data["custo_variavel_adicional_real"]
            )
    if "custo_variavel_adicional_orcado" in data.columns:
        if "margem_contribuicao_orcada" not in data.columns:
            data["margem_contribuicao_orcada"] = (
                data["lucro_bruto_orcado"] - data["custo_variavel_adicional_orcado"]
            )

    if "margem_contribuicao_real" in data.columns:
        data["margem_contribuicao_real_pct_calc"] = np.where(
            data["receita_liquida_real"] != 0,
            data["margem_contribuicao_real"] / data["receita_liquida_real"],
            np.nan,
        )
    if "margem_contribuicao_orcada" in data.columns:
        data["margem_contribuicao_orcada_pct_calc"] = np.where(
            data["receita_liquida_orcada"] != 0,
            data["margem_contribuicao_orcada"] / data["receita_liquida_orcada"],
            np.nan,
        )

    return data

try:
    hist = load_data()
except Exception as exc:
    st.error("Não foi possível carregar os dados.")
    st.exception(exc)
    st.stop()


# ==========================================================
# FILTROS E NAVEGAÇÃO
# ==========================================================

min_month = hist["mes"].min().to_period("M").to_timestamp()
max_month = hist["mes"].max().to_period("M").to_timestamp()

pages = [
    "01 · Executive Overview",
    "02 · Performance & Trends",
    "03 · Profit Bridge",
    "04 · Portfolio Intelligence",
    "05 · SKU Investigation",
    "06 · Gap & Risk Diagnosis",
    "07 · Action Plan & Opportunities",
    "08 · Data Quality & Methodology",
    "09 · Pricing Lab",
    "10 · Rentabilidade & Descontos",
]

st.sidebar.title("SKU PROFITABILITY")
st.sidebar.caption("INTELLIGENCE & ANALYTICS")
st.sidebar.divider()

page = st.sidebar.radio("Navegação", pages)
st.sidebar.divider()
st.sidebar.subheader("Filtros")

period = st.sidebar.selectbox(
    "Período de análise",
    ["Últimos 6 meses", "Últimos 12 meses", "Histórico completo", "Escolher datas"],
)

if period == "Últimos 6 meses":
    start_date = max_month - pd.DateOffset(months=5)
    end_date = max_month
elif period == "Últimos 12 meses":
    start_date = max_month - pd.DateOffset(months=11)
    end_date = max_month
elif period == "Histórico completo":
    start_date, end_date = min_month, max_month
else:
    date_range = st.sidebar.date_input(
        "Intervalo",
        value=(min_month.date(), max_month.date()),
        min_value=min_month.date(),
        max_value=max_month.date(),
    )
    if isinstance(date_range, (tuple, list)) and len(date_range) == 2:
        start_date = pd.Timestamp(date_range[0])
        end_date = pd.Timestamp(date_range[1])
    else:
        start_date, end_date = min_month, max_month

family_list = sorted(hist["familia"].dropna().unique().tolist())
segment_list = sorted(hist["segmento"].dropna().unique().tolist())

families_selected = st.sidebar.multiselect(
    "Família de produto", family_list, default=family_list
)
segments_selected = st.sidebar.multiselect(
    "Segmento", segment_list, default=segment_list
)

filtered = hist[
    (hist["mes"] >= start_date)
    & (hist["mes"] <= end_date + pd.offsets.MonthEnd(0))
    & hist["familia"].isin(families_selected)
    & hist["segmento"].isin(segments_selected)
].copy()

if filtered.empty:
    st.warning(
        "Não há dados para essa combinação de filtros. "
        "Selecione outras famílias, segmentos ou datas."
    )
    st.stop()

period_text = (
    f"{filtered['mes'].min():%m/%Y} até {filtered['mes'].max():%m/%Y}"
)


# ==========================================================
# AGREGAÇÕES
# ==========================================================

def summarize(data, by=None):
    agg = {
        "receita_real": ("receita_liquida_real", "sum"),
        "receita_orcada": ("receita_liquida_orcada", "sum"),
        "lucro_real": ("lucro_bruto_real", "sum"),
        "lucro_orcado": ("lucro_bruto_orcado", "sum"),
        "volume_real": ("quantidade_real", "sum"),
        "volume_orcado": ("quantidade_orcada", "sum"),
        "custo_real": ("custo_produtos_real", "sum"),
        "custo_orcado": ("custo_produtos_orcado", "sum"),
        "skus": ("sku_id", "nunique"),
    }

    if by:
        out = data.groupby(by, dropna=False).agg(**agg).reset_index()
    else:
        out = pd.DataFrame([{
            "receita_real": data["receita_liquida_real"].sum(),
            "receita_orcada": data["receita_liquida_orcada"].sum(),
            "lucro_real": data["lucro_bruto_real"].sum(),
            "lucro_orcado": data["lucro_bruto_orcado"].sum(),
            "volume_real": data["quantidade_real"].sum(),
            "volume_orcado": data["quantidade_orcada"].sum(),
            "custo_real": data["custo_produtos_real"].sum(),
            "custo_orcado": data["custo_produtos_orcado"].sum(),
            "skus": data["sku_id"].nunique(),
        }])

    out["desvio_receita"] = out["receita_real"] - out["receita_orcada"]
    out["desvio_lucro"] = out["lucro_real"] - out["lucro_orcado"]
    out["margem_real"] = np.where(
        out["receita_real"] != 0,
        out["lucro_real"] / out["receita_real"],
        np.nan,
    )
    out["margem_orcada"] = np.where(
        out["receita_orcada"] != 0,
        out["lucro_orcado"] / out["receita_orcada"],
        np.nan,
    )
    out["desvio_margem_pp"] = (
        out["margem_real"] - out["margem_orcada"]
    ) * 100

    # Métricas de margem de contribuição só são exibidas quando a base contém
    # os componentes necessários para calculá-las.
    if {"margem_contribuicao_real", "margem_contribuicao_orcada"}.issubset(data.columns):
        if by:
            contribution = data.groupby(by, dropna=False).agg(
                mc_real=("margem_contribuicao_real", "sum"),
                mc_orcada=("margem_contribuicao_orcada", "sum"),
            ).reset_index()
            out = out.merge(contribution, on=by, how="left")
        else:
            out["mc_real"] = data["margem_contribuicao_real"].sum()
            out["mc_orcada"] = data["margem_contribuicao_orcada"].sum()

        out["margem_contribuicao_real_pct"] = np.where(
            out["receita_real"] != 0, out["mc_real"] / out["receita_real"], np.nan
        )
        out["margem_contribuicao_orcada_pct"] = np.where(
            out["receita_orcada"] != 0, out["mc_orcada"] / out["receita_orcada"], np.nan
        )
        out["desvio_margem_contribuicao_pp"] = (
            out["margem_contribuicao_real_pct"]
            - out["margem_contribuicao_orcada_pct"]
        ) * 100

    return out


total = summarize(filtered).iloc[0]
monthly = summarize(filtered, ["mes"]).sort_values("mes")
family_summary = summarize(filtered, ["familia"]).sort_values("desvio_lucro")
sku_summary = summarize(filtered, ["sku_id", "familia", "segmento"])

# Decomposição aritmética do desvio do lucro bruto por registro.
# Estes componentes ajudam a priorizar investigação, mas não provam causalidade.
filtered["efeito_preco"] = (
    (filtered["preco_liquido_unitario"] - filtered["preco_liquido_orcado_unitario"])
    * filtered["quantidade_real"]
)
filtered["efeito_volume"] = (
    (filtered["quantidade_real"] - filtered["quantidade_orcada"])
    * (filtered["preco_liquido_orcado_unitario"] - filtered["custo_unitario_orcado"])
)
filtered["efeito_custo"] = -(
    (filtered["custo_unitario_real"] - filtered["custo_unitario_orcado"])
    * filtered["quantidade_real"]
)
filtered["residual_decomposicao"] = (
    filtered["desvio_lucro"]
    - filtered["efeito_preco"]
    - filtered["efeito_volume"]
    - filtered["efeito_custo"]
)

sku_extra = filtered.groupby("sku_id", as_index=False).agg(
    preco_real=("preco_liquido_unitario", "mean"),
    preco_orcado=("preco_liquido_orcado_unitario", "mean"),
    custo_unit_real=("custo_unitario_real", "mean"),
    custo_unit_orcado=("custo_unitario_orcado", "mean"),
    desconto_medio=("desconto_pct", "mean"),
    meses_analisados=("mes", "nunique"),
    meses_com_gap=("desvio_lucro", lambda s: int((s < 0).sum())),
    efeito_preco=("efeito_preco", "sum"),
    efeito_volume=("efeito_volume", "sum"),
    efeito_custo=("efeito_custo", "sum"),
    residual_decomposicao=("residual_decomposicao", "sum"),
)

if {"margem_contribuicao_real", "margem_contribuicao_orcada"}.issubset(filtered.columns):
    mc_extra = filtered.groupby("sku_id", as_index=False).agg(
        margem_contribuicao_real=("margem_contribuicao_real", "sum"),
        margem_contribuicao_orcada=("margem_contribuicao_orcada", "sum"),
    )
    sku_extra = sku_extra.merge(mc_extra, on="sku_id", how="left")

sku_summary = sku_summary.merge(sku_extra, on="sku_id", how="left")
if {"margem_contribuicao_real", "margem_contribuicao_orcada"}.issubset(sku_summary.columns):
    sku_summary["margem_contribuicao_real_pct"] = np.where(
        sku_summary["receita_real"] != 0,
        sku_summary["margem_contribuicao_real"] / sku_summary["receita_real"],
        np.nan,
    )
    sku_summary["margem_contribuicao_orcada_pct"] = np.where(
        sku_summary["receita_orcada"] != 0,
        sku_summary["margem_contribuicao_orcada"] / sku_summary["receita_orcada"],
        np.nan,
    )
    sku_summary["desvio_margem_contribuicao_pp"] = (
        sku_summary["margem_contribuicao_real_pct"]
        - sku_summary["margem_contribuicao_orcada_pct"]
    ) * 100
sku_summary["recorrencia_gap"] = (
    sku_summary["meses_com_gap"]
    / sku_summary["meses_analisados"].replace(0, np.nan)
)

# Seleciona o componente negativo de maior magnitude como sinal inicial.
# O rótulo descreve uma hipótese de investigação, não uma causa confirmada.
component_cols = ["efeito_preco", "efeito_volume", "efeito_custo", "residual_decomposicao"]
component_labels = {
    "efeito_preco": "Sinal: pressão de preço (validar)",
    "efeito_volume": "Sinal: efeito de volume (validar)",
    "efeito_custo": "Sinal: aumento de custo (validar)",
    "residual_decomposicao": "Sinal: interações/outros fatores (validar)",
}
sku_summary["componente_mais_negativo"] = sku_summary[component_cols].idxmin(axis=1)
sku_summary["hipotese"] = sku_summary["componente_mais_negativo"].map(component_labels)
sku_summary.loc[
    sku_summary["desvio_lucro"] >= 0, "hipotese"
] = "Sem gap negativo: monitorar desempenho"

sku_summary["prioridade"] = np.select(
    [
        (sku_summary["desvio_lucro"] < 0)
        & (sku_summary["desvio_margem_pp"] <= -3),
        sku_summary["desvio_lucro"] < 0,
    ],
    ["Alta", "Média"],
    default="Monitorar / oportunidade",
)


# ==========================================================
# CABEÇALHO E EXPORTAÇÃO GERAL
# ==========================================================

st.markdown(
    f"""
    <div class="hero">
        <h1>SKU Profitability Intelligence</h1>
        <p>Rentabilidade, performance, diagnóstico e oportunidades</p>
        <p>Período: {period_text} | Base sintética de demonstração</p>
    </div>
    """,
    unsafe_allow_html=True,
)
st.caption(
    "Os dados são sintéticos. As hipóteses são sinais para investigação, "
    "não causas comprovadas."
)

with st.expander("⬇️ Exportar dados para análise"):
    st.write(
        "Baixe os registros que correspondem aos filtros atuais. "
        "O arquivo pode ser aberto no Excel ou importado em outra ferramenta."
    )
    download_csv(
        filtered,
        "Baixar dados filtrados em CSV",
        "historico_skus_filtrado.csv",
        "download_filtered_global",
    )


# ==========================================================
# COMPONENTES REUTILIZÁVEIS
# ==========================================================

def kpi_row():
    has_contribution = "mc_real" in total.index
    columns = st.columns(5 if has_contribution else 4)
    columns[0].metric(
        "Receita realizada",
        money(total["receita_real"]),
        f"{money(total['desvio_receita'])} vs. orçamento",
    )
    columns[1].metric(
        "Lucro bruto realizado",
        money(total["lucro_real"]),
        f"{money(total['desvio_lucro'])} vs. orçamento",
    )
    columns[2].metric(
        "Margem bruta realizada",
        percent(total["margem_real"]),
        percentage_points(total["desvio_margem_pp"]),
    )
    if has_contribution:
        columns[3].metric(
            "Margem de contribuição",
            percent(total["margem_contribuicao_real_pct"]),
            percentage_points(total["desvio_margem_contribuicao_pp"]),
            help="Lucro bruto menos custos variáveis adicionais presentes na base; não equivale à margem líquida.",
        )
        columns[4].metric(
            "SKUs analisados",
            number(total["skus"]),
            f"{filtered['mes'].nunique()} meses no recorte",
        )
    else:
        columns[3].metric(
            "SKUs analisados",
            number(total["skus"]),
            f"{filtered['mes'].nunique()} meses no recorte",
        )


def show_monthly(real_col, budget_col, title, percent_axis=False):
    data = monthly[["mes", real_col, budget_col]].melt(
        id_vars="mes",
        var_name="Série",
        value_name="Valor",
    )
    data["Série"] = data["Série"].map({
        real_col: "Realizado",
        budget_col: "Orçado",
    })

    fig = px.line(
        data,
        x="mes",
        y="Valor",
        color="Série",
        markers=True,
        title=title,
        color_discrete_map={
            "Realizado": BLUE,
            "Orçado": "#9AA8B8",
        },
    )

    if percent_axis:
        fig.update_yaxes(tickformat=".1%")
        fig.update_traces(
            hovertemplate="%{x|%m/%Y}<br>%{fullData.name}: %{y:.1%}<extra></extra>"
        )
    elif "volume" not in real_col.lower():
        fig.update_yaxes(tickprefix="R$ ", tickformat=",.2f")
        fig.update_traces(
            hovertemplate="%{x|%m/%Y}<br>%{fullData.name}: R$ %{y:,.2f}<extra></extra>"
        )
    else:
        fig.update_yaxes(tickformat=",.0f")
        fig.update_traces(
            hovertemplate="%{x|%m/%Y}<br>%{fullData.name}: %{y:,.0f}<extra></extra>"
        )

    st.plotly_chart(
        style_plot(fig, height=370, percent_axis=percent_axis),
        width="stretch",
    )


def show_sku_table(data, height=450, suffix="sku_table"):
    cols = [
        "sku_id", "familia", "segmento",
        "receita_real", "desvio_receita",
        "lucro_real", "lucro_orcado", "desvio_lucro",
        "margem_real", "margem_orcada",
        "desvio_margem_pp", "recorrencia_gap",
        "efeito_preco", "efeito_volume", "efeito_custo",
        "residual_decomposicao",
        "prioridade", "hipotese",
    ]

    view = data[[c for c in cols if c in data.columns]].copy()
    view = view.rename(columns={
        "sku_id": "SKU",
        "familia": "Família",
        "segmento": "Segmento",
        "receita_real": "Receita real (R$)",
        "desvio_receita": "Gap receita (R$)",
        "lucro_real": "Lucro real (R$)",
        "lucro_orcado": "Lucro orçado (R$)",
        "desvio_lucro": "Gap lucro (R$)",
        "margem_real": "Margem real",
        "margem_orcada": "Margem orçada",
        "desvio_margem_pp": "Gap margem (p.p.)",
        "recorrencia_gap": "Recorrência do gap",
        "efeito_preco": "Efeito preço (R$)",
        "efeito_volume": "Efeito volume (R$)",
        "efeito_custo": "Efeito custo (R$)",
        "residual_decomposicao": "Residual (R$)",
        "prioridade": "Prioridade",
        "hipotese": "Hipótese inicial",
    })

    # As colunas percentuais são convertidas para pontos percentuais
    # somente para exibição. Os valores financeiros continuam numéricos.
    for col in ["Margem real", "Margem orçada", "Recorrência do gap"]:
        if col in view.columns:
            view[col] = view[col] * 100

    config = {}
    for col in [
        "Receita real (R$)", "Gap receita (R$)",
        "Lucro real (R$)", "Lucro orçado (R$)", "Gap lucro (R$)",
    ]:
        if col in view.columns:
            config[col] = st.column_config.NumberColumn(
                col,
                format="R$ %,.2f",
            )

    for col in ["Margem real", "Margem orçada", "Recorrência do gap"]:
        if col in view.columns:
            config[col] = st.column_config.NumberColumn(
                col,
                format="%.1f%%",
            )

    if "Gap margem (p.p.)" in view.columns:
        config["Gap margem (p.p.)"] = st.column_config.NumberColumn(
            "Gap margem (p.p.)",
            format="%.2f",
        )

    show_table(view, height=height, key=suffix, column_config=config)
    download_csv(
        data,
        "Baixar esta tabela em CSV",
        f"{suffix}.csv",
        f"download_{suffix}",
    )


# ==========================================================
# 01 — EXECUTIVE OVERVIEW
# ==========================================================

if page == "01 · Executive Overview":
    kpi_row()
    left, right = st.columns([1.4, 1])

    with left:
        show_monthly(
            "receita_real", "receita_orcada",
            "Receita mensal: realizado x orçamento",
        )

    with right:
        st.subheader("Resumo do período")
        summary_cards = pd.DataFrame({
            "Indicador": [
                "Receita orçada", "Desvio de receita",
                "Lucro bruto orçado", "Desvio de lucro",
                "Custo real dos produtos", "Custo orçado dos produtos",
                "Volume realizado", "Volume orçado",
            ],
            "Valor": [
                money(total["receita_orcada"]),
                money(total["desvio_receita"]),
                money(total["lucro_orcado"]),
                money(total["desvio_lucro"]),
                money(total["custo_real"]),
                money(total["custo_orcado"]),
                number(total["volume_real"]),
                number(total["volume_orcado"]),
            ],
        })
        show_table(summary_cards, height=340, key="executive_summary")
        download_csv(
            summary_cards, "Baixar resumo executivo em CSV",
            "resumo_executivo.csv", "download_executive_summary",
        )

    st.subheader("Maiores gaps negativos de lucro por SKU")
    show_sku_table(
        sku_summary.sort_values("desvio_lucro").head(15),
        suffix="maiores_gaps_sku",
    )

    st.subheader("SKUs de maior receita com margem abaixo do orçamento")
    receita_corte = sku_summary["receita_real"].quantile(0.75)
    high_revenue_low_margin = sku_summary[
        (sku_summary["receita_real"] >= receita_corte)
        & (sku_summary["desvio_margem_pp"] < 0)
    ].sort_values("desvio_lucro").head(15)
    if high_revenue_low_margin.empty:
        st.info("Nenhum SKU atende aos critérios de receita alta e margem abaixo do orçamento neste recorte.")
    else:
        show_sku_table(
            high_revenue_low_margin,
            suffix="alta_receita_margem_baixa",
        )
    st.caption(
        "O corte de receita alta corresponde ao quartil superior dos SKUs no recorte. "
        "A tabela prioriza produtos relevantes em receita que perderam margem versus orçamento."
    )

    st.markdown(
        '<div class="insight"><b>Como interpretar:</b> comece pelos '
        'maiores impactos em reais, depois avalie a queda de margem e '
        'a recorrência. As hipóteses orientam a investigação, mas não '
        'representam causas confirmadas.</div>',
        unsafe_allow_html=True,
    )


# ==========================================================
# 02 — PERFORMANCE & TRENDS
# ==========================================================

elif page == "02 · Performance & Trends":
    kpi_row()
    indicator = st.selectbox(
        "Selecione o indicador",
        ["Receita", "Lucro bruto", "Volume", "Margem bruta"],
    )

    if indicator == "Receita":
        show_monthly("receita_real", "receita_orcada", "Receita mensal")
    elif indicator == "Lucro bruto":
        show_monthly("lucro_real", "lucro_orcado", "Lucro bruto mensal")
    elif indicator == "Volume":
        show_monthly("volume_real", "volume_orcado", "Volume mensal")
    else:
        show_monthly(
            "margem_real", "margem_orcada",
            "Margem bruta mensal", percent_axis=True,
        )

    st.subheader("Desvio de lucro por mês")
    fig = px.bar(
        monthly,
        x="mes",
        y="desvio_lucro",
        color="desvio_lucro",
        color_continuous_scale=[RED, "#F4D9A6", GREEN],
        title="Diferença entre lucro realizado e orçado",
    )
    fig.update_layout(coloraxis_showscale=False)
    fig.update_yaxes(tickprefix="R$ ", tickformat=",.2f")
    fig.update_traces(
        hovertemplate="%{x|%m/%Y}<br>Desvio: R$ %{y:,.2f}<extra></extra>"
    )
    st.plotly_chart(style_plot(fig, height=350), width="stretch")

    st.subheader("Dados mensais detalhados")
    monthly_view = monthly.copy()
    monthly_view["mes"] = monthly_view["mes"].dt.strftime("%m/%Y")
    show_table(monthly_view, key="monthly_detail")
    download_csv(
        monthly_view, "Baixar dados mensais em CSV",
        "performance_mensal.csv", "download_monthly",
    )


# ==========================================================
# 03 — PROFIT BRIDGE
# ==========================================================

elif page == "03 · Profit Bridge":
    kpi_row()

    price_effect = (
        (
            filtered["preco_liquido_unitario"]
            - filtered["preco_liquido_orcado_unitario"]
        ) * filtered["quantidade_real"]
    ).sum()

    volume_effect = (
        (filtered["quantidade_real"] - filtered["quantidade_orcada"])
        * (
            filtered["preco_liquido_orcado_unitario"]
            - filtered["custo_unitario_orcado"]
        )
    ).sum()

    cost_effect = (
        -(
            filtered["custo_unitario_real"]
            - filtered["custo_unitario_orcado"]
        ) * filtered["quantidade_real"]
    ).sum()

    total_gap = (
        filtered["lucro_bruto_real"].sum()
        - filtered["lucro_bruto_orcado"].sum()
    )
    residual = total_gap - price_effect - volume_effect - cost_effect

    bridge = pd.DataFrame({
        "Componente": [
            "Preço", "Volume", "Custo",
            "Interações / residual", "Desvio total real",
        ],
        "Impacto (R$)": [
            price_effect, volume_effect, cost_effect, residual, total_gap,
        ],
    })

    st.subheader("Ponte de variação do lucro bruto")
    fig = go.Figure(go.Waterfall(
        orientation="v",
        measure=["relative", "relative", "relative", "relative", "total"],
        x=bridge["Componente"],
        y=[price_effect, volume_effect, cost_effect, residual, 0],
        connector={"line": {"color": "#9AA8B8"}},
        increasing={"marker": {"color": GREEN}},
        decreasing={"marker": {"color": RED}},
        totals={"marker": {"color": NAVY}},
        text=[money(x) for x in [
            price_effect, volume_effect, cost_effect, residual, total_gap
        ]],
        textposition="outside",
    ))
    fig.update_yaxes(tickprefix="R$ ", tickformat=",.2f")
    fig.update_traces(
        hovertemplate="%{x}<br>Impacto: R$ %{y:,.2f}<extra></extra>"
    )
    st.plotly_chart(style_plot(fig, height=480), width="stretch")

    st.subheader("Valores da ponte")
    show_table(bridge, key="profit_bridge_table")
    download_csv(
        bridge, "Baixar ponte de lucro em CSV",
        "profit_bridge.csv", "download_profit_bridge",
    )

    st.warning(
        "O residual mostra a parcela ainda não explicada pela ponte "
        "simplificada. Valide a decomposição financeira antes de atribuir "
        "causalidade aos efeitos."
    )


# ==========================================================
# 04 — PORTFOLIO INTELLIGENCE
# ==========================================================

elif page == "04 · Portfolio Intelligence":
    kpi_row()
    left, right = st.columns(2)

    with left:
        st.subheader("Desvio de lucro por família")
        fam = family_summary.sort_values("desvio_lucro")
        fig = px.bar(
            fam, x="desvio_lucro", y="familia", orientation="h",
            color="desvio_lucro",
            color_continuous_scale=[RED, "#F1D8A8", GREEN],
        )
        fig.update_layout(coloraxis_showscale=False)
        fig.update_xaxes(tickprefix="R$ ", tickformat=",.2f")
        fig.update_traces(
            hovertemplate="%{y}<br>Desvio: R$ %{x:,.2f}<extra></extra>"
        )
        st.plotly_chart(style_plot(fig, height=440), width="stretch")

    with right:
        st.subheader("Receita x margem por SKU")
        plot = sku_summary.copy()
        plot["Margem realizada (%)"] = plot["margem_real"] * 100
        fig = px.scatter(
            plot,
            x="receita_real",
            y="Margem realizada (%)",
            size="lucro_real",
            color="desvio_lucro",
            hover_name="sku_id",
            hover_data=["familia", "desvio_lucro"],
            color_continuous_scale=[RED, "#E7C77E", GREEN],
        )
        fig.update_xaxes(tickprefix="R$ ", tickformat=",.2f")
        fig.update_yaxes(ticksuffix="%")
        fig.update_traces(
            hovertemplate=(
                "SKU: %{hovertext}<br>Receita: R$ %{x:,.2f}"
                "<br>Margem: %{y:.1f}%<extra></extra>"
            )
        )
        fig.update_layout(coloraxis_showscale=False)
        st.plotly_chart(style_plot(fig, height=440), width="stretch")

    st.subheader("Tabela de desempenho por família")
    family_view = family_summary.sort_values("desvio_lucro")
    show_table(family_view, key="family_performance")
    download_csv(
        family_view, "Baixar desempenho por família em CSV",
        "desempenho_familias.csv", "download_family_performance",
    )


# ==========================================================
# 05 — SKU INVESTIGATION
# ==========================================================

elif page == "05 · SKU Investigation":
    kpi_row()
    st.subheader("Investigação detalhada por SKU")

    selected_sku = st.selectbox(
        "Escolha o SKU",
        sorted(sku_summary["sku_id"].astype(str).unique()),
    )
    sku_row = sku_summary[
        sku_summary["sku_id"].astype(str) == selected_sku
    ].iloc[0]

    a, b, c, d = st.columns(4)
    a.metric("Família", str(sku_row["familia"]))
    b.metric("Receita realizada", money(sku_row["receita_real"]))
    c.metric("Desvio de lucro", money(sku_row["desvio_lucro"]))
    d.metric("Desvio de margem", percentage_points(sku_row["desvio_margem_pp"]))

    detail_rows = [
        ("Receita realizada", money(sku_row["receita_real"])),
        ("Receita orçada", money(sku_row["receita_orcada"])),
        ("Desvio de receita", money(sku_row["desvio_receita"])),
        ("Lucro bruto realizado", money(sku_row["lucro_real"])),
        ("Lucro bruto orçado", money(sku_row["lucro_orcado"])),
        ("Desvio de lucro bruto", money(sku_row["desvio_lucro"])),
        ("Margem bruta realizada", percent(sku_row["margem_real"])),
        ("Margem bruta orçada", percent(sku_row["margem_orcada"])),
        ("Desvio de margem bruta", percentage_points(sku_row["desvio_margem_pp"])),
        ("Volume realizado", number(sku_row["volume_real"])),
        ("Volume orçado", number(sku_row["volume_orcado"])),
        ("Preço líquido médio real", money(sku_row["preco_real"])),
        ("Preço líquido médio orçado", money(sku_row["preco_orcado"])),
        ("Custo unitário médio real", money(sku_row["custo_unit_real"])),
        ("Custo unitário médio orçado", money(sku_row["custo_unit_orcado"])),
        ("Recorrência do gap", percent(sku_row["recorrencia_gap"])),
        ("Hipótese inicial", str(sku_row["hipotese"])),
        ("Prioridade", str(sku_row["prioridade"])),
    ]
    if "margem_contribuicao_real_pct" in sku_row.index:
        detail_rows.extend([
            ("Margem de contribuição real", percent(sku_row["margem_contribuicao_real_pct"])),
            ("Margem de contribuição orçada", percent(sku_row["margem_contribuicao_orcada_pct"])),
            ("Desvio de margem de contribuição", percentage_points(sku_row["desvio_margem_contribuicao_pp"])),
        ])
    detail_table = pd.DataFrame(detail_rows, columns=["Indicador", "Valor"])

    show_table(detail_table, key="sku_detail_table")

    st.subheader("Decomposição aritmética do desvio de lucro")
    decomposition = pd.DataFrame({
        "Componente": ["Preço", "Volume", "Custo unitário", "Residual / interações", "Desvio total observado"],
        "Impacto (R$)": [
            sku_row["efeito_preco"],
            sku_row["efeito_volume"],
            sku_row["efeito_custo"],
            sku_row["residual_decomposicao"],
            sku_row["desvio_lucro"],
        ],
    })
    show_table(decomposition, key="sku_decomposition")
    st.caption(
        "A decomposição é uma aproximação aritmética baseada nas diferenças entre realizado e orçamento. "
        "O residual reúne efeitos não representados e interações; nenhum componente, isoladamente, comprova causalidade."
    )
    download_csv(
        detail_table, "Baixar indicadores do SKU em CSV",
        f"indicadores_{selected_sku}.csv", "download_sku_detail",
    )

    product_history = filtered[
        filtered["sku_id"].astype(str) == selected_sku
    ].groupby("mes", as_index=False).agg(
        receita_real=("receita_liquida_real", "sum"),
        receita_orcada=("receita_liquida_orcada", "sum"),
        lucro_real=("lucro_bruto_real", "sum"),
        lucro_orcado=("lucro_bruto_orcado", "sum"),
    )

    left, right = st.columns(2)
    with left:
        chart = product_history.melt(
            id_vars="mes",
            value_vars=["receita_real", "receita_orcada"],
            var_name="Série",
            value_name="Valor (R$)",
        )
        fig = px.line(
            chart, x="mes", y="Valor (R$)", color="Série",
            markers=True, title="Histórico de receita",
        )
        fig.update_yaxes(tickprefix="R$ ", tickformat=",.2f")
        fig.update_traces(
            hovertemplate="%{x|%m/%Y}<br>%{fullData.name}: R$ %{y:,.2f}<extra></extra>"
        )
        st.plotly_chart(style_plot(fig, height=340), width="stretch")

    with right:
        chart = product_history.melt(
            id_vars="mes",
            value_vars=["lucro_real", "lucro_orcado"],
            var_name="Série",
            value_name="Valor (R$)",
        )
        fig = px.line(
            chart, x="mes", y="Valor (R$)", color="Série",
            markers=True, title="Histórico de lucro",
        )
        fig.update_yaxes(tickprefix="R$ ", tickformat=",.2f")
        fig.update_traces(
            hovertemplate="%{x|%m/%Y}<br>%{fullData.name}: R$ %{y:,.2f}<extra></extra>"
        )
        st.plotly_chart(style_plot(fig, height=340), width="stretch")

    st.subheader("Histórico mensal em números")
    show_table(product_history, key="sku_monthly_history")
    download_csv(
        product_history, "Baixar histórico mensal do SKU em CSV",
        f"historico_{selected_sku}.csv", "download_sku_history",
    )


# ==========================================================
# 06 — GAP & RISK DIAGNOSIS
# ==========================================================

elif page == "06 · Gap & Risk Diagnosis":
    kpi_row()
    negative = sku_summary[sku_summary["desvio_lucro"] < 0].copy()
    positive = sku_summary[sku_summary["desvio_lucro"] > 0].copy()

    a, b, c, d = st.columns(4)
    a.metric("SKUs com gap negativo", number(negative["sku_id"].nunique()))
    b.metric("SKUs acima do orçamento", number(positive["sku_id"].nunique()))
    c.metric("Exposição negativa", money(-negative["desvio_lucro"].sum()))
    d.metric(
        "Perda média por SKU negativo",
        money(negative["desvio_lucro"].mean() if len(negative) else 0),
    )

    left, right = st.columns(2)
    with left:
        st.subheader("Famílias com maiores gaps")
        loss_families = family_summary.sort_values("desvio_lucro")
        fig = px.bar(
            loss_families, x="desvio_lucro", y="familia",
            orientation="h", color="desvio_lucro",
            color_continuous_scale=[RED, "#F2D6A0", GREEN],
        )
        fig.update_layout(coloraxis_showscale=False)
        fig.update_xaxes(tickprefix="R$ ", tickformat=",.2f")
        fig.update_traces(
            hovertemplate="%{y}<br>Desvio: R$ %{x:,.2f}<extra></extra>"
        )
        st.plotly_chart(style_plot(fig, height=420), width="stretch")

    with right:
        st.subheader("Impacto x recorrência")
        risk = negative.copy()
        risk["Impacto negativo absoluto"] = -risk["desvio_lucro"]
        risk["Recorrência (%)"] = risk["recorrencia_gap"] * 100

        fig = px.scatter(
            risk,
            x="Recorrência (%)",
            y="Impacto negativo absoluto",
            size="receita_real",
            color="prioridade",
            hover_name="sku_id",
            hover_data=["familia", "desvio_lucro", "desvio_margem_pp"],
            labels={"Impacto negativo absoluto": "Exposição financeira (R$)"},
            color_discrete_map={
                "Alta": RED,
                "Média": "#D99A32",
                "Monitorar / oportunidade": GREEN,
            },
        )
        fig.update_xaxes(ticksuffix="%", tickformat=".1f")
        fig.update_yaxes(tickprefix="R$ ", tickformat=",.2f")
        fig.update_traces(
            hovertemplate=(
                "SKU: %{hovertext}<br>Recorrência: %{x:.1f}%"
                "<br>Exposição: R$ %{y:,.2f}<extra></extra>"
            )
        )
        st.plotly_chart(style_plot(fig, height=420), width="stretch")

    st.subheader("Tabela completa de SKUs em risco")
    show_sku_table(
        negative.sort_values("desvio_lucro"),
        suffix="skus_em_risco",
    )
    st.caption(
        "A recorrência representa a proporção de meses selecionados "
        "em que o SKU teve desvio negativo de lucro bruto."
    )


# ==========================================================
# 07 — ACTION PLAN & OPPORTUNITIES
# ==========================================================

elif page == "07 · Action Plan & Opportunities":
    kpi_row()
    actions = sku_summary[sku_summary["desvio_lucro"] < 0].copy()
    actions = actions.sort_values("desvio_lucro")
    actions["Exposição potencial (R$)"] = -actions["desvio_lucro"]

    action_text = {
        "Sinal: aumento de custo (validar)":
            "Comparar custo unitário real e orçado; investigar compras, consumo, perdas e eficiência.",
        "Sinal: pressão de preço (validar)":
            "Validar preço líquido, descontos, condições comerciais e posicionamento de preço.",
        "Sinal: efeito de volume (validar)":
            "Validar variação de volume, demanda, disponibilidade, carteira e execução comercial.",
        "Sinal: interações/outros fatores (validar)":
            "Analisar mix, interações e fatores não representados na decomposição simplificada.",
        "Sem gap negativo: monitorar desempenho":
            "Monitorar a evolução da margem e confirmar se o desempenho favorável se mantém.",
    }
    actions["Próxima investigação"] = actions["hipotese"].map(action_text).fillna(
        "Validar dados e decomposição antes de concluir a causa do desvio."
    )
    actions["Status"] = "A investigar"

    a, b, c = st.columns(3)
    a.metric("SKUs no plano", number(len(actions)))
    b.metric("Exposição negativa", money(actions["Exposição potencial (R$)"].sum()))
    c.metric("SKUs prioridade alta", number((actions["prioridade"] == "Alta").sum()))

    st.markdown(
        '<div class="insight"><b>Como usar este plano:</b> a exposição '
        'potencial é o desvio negativo observado, não uma previsão de '
        'recuperação. Confirme a causa e a viabilidade antes de definir '
        'uma meta financeira.</div>',
        unsafe_allow_html=True,
    )

    st.subheader("Plano de investigação por SKU")
    action_view = actions[[
        "sku_id", "familia", "segmento",
        "desvio_lucro", "desvio_margem_pp",
        "recorrencia_gap", "prioridade", "hipotese",
        "Próxima investigação", "Status",
    ]].rename(columns={
        "sku_id": "SKU",
        "familia": "Família",
        "segmento": "Segmento",
        "desvio_lucro": "Gap lucro (R$)",
        "desvio_margem_pp": "Gap margem (p.p.)",
        "recorrencia_gap": "Recorrência",
        "prioridade": "Prioridade",
        "hipotese": "Hipótese inicial",
    })

    action_view["Recorrência"] = action_view["Recorrência"] * 100
    show_table(
        action_view,
        height=500,
        key="action_plan_table",
        column_config={
            "Gap lucro (R$)": st.column_config.NumberColumn(
                "Gap lucro (R$)", format="R$ %,.2f"
            ),
            "Gap margem (p.p.)": st.column_config.NumberColumn(
                "Gap margem (p.p.)", format="%.2f"
            ),
            "Recorrência": st.column_config.ProgressColumn(
                "Recorrência", format="%.1f%%", min_value=0, max_value=100
            ),
        },
    )
    download_csv(
        action_view, "Baixar plano de investigação em CSV",
        "plano_investigacao_skus.csv", "download_action_plan",
    )

    st.subheader("Exposição por prioridade")
    priority_summary = actions.groupby(
        "prioridade", as_index=False
    ).agg(
        quantidade_skus=("sku_id", "nunique"),
        exposicao=("Exposição potencial (R$)", "sum"),
    )
    show_table(priority_summary, key="priority_summary")
    download_csv(
        priority_summary, "Baixar resumo por prioridade em CSV",
        "exposicao_por_prioridade.csv", "download_priority_summary",
    )


# ==========================================================
# 09 — PRICING LAB: SIMULADOR, PVM E DISPERSÃO TEMPORAL
# ==========================================================

elif page == "09 · Pricing Lab":
    kpi_row()
    st.markdown(
        '<div class="insight"><b>Pricing Lab:</b> use os cenários como apoio à decisão, '
        'não como previsão garantida. A elasticidade é uma premissa editável pelo usuário; '
        'não é estimada automaticamente por esta base sintética.</div>',
        unsafe_allow_html=True,
    )

    tab_sim, tab_pvm, tab_disp = st.tabs([
        "Simulador de preço e margem",
        "Price-Volume-Mix",
        "Dispersão temporal de preços",
    ])

    # ------------------------------------------------------
    # SIMULADOR DE PREÇO
    # ------------------------------------------------------
    with tab_sim:
        st.subheader("Simulação de preço, demanda e rentabilidade")
        st.caption(
            "O cenário parte dos resultados agregados do SKU no período filtrado. "
            "O efeito de volume é estimado pela elasticidade informada, mantendo as demais "
            "condições constantes, exceto a variação de custo selecionada."
        )

        sku_options = sorted(sku_summary["sku_id"].astype(str).unique().tolist())
        selected_pricing_sku = st.selectbox(
            "SKU para simulação",
            sku_options,
            key="pricing_lab_sku",
        )
        pr = sku_summary[sku_summary["sku_id"].astype(str) == selected_pricing_sku].iloc[0]

        qty_base = float(pr["volume_real"]) if pd.notna(pr["volume_real"]) else 0.0
        revenue_base = float(pr["receita_real"]) if pd.notna(pr["receita_real"]) else 0.0
        gross_profit_base = float(pr["lucro_real"]) if pd.notna(pr["lucro_real"]) else 0.0
        cost_base = float(pr["custo_real"]) if pd.notna(pr["custo_real"]) else 0.0

        if qty_base <= 0 or revenue_base <= 0:
            st.warning(
                "Este SKU não tem volume e receita realizados positivos no período. "
                "Selecione outro SKU para executar a simulação."
            )
        else:
            price_base = revenue_base / qty_base
            cost_unit_base = cost_base / qty_base
            gross_profit_unit_base = gross_profit_base / qty_base
            margin_base = gross_profit_base / revenue_base if revenue_base else np.nan

            c1, c2, c3 = st.columns(3)
            with c1:
                price_change_pct = st.slider(
                    "Variação de preço (%)", -20, 30, 5, 1,
                    key="pricing_price_change",
                )
            with c2:
                elasticity = st.slider(
                    "Elasticidade-preço assumida",
                    min_value=-3.0, max_value=0.0, value=-1.0, step=0.1,
                    key="pricing_elasticity",
                    help="Ex.: -1,0 significa que uma alta de 1% no preço corresponde aproximadamente a queda de 1% no volume, localmente.",
                )
            with c3:
                cost_change_pct = st.slider(
                    "Variação do custo unitário (%)", -20, 50, 0, 1,
                    key="pricing_cost_change",
                )

            target_margin_pct = st.slider(
                "Margem bruta-alvo (%)", 5, 70, 30, 1,
                key="pricing_target_margin",
            )

            price_factor = 1 + price_change_pct / 100
            # Modelo de elasticidade constante: quantidade relativa = preço relativo ^ elasticidade.
            volume_factor = price_factor ** elasticity
            projected_qty = qty_base * volume_factor
            projected_price = price_base * price_factor
            projected_cost_unit = cost_unit_base * (1 + cost_change_pct / 100)
            projected_revenue = projected_price * projected_qty
            projected_gross_profit_unit = (
                gross_profit_unit_base
                + (projected_price - price_base)
                - (projected_cost_unit - cost_unit_base)
            )
            projected_gross_profit = projected_gross_profit_unit * projected_qty
            projected_margin = (
                projected_gross_profit / projected_revenue
                if projected_revenue else np.nan
            )
            delta_profit = projected_gross_profit - gross_profit_base
            delta_revenue = projected_revenue - revenue_base
            target_margin = target_margin_pct / 100

            if price_base > 0 and target_margin < 1:
                target_price_change = (
                    target_margin * price_base
                    - gross_profit_unit_base
                    + (projected_cost_unit - cost_unit_base)
                ) / (price_base * (1 - target_margin))
                target_price = price_base * (1 + target_price_change)
            else:
                target_price = np.nan

            st.divider()
            k1, k2, k3, k4 = st.columns(4)
            k1.metric(
                "Preço projetado por unidade",
                money(projected_price),
                f"{price_change_pct:+.0f}% vs. preço médio atual",
            )
            k2.metric(
                "Receita projetada",
                money(projected_revenue),
                money(delta_revenue) + " vs. atual",
            )
            k3.metric(
                "Lucro bruto projetado",
                money(projected_gross_profit),
                money(delta_profit) + " vs. atual",
                delta_color="normal",
            )
            k4.metric(
                "Margem bruta projetada",
                percent(projected_margin),
                percentage_points(projected_margin - margin_base)
                if pd.notna(projected_margin) and pd.notna(margin_base) else None,
                delta_color="normal",
            )

            m1, m2, m3 = st.columns(3)
            m1.metric("Volume projetado", number(projected_qty), f"{(volume_factor - 1) * 100:+.1f}% vs. atual")
            m2.metric("Custo unitário projetado", money(projected_cost_unit))
            m3.metric(
                f"Preço indicativo para margem-alvo de {target_margin_pct}%",
                money(target_price) if pd.notna(target_price) and target_price > 0 else "Não calculável",
            )

            scenario_rows = []
            for pct in [-10, -5, 0, 5, 10, 15, 20]:
                if pct <= -100:
                    continue
                factor = (1 + pct / 100) ** elasticity
                q = qty_base * factor
                p = price_base * (1 + pct / 100)
                c = cost_unit_base * (1 + cost_change_pct / 100)
                gp_unit = gross_profit_unit_base + (p - price_base) - (c - cost_unit_base)
                rev = p * q
                gp = gp_unit * q
                scenario_rows.append({
                    "Variação de preço (%)": pct,
                    "Volume projetado": q,
                    "Preço unitário (R$)": p,
                    "Receita projetada (R$)": rev,
                    "Lucro bruto projetado (R$)": gp,
                    "Margem bruta projetada (%)": gp / rev * 100 if rev else np.nan,
                    "Variação de lucro (R$)": gp - gross_profit_base,
                })
            scenario_table = pd.DataFrame(scenario_rows)
            fig_sens = px.line(
                scenario_table,
                x="Variação de preço (%)",
                y="Lucro bruto projetado (R$)",
                markers=True,
                title="Sensibilidade do lucro bruto ao preço",
            )
            fig_sens.add_hline(
                y=gross_profit_base,
                line_dash="dash",
                annotation_text="Lucro atual",
            )
            fig_sens.update_yaxes(tickprefix="R$ ", tickformat=",.0f")
            st.plotly_chart(style_plot(fig_sens, height=360), width="stretch")
            show_table(scenario_table, key="pricing_sensitivity_table")
            download_csv(
                scenario_table, "Baixar cenários de preço em CSV",
                f"pricing_scenarios_{selected_pricing_sku}.csv",
                "download_pricing_scenarios",
            )
            st.caption(
                "Limites: o lucro projetado parte do lucro bruto observado por unidade e ajusta "
                "preço e custo unitário. Não incorpora capacidade produtiva, reação competitiva, "
                "contratos, impostos, custos fixos ou mudanças no mix. O preço indicativo é "
                "matemático, não uma recomendação automática de reajuste."
            )

    # ------------------------------------------------------
    # PRICE-VOLUME-MIX
    # ------------------------------------------------------
    with tab_pvm:
        st.subheader("Ponte de rentabilidade: preço, volume, mix e custo")
        st.caption(
            "A ponte compara o realizado ao orçamento no recorte selecionado. "
            "Os efeitos são decomposições aritméticas; o residual deve ser investigado."
        )

        pvm = filtered.groupby("sku_id", as_index=False).agg(
            familia=("familia", "first"),
            receita_real=("receita_liquida_real", "sum"),
            receita_orcada=("receita_liquida_orcada", "sum"),
            volume_real=("quantidade_real", "sum"),
            volume_orcado=("quantidade_orcada", "sum"),
            custo_real=("custo_produtos_real", "sum"),
            custo_orcado=("custo_produtos_orcado", "sum"),
            lucro_real=("lucro_bruto_real", "sum"),
            lucro_orcado=("lucro_bruto_orcado", "sum"),
        )
        pvm = pvm[
            (pvm["volume_real"] >= 0)
            & (pvm["volume_orcado"] > 0)
        ].copy()

        pvm["preco_real_unit"] = np.where(
            pvm["volume_real"] > 0, pvm["receita_real"] / pvm["volume_real"], np.nan
        )
        pvm["preco_orcado_unit"] = pvm["receita_orcada"] / pvm["volume_orcado"]
        pvm["custo_real_unit"] = np.where(
            pvm["volume_real"] > 0, pvm["custo_real"] / pvm["volume_real"], np.nan
        )
        pvm["custo_orcado_unit"] = pvm["custo_orcado"] / pvm["volume_orcado"]
        pvm["lucro_orcado_unit"] = pvm["lucro_orcado"] / pvm["volume_orcado"]

        total_q_real = pvm["volume_real"].sum()
        total_q_budget = pvm["volume_orcado"].sum()
        avg_budget_gp_unit = (
            pvm["lucro_orcado"].sum() / total_q_budget if total_q_budget else 0
        )
        volume_effect_pvm = (total_q_real - total_q_budget) * avg_budget_gp_unit

        pvm["mix_orcado"] = pvm["volume_orcado"] / total_q_budget if total_q_budget else 0
        pvm["mix_real"] = pvm["volume_real"] / total_q_real if total_q_real else 0
        pvm["mix_qty_variance"] = (
            pvm["volume_real"] - total_q_real * pvm["mix_orcado"]
        )
        mix_effect_pvm = (
            pvm["mix_qty_variance"] * pvm["lucro_orcado_unit"]
        ).sum()

        price_effect_pvm = (
            (pvm["preco_real_unit"] - pvm["preco_orcado_unit"])
            * pvm["volume_real"]
        ).replace([np.inf, -np.inf], np.nan).sum(skipna=True)
        cost_effect_pvm = -(
            (pvm["custo_real_unit"] - pvm["custo_orcado_unit"])
            * pvm["volume_real"]
        ).replace([np.inf, -np.inf], np.nan).sum(skipna=True)
        profit_gap_pvm = pvm["lucro_real"].sum() - pvm["lucro_orcado"].sum()
        residual_pvm = (
            profit_gap_pvm - price_effect_pvm - volume_effect_pvm
            - mix_effect_pvm - cost_effect_pvm
        )

        pvm_bridge = pd.DataFrame({
            "Componente": [
                "Preço", "Volume total", "Mix de SKUs", "Custo unitário",
                "Interações / residual", "Desvio total de lucro bruto",
            ],
            "Impacto (R$)": [
                price_effect_pvm, volume_effect_pvm, mix_effect_pvm,
                cost_effect_pvm, residual_pvm, profit_gap_pvm,
            ],
        })

        fig_pvm = go.Figure(go.Waterfall(
            orientation="v",
            measure=["relative", "relative", "relative", "relative", "relative", "total"],
            x=pvm_bridge["Componente"],
            y=[price_effect_pvm, volume_effect_pvm, mix_effect_pvm,
               cost_effect_pvm, residual_pvm, 0],
            connector={"line": {"color": "#9AA8B8"}},
            increasing={"marker": {"color": GREEN}},
            decreasing={"marker": {"color": RED}},
            totals={"marker": {"color": NAVY}},
            text=[money(v) for v in pvm_bridge["Impacto (R$)"]],
            textposition="outside",
            hovertemplate="%{x}<br>Impacto: R$ %{y:,.2f}<extra></extra>",
        ))
        fig_pvm.update_layout(showlegend=False)
        fig_pvm.update_yaxes(tickprefix="R$ ", tickformat=",.0f")
        st.plotly_chart(style_plot(fig_pvm, height=440), width="stretch")
        show_table(pvm_bridge, key="pvm_bridge_table")
        download_csv(
            pvm_bridge, "Baixar ponte Price-Volume-Mix em CSV",
            "price_volume_mix.csv", "download_pvm_bridge",
        )
        st.caption(
            "O efeito de mix mede a mudança na composição de volumes entre SKUs usando "
            "o lucro bruto unitário orçado. O residual pode incluir interações, diferenças "
            "de definição contábil e limitações da base. Não é evidência causal."
        )

    # ------------------------------------------------------
    # DISPERSÃO TEMPORAL DE PREÇOS
    # ------------------------------------------------------
    with tab_disp:
        st.subheader("Evolução e dispersão temporal do preço líquido")
        st.caption(
            "A base disponível permite avaliar variação temporal por SKU, mas não comparar "
            "preços entre clientes ou vendedores se esses identificadores não existirem."
        )
        selected_disp_sku = st.selectbox(
            "SKU para análise temporal",
            sorted(filtered["sku_id"].astype(str).unique().tolist()),
            key="pricing_dispersion_sku",
        )
        disp_data = filtered[
            filtered["sku_id"].astype(str) == selected_disp_sku
        ].copy()
        disp_monthly = disp_data.groupby("mes", as_index=False).agg(
            receita=("receita_liquida_real", "sum"),
            volume=("quantidade_real", "sum"),
            preco_orcado=("preco_liquido_orcado_unitario", "mean"),
            desconto_medio=("desconto_pct", "mean"),
        )
        disp_monthly["preco_real"] = np.where(
            disp_monthly["volume"] != 0,
            disp_monthly["receita"] / disp_monthly["volume"],
            np.nan,
        )
        price_points = disp_monthly["preco_real"].dropna()
        if len(price_points):
            avg_price = price_points.mean()
            price_range_pct = (
                (price_points.max() - price_points.min()) / avg_price * 100
                if avg_price else np.nan
            )
            d1, d2, d3 = st.columns(3)
            d1.metric("Preço médio realizado", money(avg_price))
            d2.metric(
                "Amplitude entre máximo e mínimo",
                f"{price_range_pct:.1f}%" if pd.notna(price_range_pct) else "—",
            )
            d3.metric(
                "Meses com preço observável",
                number(len(price_points)),
            )
            price_chart_data = disp_monthly.melt(
                id_vars="mes",
                value_vars=["preco_real", "preco_orcado"],
                var_name="Série",
                value_name="Preço unitário (R$)",
            )
            fig_price = px.line(
                price_chart_data,
                x="mes", y="Preço unitário (R$)", color="Série",
                markers=True,
                title=f"Preço realizado x orçado — {selected_disp_sku}",
            )
            fig_price.update_yaxes(tickprefix="R$ ", tickformat=",.2f")
            st.plotly_chart(style_plot(fig_price, height=360), width="stretch")
            if disp_monthly["desconto_medio"].notna().any():
                st.subheader("Evolução do desconto registrado")
                discount_data = disp_monthly.dropna(subset=["desconto_medio"])
                fig_discount = px.line(
                    discount_data,
                    x="mes", y="desconto_medio", markers=True,
                    title="Desconto médio registrado por mês",
                )
                fig_discount.update_yaxes(ticksuffix="%")
                st.plotly_chart(style_plot(fig_discount, height=300), width="stretch")
            show_table(disp_monthly, key="pricing_temporal_dispersion")
            download_csv(
                disp_monthly, "Baixar série temporal de preços em CSV",
                f"preco_temporal_{selected_disp_sku}.csv",
                "download_price_temporal",
            )
        else:
            st.info("Não há preços realizados válidos para este SKU no período filtrado.")


# ==========================================================
# 08 — DATA QUALITY & METHODOLOGY
# ==========================================================

elif page == "10 · Rentabilidade & Descontos":
    kpi_row()
    st.title("Rentabilidade & Descontos")
    st.markdown(
        '<div class="insight"><b>Objetivo:</b> priorizar famílias, segmentos e SKUs para investigação '
        'de rentabilidade e possíveis oportunidades de preço. O valor de oportunidade é uma estimativa '
        'aritmética frente ao preço orçado — não representa recuperação garantida nem prova de desconto indevido.</div>',
        unsafe_allow_html=True,
    )

    tab_portfolio, tab_discount, tab_simulation = st.tabs([
        "Rentabilidade por família e segmento",
        "Oportunidade indicativa de preço",
        "Simulador de recuperação de margem",
    ])

    with tab_portfolio:
        st.subheader("Onde a rentabilidade está pressionada?")
        level = st.radio(
            "Agrupar por",
            ["Família", "Segmento"],
            horizontal=True,
            key="profitability_level",
        )
        group_col = "familia" if level == "Família" else "segmento"
        rent = summarize(filtered, [group_col])
        discount_agg = filtered.groupby(group_col, dropna=False).agg(
            desconto_medio=("desconto_pct", "mean"),
            preco_real_medio=("preco_liquido_unitario", "mean"),
            preco_orcado_medio=("preco_liquido_orcado_unitario", "mean"),
        ).reset_index()
        rent = rent.merge(discount_agg, on=group_col, how="left")
        rent["oportunidade_preco_indicativa"] = (
            (filtered["preco_liquido_orcado_unitario"] - filtered["preco_liquido_unitario"])
            .clip(lower=0) * filtered["quantidade_real"].clip(lower=0)
        ).groupby(filtered[group_col], dropna=False).sum().reindex(rent[group_col]).to_numpy()
        rent["desconto_medio_pct"] = rent["desconto_medio"] * 100
        rent["margem_real_pct"] = rent["margem_real"] * 100
        rent["margem_orcada_pct"] = rent["margem_orcada"] * 100
        c1, c2 = st.columns(2)
        with c1:
            st.plotly_chart(
                style_plot(px.bar(
                    rent.sort_values("desvio_lucro"),
                    x=group_col, y="desvio_lucro",
                    title="Desvio de lucro bruto vs. orçamento",
                    labels={group_col: level, "desvio_lucro": "Desvio de lucro bruto (R$)"},
                ).update_layout(paper_bgcolor=WHITE, plot_bgcolor=WHITE, font=dict(color=TEXT)), height=370, money_axis=True),
                use_container_width=True,
            )
        with c2:
            st.plotly_chart(
                style_plot(px.scatter(
                    rent,
                    x="desconto_medio_pct", y="margem_real_pct",
                    size="receita_real", color="desvio_lucro",
                    hover_name=group_col,
                    title="Desconto médio × margem bruta realizada",
                    labels={
                        "desconto_medio_pct": "Desconto médio (%)",
                        "margem_real_pct": "Margem bruta realizada (%)",
                        "desvio_lucro": "Desvio de lucro (R$)",
                        "receita_real": "Receita realizada (R$)",
                    },
                ).update_layout(paper_bgcolor=WHITE, plot_bgcolor=WHITE, font=dict(color=TEXT)), height=370),
                use_container_width=True,
            )
        rent_view = rent[[
            group_col, "skus", "receita_real", "receita_orcada",
            "lucro_real", "lucro_orcado", "margem_real_pct",
            "margem_orcada_pct", "desvio_margem_pp",
            "desconto_medio_pct", "oportunidade_preco_indicativa",
        ]].copy()
        rent_view = rent_view.rename(columns={
            group_col: level,
            "skus": "SKUs",
            "receita_real": "Receita realizada",
            "receita_orcada": "Receita orçada",
            "lucro_real": "Lucro bruto realizado",
            "lucro_orcado": "Lucro bruto orçado",
            "margem_real_pct": "Margem realizada (%)",
            "margem_orcada_pct": "Margem orçada (%)",
            "desvio_margem_pp": "Desvio margem (p.p.)",
            "desconto_medio_pct": "Desconto médio (%)",
            "oportunidade_preco_indicativa": "Oportunidade indicativa de preço",
        })
        show_table(
            rent_view.sort_values("Desvio margem (p.p.)"),
            height=430,
            key="rentabilidade_family_segment_table",
        )
        st.download_button(
            "Baixar análise por família/segmento (CSV)",
            csv_bytes(rent_view),
            file_name="rentabilidade_familias_segmentos.csv",
            mime="text/csv",
        )

    with tab_discount:
        st.subheader("SKUs com preço realizado abaixo do orçamento")
        st.caption(
            "A oportunidade indicativa calcula (preço orçado − preço realizado) × volume realizado, "
            "considerando apenas diferenças positivas. Não incorpora elasticidade, resposta competitiva, "
            "impostos adicionais nem condições específicas de clientes."
        )
        price_op = filtered.copy()
        price_op["gap_preco_unitario"] = (
            price_op["preco_liquido_orcado_unitario"] - price_op["preco_liquido_unitario"]
        )
        price_op["oportunidade_preco_indicativa"] = (
            price_op["gap_preco_unitario"].clip(lower=0)
            * price_op["quantidade_real"].clip(lower=0)
        )
        price_op["receita_preco_orcado_volume_real"] = (
            price_op["preco_liquido_orcado_unitario"]
            * price_op["quantidade_real"].clip(lower=0)
        )
        opp = price_op.groupby(["sku_id", "familia", "segmento"], dropna=False).agg(
            receita_real=("receita_liquida_real", "sum"),
            volume_real=("quantidade_real", "sum"),
            preco_real_medio=("preco_liquido_unitario", "mean"),
            preco_orcado_medio=("preco_liquido_orcado_unitario", "mean"),
            desconto_medio=("desconto_pct", "mean"),
            desvio_lucro=("desvio_lucro", "sum"),
            oportunidade_preco_indicativa=("oportunidade_preco_indicativa", "sum"),
            receita_preco_orcado_volume_real=("receita_preco_orcado_volume_real", "sum"),
        ).reset_index()
        opp["gap_preco_pct"] = np.where(
            opp["preco_orcado_medio"] != 0,
            (opp["preco_real_medio"] / opp["preco_orcado_medio"] - 1) * 100,
            np.nan,
        )
        opp = opp.sort_values("oportunidade_preco_indicativa", ascending=False)
        top_n = st.slider("Quantidade de SKUs para exibir", 5, 30, 15, key="price_op_topn")
        opp_top = opp.head(top_n)
        k1, k2, k3 = st.columns(3)
        k1.metric("Oportunidade indicativa total", money(opp["oportunidade_preco_indicativa"].sum()))
        k2.metric("SKUs com diferença positiva", int((opp["oportunidade_preco_indicativa"] > 0).sum()))
        k3.metric("Receita realizada dos SKUs", money(opp["receita_real"].sum()))
        st.plotly_chart(
            style_plot(px.bar(
                opp_top.sort_values("oportunidade_preco_indicativa"),
                x="oportunidade_preco_indicativa", y="sku_id", orientation="h",
                color="familia",
                title="Maiores oportunidades indicativas frente ao preço orçado",
                labels={
                    "oportunidade_preco_indicativa": "Valor indicativo (R$)",
                    "sku_id": "SKU",
                    "familia": "Família",
                },
            ).update_layout(paper_bgcolor=WHITE, plot_bgcolor=WHITE, font=dict(color=TEXT)).update_xaxes(tickprefix="R$ ", tickformat=",.0f"), height=440),
            use_container_width=True,
        )
        opp_view = opp[[
            "sku_id", "familia", "segmento", "receita_real", "volume_real",
            "preco_real_medio", "preco_orcado_medio", "gap_preco_pct",
            "desconto_medio", "desvio_lucro", "oportunidade_preco_indicativa",
            "receita_preco_orcado_volume_real",
        ]].rename(columns={
            "sku_id": "SKU",
            "familia": "Família",
            "segmento": "Segmento",
            "receita_real": "Receita realizada",
            "volume_real": "Volume realizado",
            "preco_real_medio": "Preço realizado médio",
            "preco_orcado_medio": "Preço orçado médio",
            "gap_preco_pct": "Diferença preço vs. orçamento (%)",
            "desconto_medio": "Desconto médio (%)",
            "desvio_lucro": "Desvio de lucro bruto",
            "oportunidade_preco_indicativa": "Oportunidade indicativa (R$)",
            "receita_preco_orcado_volume_real": "Receita a preço orçado e volume real",
        })
        show_table(
            opp_view.head(top_n),
            height=500,
            key="price_opportunity_table",
        )
        st.download_button(
            "Baixar oportunidades indicativas (CSV)",
            csv_bytes(opp_view),
            file_name="oportunidades_preco_sku.csv",
            mime="text/csv",
        )

    with tab_simulation:
        st.subheader("Simulação de recuperação de margem por ajuste de preço")
        st.markdown(
            '<div class="insight"><b>Simulação gerencial:</b> estima o efeito de recuperar parte da diferença positiva entre o preço orçado e o realizado nos SKUs abaixo do orçamento. '
            'Considera custo unitário constante e uma hipótese de retenção de volume definida pelo usuário. Não estima elasticidade real nem garante recuperação financeira.</div>',
            unsafe_allow_html=True,
        )

        sim_col1, sim_col2 = st.columns(2)
        with sim_col1:
            gap_capture_pct = st.slider(
                "Parcela da diferença de preço a recuperar (%)",
                min_value=0, max_value=100, value=25, step=5,
                key="margin_sim_gap_capture",
                help="Percentual do gap positivo entre preço orçado e realizado que seria recuperado no cenário.",
            )
        with sim_col2:
            volume_retention_pct = st.slider(
                "Retenção de volume nos SKUs reajustados (%)",
                min_value=70, max_value=100, value=95, step=1,
                key="margin_sim_volume_retention",
                help="Hipótese de volume mantido após o reajuste. Não é uma elasticidade estimada a partir dos dados.",
            )

        sim = filtered.copy()
        sim["volume_base_sim"] = pd.to_numeric(sim["quantidade_real"], errors="coerce").fillna(0).clip(lower=0)
        sim["preco_base_sim"] = pd.to_numeric(sim["preco_liquido_unitario"], errors="coerce").fillna(0)
        sim["preco_orcado_sim"] = pd.to_numeric(sim["preco_liquido_orcado_unitario"], errors="coerce").fillna(0)
        sim["custo_unitario_sim"] = pd.to_numeric(sim["custo_unitario_real"], errors="coerce").fillna(0)
        sim["gap_positivo_sim"] = (sim["preco_orcado_sim"] - sim["preco_base_sim"]).clip(lower=0)
        sim["sku_reajustado_sim"] = sim["gap_positivo_sim"] > 0
        sim["ajuste_unitario_sim"] = sim["gap_positivo_sim"] * (gap_capture_pct / 100)
        sim["volume_cenario_sim"] = np.where(
            sim["sku_reajustado_sim"],
            sim["volume_base_sim"] * (volume_retention_pct / 100),
            sim["volume_base_sim"],
        )
        sim["receita_base_sim"] = sim["preco_base_sim"] * sim["volume_base_sim"]
        sim["receita_cenario_sim"] = (
            sim["preco_base_sim"] + sim["ajuste_unitario_sim"]
        ) * sim["volume_cenario_sim"]
        sim["lucro_bruto_base_sim"] = (
            sim["preco_base_sim"] - sim["custo_unitario_sim"]
        ) * sim["volume_base_sim"]
        sim["lucro_bruto_cenario_sim"] = (
            sim["preco_base_sim"] + sim["ajuste_unitario_sim"] - sim["custo_unitario_sim"]
        ) * sim["volume_cenario_sim"]
        sim["variacao_receita_sim"] = sim["receita_cenario_sim"] - sim["receita_base_sim"]
        sim["variacao_lucro_sim"] = sim["lucro_bruto_cenario_sim"] - sim["lucro_bruto_base_sim"]

        sku_sim = sim.groupby(["sku_id", "familia", "segmento"], dropna=False).agg(
            receita_base=("receita_base_sim", "sum"),
            receita_cenario=("receita_cenario_sim", "sum"),
            lucro_base=("lucro_bruto_base_sim", "sum"),
            lucro_cenario=("lucro_bruto_cenario_sim", "sum"),
            variacao_receita=("variacao_receita_sim", "sum"),
            variacao_lucro_bruto=("variacao_lucro_sim", "sum"),
            volume_base=("volume_base_sim", "sum"),
            volume_cenario=("volume_cenario_sim", "sum"),
            gap_preco_medio=("gap_positivo_sim", "mean"),
            linhas_com_gap=("sku_reajustado_sim", "sum"),
        ).reset_index()
        sku_sim["margem_base_pct"] = np.where(
            sku_sim["receita_base"] != 0,
            sku_sim["lucro_base"] / sku_sim["receita_base"] * 100,
            np.nan,
        )
        sku_sim["margem_cenario_pct"] = np.where(
            sku_sim["receita_cenario"] != 0,
            sku_sim["lucro_cenario"] / sku_sim["receita_cenario"] * 100,
            np.nan,
        )
        sku_sim["sku_com_gap"] = sku_sim["linhas_com_gap"] > 0
        sku_sim = sku_sim.sort_values("variacao_lucro_bruto", ascending=False)

        total_variacao_lucro = float(sim["variacao_lucro_sim"].sum())
        total_variacao_receita = float(sim["variacao_receita_sim"].sum())
        skus_com_gap = int(sim.loc[sim["sku_reajustado_sim"], "sku_id"].nunique())
        k1, k2, k3 = st.columns(3)
        k1.metric("Variação estimada do lucro bruto", money(total_variacao_lucro))
        k2.metric("Variação estimada da receita", money(total_variacao_receita))
        k3.metric("SKUs com preço abaixo do orçamento", number(skus_com_gap))

        st.caption(
            f"Cenário: recuperação de {gap_capture_pct}% do gap positivo e retenção de volume de "
            f"{volume_retention_pct}%. A variação considera perda de volume apenas nos registros com gap positivo; "
            "os demais permanecem com o volume realizado. O cálculo é indicativo e mantém o custo unitário constante."
        )

        sim_chart = sku_sim[sku_sim["sku_com_gap"]].head(15).sort_values("variacao_lucro_bruto")
        if not sim_chart.empty:
            st.plotly_chart(
                style_plot(
                    px.bar(
                        sim_chart,
                        x="variacao_lucro_bruto",
                        y="sku_id",
                        orientation="h",
                        color="familia",
                        title="SKUs prioritários por variação estimada do lucro bruto",
                        labels={
                            "variacao_lucro_bruto": "Variação estimada do lucro bruto (R$)",
                            "sku_id": "SKU",
                            "familia": "Família",
                        },
                    ).update_layout(paper_bgcolor=WHITE, plot_bgcolor=WHITE, font=dict(color=TEXT)).update_xaxes(tickprefix="R$ ", tickformat=",.2f"),
                    height=440,
                ),
                use_container_width=True,
            )
        else:
            st.info("Não há SKUs com preço realizado abaixo do orçamento no período e nos filtros selecionados.")

        sim_view = sku_sim[[
            "sku_id", "familia", "segmento", "receita_base", "receita_cenario",
            "variacao_receita", "lucro_base", "lucro_cenario", "variacao_lucro_bruto",
            "margem_base_pct", "margem_cenario_pct", "volume_base", "volume_cenario",
            "gap_preco_medio", "sku_com_gap",
        ]].rename(columns={
            "sku_id": "SKU",
            "familia": "Família",
            "segmento": "Segmento",
            "receita_base": "Receita base simulada",
            "receita_cenario": "Receita no cenário",
            "variacao_receita": "Variação estimada da receita",
            "lucro_base": "Lucro bruto base simulado",
            "lucro_cenario": "Lucro bruto no cenário",
            "variacao_lucro_bruto": "Variação estimada do lucro bruto",
            "margem_base_pct": "Margem base simulada (%)",
            "margem_cenario_pct": "Margem no cenário (%)",
            "volume_base": "Volume base",
            "volume_cenario": "Volume no cenário",
            "gap_preco_medio": "Gap positivo médio de preço",
            "sku_com_gap": "Possui gap positivo",
        })
        show_table(
            sim_view,
            height=500,
            key="margin_recovery_simulation_table",
        )
        st.download_button(
            "Baixar simulação de recuperação de margem (CSV)",
            csv_bytes(sim_view),
            file_name="simulacao_recuperacao_margem.csv",
            mime="text/csv",
        )

elif page == "08 · Data Quality & Methodology":
    st.subheader("Qualidade e cobertura dos dados")

    quality = pd.DataFrame({
        "Teste": [
            "Quantidade de registros", "Quantidade de SKUs únicos",
            "Famílias distintas", "Segmentos distintos",
            "Meses disponíveis", "Primeiro mês", "Último mês",
            "Duplicidades de mês + SKU", "Células vazias",
        ],
        "Resultado": [
            number(len(hist)),
            number(hist["sku_id"].nunique()),
            number(hist["familia"].nunique()),
            number(hist["segmento"].nunique()),
            number(hist["mes"].nunique()),
            hist["mes"].min().strftime("%m/%Y"),
            hist["mes"].max().strftime("%m/%Y"),
            number(hist.duplicated(["mes", "sku_id"]).sum()),
            number(int(hist.isna().sum().sum())),
        ],
    })
    show_table(quality, key="data_quality_table")
    download_csv(
        quality, "Baixar relatório de qualidade em CSV",
        "qualidade_dados.csv", "download_quality",
    )

    st.subheader("Indicadores financeiros do recorte")
    financial = pd.DataFrame({
        "Indicador": [
            "Receita realizada", "Receita orçada", "Desvio de receita",
            "Lucro bruto realizado", "Lucro bruto orçado",
            "Desvio de lucro bruto", "Custo real", "Custo orçado",
            "Margem real", "Margem orçada", "Desvio de margem",
        ],
        "Valor": [
            money(total["receita_real"]),
            money(total["receita_orcada"]),
            money(total["desvio_receita"]),
            money(total["lucro_real"]),
            money(total["lucro_orcado"]),
            money(total["desvio_lucro"]),
            money(total["custo_real"]),
            money(total["custo_orcado"]),
            percent(total["margem_real"]),
            percent(total["margem_orcada"]),
            percentage_points(total["desvio_margem_pp"]),
        ],
    })
    show_table(financial, key="financial_summary")
    download_csv(
        financial, "Baixar indicadores financeiros em CSV",
        "indicadores_financeiros.csv", "download_financial",
    )

    st.subheader("Metodologia e definições")
    st.markdown("""
    - **Desvio:** realizado menos orçamento.
    - **Margem bruta:** lucro bruto dividido pela receita líquida.
    - **Margem de contribuição:** lucro bruto menos custos variáveis adicionais
      explicitamente registrados na base, dividido pela receita líquida.
    - **Margem líquida:** não é calculada neste projeto; exigiria despesas fixas,
      financeiras, impostos e demais componentes aplicáveis.
    - **Recorrência do gap:** proporção de meses do período com desvio
      negativo de lucro bruto.
    - **Decomposição preço/volume/custo:** estimativa aritmética para orientar
      investigação; o residual reúne interações e efeitos não representados.
    - **Hipótese de causa:** sinal preliminar, não comprovação causal.
    - **Dados:** base sintética criada para demonstrar o processo analítico.
    """)

    st.subheader("Amostra dos dados filtrados")
    show_table(filtered.head(100), key="filtered_data_sample")
    download_csv(
        filtered, "Exportar todos os dados filtrados",
        "historico_skus_filtrado.csv", "download_filtered_quality",
    )


# ==========================================================
# RODAPÉ
# ==========================================================

st.divider()
st.caption(
    "SKU Profitability Intelligence | Python · Pandas · Plotly · Streamlit "
    "| Base sintética para demonstração"
)
