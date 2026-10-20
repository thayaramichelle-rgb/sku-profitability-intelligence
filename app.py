
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
    "impacto", "exposição", "exposicao", "gap receita",
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
    path = DATA_DIR / "historico_skus.csv"

    if not path.exists():
        raise FileNotFoundError(
            f"Não encontrei o arquivo: {path}. "
            "Confirme se historico_skus.csv está dentro da pasta data."
        )

    data = pd.read_csv(path, sep=";")

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
    return out


total = summarize(filtered).iloc[0]
monthly = summarize(filtered, ["mes"]).sort_values("mes")
family_summary = summarize(filtered, ["familia"]).sort_values("desvio_lucro")
sku_summary = summarize(filtered, ["sku_id", "familia", "segmento"])

sku_extra = filtered.groupby("sku_id", as_index=False).agg(
    preco_real=("preco_liquido_unitario", "mean"),
    preco_orcado=("preco_liquido_orcado_unitario", "mean"),
    custo_unit_real=("custo_unitario_real", "mean"),
    custo_unit_orcado=("custo_unitario_orcado", "mean"),
    desconto_medio=("desconto_pct", "mean"),
    meses_analisados=("mes", "nunique"),
    meses_com_gap=("desvio_lucro", lambda s: int((s < 0).sum())),
)

sku_summary = sku_summary.merge(sku_extra, on="sku_id", how="left")
sku_summary["recorrencia_gap"] = (
    sku_summary["meses_com_gap"]
    / sku_summary["meses_analisados"].replace(0, np.nan)
)

sku_summary["hipotese"] = np.select(
    [
        (sku_summary["desvio_lucro"] < 0)
        & (sku_summary["custo_unit_real"] > sku_summary["custo_unit_orcado"]),
        (sku_summary["desvio_lucro"] < 0)
        & (sku_summary["preco_real"] < sku_summary["preco_orcado"]),
        (sku_summary["desvio_lucro"] < 0)
        & (sku_summary["volume_real"] < sku_summary["volume_orcado"]),
    ],
    [
        "Investigar custo unitário",
        "Investigar preço e descontos",
        "Investigar volume",
    ],
    default="Investigar mix e outros fatores",
)

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
    a, b, c, d = st.columns(4)
    a.metric(
        "Receita realizada",
        money(total["receita_real"]),
        f"{money(total['desvio_receita'])} vs. orçamento",
    )
    b.metric(
        "Lucro bruto realizado",
        money(total["lucro_real"]),
        f"{money(total['desvio_lucro'])} vs. orçamento",
    )
    c.metric(
        "Margem bruta realizada",
        percent(total["margem_real"]),
        percentage_points(total["desvio_margem_pp"]),
    )
    d.metric(
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

    detail_table = pd.DataFrame({
        "Indicador": [
            "Receita realizada", "Receita orçada", "Desvio de receita",
            "Lucro bruto realizado", "Lucro bruto orçado",
            "Desvio de lucro bruto", "Margem realizada", "Margem orçada",
            "Desvio de margem", "Volume realizado", "Volume orçado",
            "Preço líquido médio real", "Preço líquido médio orçado",
            "Custo unitário médio real", "Custo unitário médio orçado",
            "Recorrência do gap", "Hipótese inicial", "Prioridade",
        ],
        "Valor": [
            money(sku_row["receita_real"]),
            money(sku_row["receita_orcada"]),
            money(sku_row["desvio_receita"]),
            money(sku_row["lucro_real"]),
            money(sku_row["lucro_orcado"]),
            money(sku_row["desvio_lucro"]),
            percent(sku_row["margem_real"]),
            percent(sku_row["margem_orcada"]),
            percentage_points(sku_row["desvio_margem_pp"]),
            number(sku_row["volume_real"]),
            number(sku_row["volume_orcado"]),
            money(sku_row["preco_real"]),
            money(sku_row["preco_orcado"]),
            money(sku_row["custo_unit_real"]),
            money(sku_row["custo_unit_orcado"]),
            percent(sku_row["recorrencia_gap"]),
            str(sku_row["hipotese"]),
            str(sku_row["prioridade"]),
        ],
    })

    show_table(detail_table, key="sku_detail_table")
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
        "Investigar custo unitário":
            "Comparar custo real e orçamento; revisar consumo, perdas, compras e eficiência.",
        "Investigar preço e descontos":
            "Revisar preço líquido, descontos concedidos e condições comerciais.",
        "Investigar volume":
            "Avaliar demanda, disponibilidade, carteira e execução comercial.",
        "Investigar mix e outros fatores":
            "Comparar com SKUs semelhantes e decompor os fatores do desvio.",
    }
    actions["Próxima investigação"] = actions["hipotese"].map(action_text)
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
# 08 — DATA QUALITY & METHODOLOGY
# ==========================================================

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
    - **Recorrência do gap:** proporção de meses do período com desvio
      negativo de lucro bruto.
    - **Prioridade:** regra inicial para ordenar a investigação.
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
