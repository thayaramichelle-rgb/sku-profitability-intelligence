
"""Metricas financeiras do projeto SKU Profitability Intelligence.

Todos os dados utilizados neste projeto sao sinteticos.
"""

from pathlib import Path

import numpy as np
import pandas as pd


# Localizacao dos arquivos do projeto
PASTA_PROJETO = Path(__file__).resolve().parent.parent
PASTA_DADOS = PASTA_PROJETO / "data"

ARQUIVO_CADASTRO = PASTA_DADOS / "cadastro_skus.csv"
ARQUIVO_HISTORICO = PASTA_DADOS / "historico_skus.csv"


def carregar_dados():
    """Carrega o cadastro de produtos e o historico financeiro."""

    if not ARQUIVO_CADASTRO.exists():
        raise FileNotFoundError(
            f"Arquivo nao encontrado: {ARQUIVO_CADASTRO}"
        )

    if not ARQUIVO_HISTORICO.exists():
        raise FileNotFoundError(
            f"Arquivo nao encontrado: {ARQUIVO_HISTORICO}"
        )

    cadastro = pd.read_csv(
        ARQUIVO_CADASTRO,
        sep=";",
        encoding="utf-8-sig"
    )

    historico = pd.read_csv(
        ARQUIVO_HISTORICO,
        sep=";",
        encoding="utf-8-sig",
        parse_dates=["mes"]
    )

    return cadastro, historico


def validar_dados(cadastro, historico):
    """Verifica a estrutura e a consistencia dos dados."""

    colunas_obrigatorias = [
        "mes",
        "sku_id",
        "familia",
        "segmento",
        "cenario_simulado",
        "quantidade_real",
        "receita_liquida_real",
        "custo_produtos_real",
        "lucro_bruto_real",
        "receita_liquida_orcada",
        "lucro_bruto_orcado",
        "margem_contribuicao_real",
    ]

    faltantes = [
        coluna
        for coluna in colunas_obrigatorias
        if coluna not in historico.columns
    ]

    if faltantes:
        raise ValueError(
            f"Colunas obrigatorias ausentes: {faltantes}"
        )

    if cadastro["sku_id"].duplicated().any():
        raise ValueError(
            "O cadastro possui SKUs duplicados."
        )

    if historico.duplicated(["mes", "sku_id"]).any():
        raise ValueError(
            "Existe mais de um registro para o mesmo SKU e mes."
        )

    if historico[colunas_obrigatorias].isna().any().any():
        raise ValueError(
            "Existem valores ausentes nas colunas obrigatorias."
        )

    # Confere se o lucro bruto corresponde a receita menos custo.
    diferenca = (
        historico["receita_liquida_real"]
        - historico["custo_produtos_real"]
        - historico["lucro_bruto_real"]
    ).abs()

    # Pequena tolerancia para os arredondamentos do arquivo CSV.
    if diferenca.max() > 0.02:
        raise ValueError(
            "A conciliacao entre receita, custo e lucro falhou."
        )

    if cadastro["sku_id"].nunique() != 8000:
        raise ValueError(
            "A quantidade de SKUs do cadastro nao e 8.000."
        )

    if historico["mes"].nunique() != 24:
        raise ValueError(
            "O historico nao possui os 24 meses esperados."
        )

    return True


def dividir_com_seguranca(numerador, denominador):
    """Divide valores sem gerar erros quando o denominador e zero."""

    return np.divide(
        numerador,
        denominador,
        out=np.full(
            np.broadcast(
                np.asarray(numerador),
                np.asarray(denominador)
            ).shape,
            np.nan,
            dtype=float
        ),
        where=np.asarray(denominador) != 0
    )


def calcular_resumo_portfolio(historico):
    """Calcula indicadores consolidados de rentabilidade."""

    receita_real = historico["receita_liquida_real"].sum()
    custo_real = historico["custo_produtos_real"].sum()
    lucro_real = historico["lucro_bruto_real"].sum()

    receita_orcada = historico["receita_liquida_orcada"].sum()
    custo_orcado = historico["custo_produtos_orcado"].sum()
    lucro_orcado = historico["lucro_bruto_orcado"].sum()

    contribuicao_real = (
        historico["margem_contribuicao_real"].sum()
    )

    contribuicao_orcada = (
        historico["margem_contribuicao_orcada"].sum()
    )

    margem_real_pct = dividir_com_seguranca(
        lucro_real, receita_real
    )

    margem_orcada_pct = dividir_com_seguranca(
        lucro_orcado, receita_orcada
    )

    contribuicao_real_pct = dividir_com_seguranca(
        contribuicao_real, receita_real
    )

    contribuicao_orcada_pct = dividir_com_seguranca(
        contribuicao_orcada, receita_orcada
    )

    return {
        "receita_liquida_real": receita_real,
        "receita_liquida_orcada": receita_orcada,
        "desvio_receita": receita_real - receita_orcada,
        "desvio_receita_pct": dividir_com_seguranca(
            receita_real - receita_orcada,
            receita_orcada
        ),

        "custo_produtos_real": custo_real,
        "custo_produtos_orcado": custo_orcado,
        "desvio_custo": custo_real - custo_orcado,

        "lucro_bruto_real": lucro_real,
        "lucro_bruto_orcado": lucro_orcado,
        "desvio_lucro_bruto": lucro_real - lucro_orcado,

        "margem_bruta_real_pct": margem_real_pct,
        "margem_bruta_orcada_pct": margem_orcada_pct,
        "desvio_margem_bruta_pp": (
            margem_real_pct - margem_orcada_pct
        ) * 100,

        "margem_contribuicao_real": contribuicao_real,
        "margem_contribuicao_orcada": contribuicao_orcada,
        "margem_contribuicao_real_pct": contribuicao_real_pct,
        "margem_contribuicao_orcada_pct": contribuicao_orcada_pct,

        "quantidade_skus": historico["sku_id"].nunique(),
        "quantidade_meses": historico["mes"].nunique(),
    }


def agrupar_por_sku(historico):
    """Consolida os 24 meses de cada SKU para analisar seu desempenho."""

    colunas_soma = [
        "quantidade_real",
        "quantidade_orcada",
        "receita_liquida_real",
        "receita_liquida_orcada",
        "custo_produtos_real",
        "custo_produtos_orcado",
        "lucro_bruto_real",
        "lucro_bruto_orcado",
        "margem_contribuicao_real",
        "margem_contribuicao_orcada",
    ]

    colunas_soma = [
        coluna
        for coluna in colunas_soma
        if coluna in historico.columns
    ]

    identificacao = [
        "sku_id",
        "familia",
        "segmento",
        "cenario_simulado",
    ]

    resultado = (
        historico
        .groupby(identificacao, as_index=False)
        [colunas_soma]
        .sum()
    )

    # Margens ponderadas: lucro dividido pela receita total.
    resultado["margem_bruta_real_pct"] = dividir_com_seguranca(
        resultado["lucro_bruto_real"],
        resultado["receita_liquida_real"]
    )

    resultado["margem_bruta_orcada_pct"] = dividir_com_seguranca(
        resultado["lucro_bruto_orcado"],
        resultado["receita_liquida_orcada"]
    )

    resultado["margem_contribuicao_real_pct"] = (
        dividir_com_seguranca(
            resultado["margem_contribuicao_real"],
            resultado["receita_liquida_real"]
        )
    )

    resultado["margem_contribuicao_orcada_pct"] = (
        dividir_com_seguranca(
            resultado["margem_contribuicao_orcada"],
            resultado["receita_liquida_orcada"]
        )
    )

    resultado["desvio_receita_vs_orcado"] = (
        resultado["receita_liquida_real"]
        - resultado["receita_liquida_orcada"]
    )

    resultado["desvio_lucro_bruto_vs_orcado"] = (
        resultado["lucro_bruto_real"]
        - resultado["lucro_bruto_orcado"]
    )

    resultado["desvio_margem_bruta_pp"] = (
        resultado["margem_bruta_real_pct"]
        - resultado["margem_bruta_orcada_pct"]
    ) * 100

    resultado["desvio_margem_contribuicao_pp"] = (
        resultado["margem_contribuicao_real_pct"]
        - resultado["margem_contribuicao_orcada_pct"]
    ) * 100

    return resultado


def analisar_familias(historico):
    """Consolida os resultados para comparar familias de produtos."""

    familias = (
        historico
        .groupby("familia", as_index=False)
        .agg(
            receita_real=("receita_liquida_real", "sum"),
            receita_orcada=("receita_liquida_orcada", "sum"),
            custo_real=("custo_produtos_real", "sum"),
            lucro_real=("lucro_bruto_real", "sum"),
            lucro_orcado=("lucro_bruto_orcado", "sum"),
            contribuicao_real=("margem_contribuicao_real", "sum"),
            skus=("sku_id", "nunique"),
        )
    )

    familias["desvio_lucro"] = (
        familias["lucro_real"] - familias["lucro_orcado"]
    )

    familias["margem_bruta_real_pct"] = (
        dividir_com_seguranca(
            familias["lucro_real"],
            familias["receita_real"]
        )
    )

    familias["margem_bruta_orcada_pct"] = (
        dividir_com_seguranca(
            familias["lucro_orcado"],
            familias["receita_orcada"]
        )
    )

    familias["desvio_margem_pp"] = (
        familias["margem_bruta_real_pct"]
        - familias["margem_bruta_orcada_pct"]
    ) * 100

    return familias.sort_values(
        "desvio_lucro",
        ascending=True
    )


def main():
    """Executa as validacoes e apresenta um primeiro diagnostico."""

    cadastro, historico = carregar_dados()

    validar_dados(cadastro, historico)

    resumo = calcular_resumo_portfolio(historico)
    skus = agrupar_por_sku(historico)
    familias = analisar_familias(historico)

    print("\n" + "=" * 60)
    print("SKU PROFITABILITY INTELLIGENCE")
    print("Diagnostico inicial de rentabilidade")
    print("=" * 60)

    print("\nVALIDACAO DA BASE")
    print(f"SKUs no cadastro: {len(cadastro):,}".replace(",", "."))
    print(f"Registros historicos: {len(historico):,}".replace(",", "."))
    print("Conciliacao financeira: aprovada")

    print("\nRESUMO FINANCEIRO DO PORTFOLIO")
    print(
        f"Receita real: R$ "
        f"{resumo['receita_liquida_real']:,.2f}"
    )
    print(
        f"Receita orcada: R$ "
        f"{resumo['receita_liquida_orcada']:,.2f}"
    )
    print(
        f"Desvio de receita: R$ "
        f"{resumo['desvio_receita']:,.2f}"
    )
    print(
        f"Lucro bruto real: R$ "
        f"{resumo['lucro_bruto_real']:,.2f}"
    )
    print(
        f"Lucro bruto orcado: R$ "
        f"{resumo['lucro_bruto_orcado']:,.2f}"
    )
    print(
        f"Desvio de lucro bruto: R$ "
        f"{resumo['desvio_lucro_bruto']:,.2f}"
    )
    print(
        f"Margem bruta real: "
        f"{resumo['margem_bruta_real_pct']:.2%}"
    )
    print(
        f"Margem bruta orcada: "
        f"{resumo['margem_bruta_orcada_pct']:.2%}"
    )
    print(
        f"Desvio de margem: "
        f"{resumo['desvio_margem_bruta_pp']:.2f} pontos percentuais"
    )

    print("\n10 SKUs COM MAIOR DETERIORACAO DO LUCRO VS. ORCAMENTO")
    colunas = [
        "sku_id",
        "familia",
        "cenario_simulado",
        "receita_liquida_real",
        "lucro_bruto_real",
        "desvio_lucro_bruto_vs_orcado",
        "desvio_margem_bruta_pp",
    ]

    print(
        skus.sort_values("desvio_lucro_bruto_vs_orcado")
        [colunas]
        .head(10)
        .round(2)
        .to_string(index=False)
    )

    print("\nFAMILIAS COM MAIOR DESVIO NEGATIVO DE LUCRO")
    print(
        familias[
            [
                "familia",
                "skus",
                "lucro_real",
                "lucro_orcado",
                "desvio_lucro",
                "desvio_margem_pp",
            ]
        ]
        .head(7)
        .round(2)
        .to_string(index=False)
    )

    print(
        "\nATENCAO: a base e sintetica. "
        "Os resultados sao demonstrativos."
    )


if __name__ == "__main__":
    main()
