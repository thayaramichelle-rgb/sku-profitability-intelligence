
"""Diagnostico de rentabilidade por SKU.
Analisa os seis meses mais recentes da base sintetica.
"""

from pathlib import Path

import numpy as np
import pandas as pd


PASTA_PROJETO = Path(__file__).resolve().parent.parent
PASTA_DADOS = PASTA_PROJETO / "data"
MESES_ANALISE = 6


def carregar_historico():
    """Carrega o historico financeiro gerado pelo projeto."""

    arquivo = PASTA_DADOS / "historico_skus.csv"

    if not arquivo.exists():
        raise FileNotFoundError(
            f"Arquivo nao encontrado: {arquivo}"
        )

    return pd.read_csv(
        arquivo,
        sep=";",
        encoding="utf-8-sig",
        parse_dates=["mes"],
    )


def dividir_seguro(numerador, denominador):
    """Calcula uma divisao, tratando denominadores iguais a zero."""

    numerador = np.asarray(numerador, dtype=float)
    denominador = np.asarray(denominador, dtype=float)

    return np.divide(
        numerador,
        denominador,
        out=np.full(
            np.broadcast(numerador, denominador).shape,
            np.nan,
            dtype=float,
        ),
        where=denominador != 0,
    )


def selecionar_periodo_recente(historico):
    """Seleciona os seis meses mais recentes disponiveis."""

    meses = np.sort(historico["mes"].dropna().unique())

    if len(meses) < MESES_ANALISE:
        raise ValueError(
            "A base nao possui seis meses de historico."
        )

    meses_selecionados = meses[-MESES_ANALISE:]

    recente = historico[
        historico["mes"].isin(meses_selecionados)
    ].copy()

    if recente.empty:
        raise ValueError(
            "Nenhum registro encontrado no periodo selecionado."
        )

    return recente, meses_selecionados


def calcular_efeitos_financeiros(historico):
    """Decompoe a variacao do lucro bruto em preco, volume e custo.

    Os efeitos formam uma ponte matematica entre o lucro bruto
    orcado e o realizado. Sao efeitos estimados pela comparacao
    com o orcamento, nao provas definitivas de causalidade.
    """

    df = historico.copy()

    # Efeito do preco liquido realizado contra o preco orcado.
    df["efeito_preco"] = (
        df["preco_liquido_unitario"]
        - df["preco_liquido_orcado_unitario"]
    ) * df["quantidade_real"]

    # Efeito do volume usando preco e custo unitarios orcados.
    df["efeito_volume"] = (
        df["quantidade_real"]
        - df["quantidade_orcada"]
    ) * (
        df["preco_liquido_orcado_unitario"]
        - df["custo_unitario_orcado"]
    )

    # Efeito do custo unitario na quantidade realizada.
    df["efeito_custo"] = (
        df["custo_unitario_orcado"]
        - df["custo_unitario_real"]
    ) * df["quantidade_real"]

    return df


def agregar_por_sku(historico):
    """Consolida desempenho e efeitos financeiros por produto."""

    identificacao = [
        "sku_id",
        "familia",
        "segmento",
        "cenario_simulado",
    ]

    sku = (
        historico
        .groupby(identificacao, as_index=False)
        .agg(
            quantidade_real=("quantidade_real", "sum"),
            quantidade_orcada=("quantidade_orcada", "sum"),
            receita_liquida_real=(
                "receita_liquida_real", "sum"
            ),
            receita_liquida_orcada=(
                "receita_liquida_orcada", "sum"
            ),
            custo_produtos_real=(
                "custo_produtos_real", "sum"
            ),
            custo_produtos_orcado=(
                "custo_produtos_orcado", "sum"
            ),
            lucro_bruto_real=("lucro_bruto_real", "sum"),
            lucro_bruto_orcado=("lucro_bruto_orcado", "sum"),
            efeito_preco=("efeito_preco", "sum"),
            efeito_volume=("efeito_volume", "sum"),
            efeito_custo=("efeito_custo", "sum"),
        )
    )

    sku["desvio_receita_vs_orcado"] = (
        sku["receita_liquida_real"]
        - sku["receita_liquida_orcada"]
    )

    sku["desvio_lucro_bruto_vs_orcado"] = (
        sku["lucro_bruto_real"]
        - sku["lucro_bruto_orcado"]
    )

    sku["margem_bruta_real_pct"] = dividir_seguro(
        sku["lucro_bruto_real"],
        sku["receita_liquida_real"],
    )

    sku["margem_bruta_orcada_pct"] = dividir_seguro(
        sku["lucro_bruto_orcado"],
        sku["receita_liquida_orcada"],
    )

    sku["desvio_margem_bruta_pp"] = (
        sku["margem_bruta_real_pct"]
        - sku["margem_bruta_orcada_pct"]
    ) * 100

    return sku


def classificar_diagnostico(sku):
    """Aponta o principal efeito negativo e prioriza as perdas."""

    componentes = [
        "efeito_preco",
        "efeito_volume",
        "efeito_custo",
    ]

    nomes_causas = {
        "efeito_preco": "Pressao de preco ou desconto",
        "efeito_volume": "Volume abaixo do orcamento",
        "efeito_custo": "Custo unitario acima do orcamento",
    }

    menor_efeito = sku[componentes].min(axis=1)
    componente_dominante = sku[componentes].idxmin(axis=1)

    sku["causa_principal_provavel"] = (
        componente_dominante.map(nomes_causas)
    )

    # Se nenhum componente for negativo, nao atribui uma
    # hipotese de deterioracao com base nessa ponte.
    sku.loc[
        menor_efeito >= 0,
        "causa_principal_provavel",
    ] = "Nenhum efeito negativo dominante"

    # Faixas relativas de priorizacao. Sao criterios demonstrativos,
    # nao limites oficiais de uma empresa.
    perda = (
        -sku["desvio_lucro_bruto_vs_orcado"]
    ).clip(lower=0)

    perdas_relevantes = perda[perda > 0]

    sku["prioridade"] = "Sem deterioracao de lucro"

    sku.loc[
        sku["desvio_lucro_bruto_vs_orcado"] < 0,
        "prioridade",
    ] = "Acompanhar"

    if not perdas_relevantes.empty:
        limite_alto = perdas_relevantes.quantile(0.90)
        limite_medio = perdas_relevantes.quantile(0.75)

        sku.loc[
            (perda >= limite_medio)
            & (sku["desvio_lucro_bruto_vs_orcado"] < 0),
            "prioridade",
        ] = "Media"

        sku.loc[
            (perda >= limite_alto)
            & (sku["desvio_lucro_bruto_vs_orcado"] < 0),
            "prioridade",
        ] = "Alta"

    return sku


def resumir_familias(historico):
    """Consolida os resultados financeiros por familia."""

    familias = (
        historico
        .groupby("familia", as_index=False)
        .agg(
            skus=("sku_id", "nunique"),
            receita_real=("receita_liquida_real", "sum"),
            receita_orcada=("receita_liquida_orcada", "sum"),
            lucro_real=("lucro_bruto_real", "sum"),
            lucro_orcado=("lucro_bruto_orcado", "sum"),
            efeito_preco=("efeito_preco", "sum"),
            efeito_volume=("efeito_volume", "sum"),
            efeito_custo=("efeito_custo", "sum"),
        )
    )

    familias["desvio_lucro"] = (
        familias["lucro_real"]
        - familias["lucro_orcado"]
    )

    familias["margem_real_pct"] = dividir_seguro(
        familias["lucro_real"],
        familias["receita_real"],
    )

    familias["margem_orcada_pct"] = dividir_seguro(
        familias["lucro_orcado"],
        familias["receita_orcada"],
    )

    familias["desvio_margem_pp"] = (
        familias["margem_real_pct"]
        - familias["margem_orcada_pct"]
    ) * 100

    return familias.sort_values(
        "desvio_lucro",
        ascending=True,
    )


def main():
    """Executa o diagnostico e salva os resultados."""

    historico = carregar_historico()
    recente, meses = selecionar_periodo_recente(historico)

    recente = calcular_efeitos_financeiros(recente)
    sku = agregar_por_sku(recente)
    sku = classificar_diagnostico(sku)
    familias = resumir_familias(recente)

    receita_real = recente["receita_liquida_real"].sum()
    receita_orcada = recente["receita_liquida_orcada"].sum()
    lucro_real = recente["lucro_bruto_real"].sum()
    lucro_orcado = recente["lucro_bruto_orcado"].sum()

    margem_real = dividir_seguro(lucro_real, receita_real)
    margem_orcada = dividir_seguro(lucro_orcado, receita_orcada)

    print("\n" + "=" * 72)
    print("SKU PROFITABILITY INTELLIGENCE")
    print("Diagnostico dos seis meses mais recentes")
    print("=" * 72)

    print(
        f"\nPeriodo: {pd.Timestamp(meses[0]).strftime('%m/%Y')}"
        f" a {pd.Timestamp(meses[-1]).strftime('%m/%Y')}"
    )

    print(f"SKUs analisados: {sku['sku_id'].nunique():,}".replace(",", "."))
    print(f"Receita realizada: R$ {receita_real:,.2f}")
    print(f"Receita orcada: R$ {receita_orcada:,.2f}")
    print(f"Desvio de receita: R$ {receita_real - receita_orcada:,.2f}")
    print(f"Lucro bruto realizado: R$ {lucro_real:,.2f}")
    print(f"Lucro bruto orcado: R$ {lucro_orcado:,.2f}")
    print(f"Desvio de lucro bruto: R$ {lucro_real - lucro_orcado:,.2f}")
    print(f"Margem bruta realizada: {margem_real:.2%}")
    print(f"Margem bruta orcada: {margem_orcada:.2%}")
    print(f"Desvio de margem: {(margem_real - margem_orcada) * 100:.2f} p.p.")

    print("\nPONTE DE VARIACAO DO LUCRO BRUTO")
    print(f"Efeito de preco: R$ {recente['efeito_preco'].sum():,.2f}")
    print(f"Efeito de volume: R$ {recente['efeito_volume'].sum():,.2f}")
    print(f"Efeito de custo: R$ {recente['efeito_custo'].sum():,.2f}")
    print(
        "Desvio total de lucro bruto: "
        f"R$ {(lucro_real - lucro_orcado):,.2f}"
    )

    colunas_top = [
        "sku_id",
        "familia",
        "cenario_simulado",
        "desvio_lucro_bruto_vs_orcado",
        "desvio_margem_bruta_pp",
        "efeito_preco",
        "efeito_volume",
        "efeito_custo",
        "causa_principal_provavel",
        "prioridade",
    ]

    print("\n20 SKUs COM MAIOR PERDA DE LUCRO CONTRA O ORCAMENTO")

    top_20 = (
        sku[sku["desvio_lucro_bruto_vs_orcado"] < 0]
        .sort_values("desvio_lucro_bruto_vs_orcado")
        .head(20)
    )

    print(
        top_20[colunas_top]
        .round(2)
        .to_string(index=False)
    )

    print("\nFAMILIAS COM MAIOR DESVIO NEGATIVO DE LUCRO")

    print(
        familias[
            [
                "familia",
                "skus",
                "desvio_lucro",
                "desvio_margem_pp",
                "efeito_preco",
                "efeito_volume",
                "efeito_custo",
            ]
        ]
        .head(7)
        .round(2)
        .to_string(index=False)
    )

    arquivo_skus = (
        PASTA_DADOS / "diagnostico_skus_ultimos_6_meses.csv"
    )

    arquivo_familias = (
        PASTA_DADOS / "diagnostico_familias_ultimos_6_meses.csv"
    )

    sku.to_csv(
        arquivo_skus,
        index=False,
        sep=";",
        encoding="utf-8-sig",
        float_format="%.4f",
    )

    familias.to_csv(
        arquivo_familias,
        index=False,
        sep=";",
        encoding="utf-8-sig",
        float_format="%.4f",
    )

    print("\nARQUIVOS GERADOS")
    print(arquivo_skus)
    print(arquivo_familias)

    print(
        "\nNota: os dados sao sinteticos. "
        "As causas indicadas sao hipoteses para investigacao."
    )


if __name__ == "__main__":
    main()
