"""Gera uma base sintetica para o projeto SKU Profitability Intelligence.

Os dados sao inteiramente ficticios e servem apenas para demonstrar metodos
de analise de rentabilidade. Nao representam dados da CBA nem de outra empresa.

Execucao no terminal, dentro da pasta do projeto:
    py -m pip install pandas numpy
    py gerar_base.py
"""

from pathlib import Path
import numpy as np
import pandas as pd


# Configuracoes gerais: manter a semente fixa torna a base reproduzivel.
SEMENTE = 42
QTD_SKUS = 8_000
QTD_MESES = 24
DATA_INICIAL = "2024-01-01"


def gerar_base() -> tuple[pd.DataFrame, pd.DataFrame]:
    """Gera cadastro de SKUs e historico mensal de desempenho financeiro."""
    rng = np.random.default_rng(SEMENTE)

    meses = pd.date_range(
        DATA_INICIAL,
        periods=QTD_MESES,
        freq="MS"
    )

    familias = np.array([
        "Chapas",
        "Bobinas",
        "Perfis",
        "Extrudados",
        "Componentes",
        "Laminados",
        "Outros industriais"
    ])

    pesos_familias = [
        0.16, 0.17, 0.14, 0.16, 0.13, 0.14, 0.10
    ]

    familia_sku = rng.choice(
        familias,
        size=QTD_SKUS,
        p=pesos_familias
    )

    segmentos = np.array([
        "Industrial",
        "Distribuicao",
        "Grandes contas",
        "PME"
    ])

    segmento_sku = rng.choice(
        segmentos,
        size=QTD_SKUS,
        p=[0.30, 0.29, 0.24, 0.17]
    )

    cadastro = pd.DataFrame({
        "sku_id": [
            f"SKU-{i:05d}"
            for i in range(1, QTD_SKUS + 1)
        ],
        "familia": familia_sku,
        "segmento": segmento_sku,
        "cenario_simulado": "Sem desvio induzido",
    })

    # Parametros economicos de cada SKU.
    preco_base = np.clip(
        rng.lognormal(
            mean=np.log(260),
            sigma=0.62,
            size=QTD_SKUS
        ),
        25,
        4500
    )

    proporcao_custo = rng.uniform(
        0.48, 0.79, size=QTD_SKUS
    )

    custo_base = preco_base * proporcao_custo

    quantidade_base = np.clip(
        rng.lognormal(
            mean=np.log(420),
            sigma=0.85,
            size=QTD_SKUS
        ),
        8,
        9000
    )

    desconto_base = rng.uniform(
        0.025, 0.105, size=QTD_SKUS
    )

    custo_variavel_pct = rng.uniform(
        0.015, 0.055, size=QTD_SKUS
    )

    tendencia_sku = rng.normal(
        loc=0.0015,
        scale=0.0020,
        size=QTD_SKUS
    )

    tendencia_sku = np.clip(
        tendencia_sku, -0.004, 0.007
    )

    # Grupos de teste mutuamente exclusivos.
    # Ajudam a conferir se o diagnostico encontra os problemas
    # inseridos de forma controlada.
    ordem = rng.permutation(QTD_SKUS)

    limites = {
        "Aumento de custo": int(QTD_SKUS * 0.10),
        "Pressao de preco": int(QTD_SKUS * 0.08),
        "Queda de volume": int(QTD_SKUS * 0.08),
        "Deterioracao combinada": int(QTD_SKUS * 0.05),
    }

    inicio = 0

    for cenario, tamanho in limites.items():
        indices = ordem[inicio:inicio + tamanho]

        cadastro.loc[
            indices, "cenario_simulado"
        ] = cenario

        inicio += tamanho

    historico = []

    # Os desvios induzidos aparecem nos seis meses finais.
    for indice_mes, mes in enumerate(meses):

        fator_tendencia = np.power(
            1 + tendencia_sku,
            indice_mes
        )

        sazonalidade = (
            1.0
            + 0.07 * np.sin(
                (indice_mes % 12) / 12 * 2 * np.pi
            )
        )

        ruido_volume = rng.lognormal(
            mean=-0.5 * 0.10**2,
            sigma=0.10,
            size=QTD_SKUS
        )

        quantidade_real = np.maximum(
            0,
            np.rint(
                quantidade_base
                * fator_tendencia
                * sazonalidade
                * ruido_volume
            )
        ).astype(int)

        # Orcamento: referencia planejada antes dos desvios.
        quantidade_orcada = np.maximum(
            1,
            np.rint(
                quantidade_base
                * fator_tendencia
                * sazonalidade
            )
        ).astype(int)

        preco_lista_orcado = (
            preco_base * (1 + 0.0015 * indice_mes)
        )

        desconto_orcado = desconto_base

        preco_liquido_orcado = (
            preco_lista_orcado * (1 - desconto_orcado)
        )

        custo_unitario_orcado = (
            custo_base * (1 + 0.0018 * indice_mes)
        )

        # Realizado: pequenas variacoes organicas de preco,
        # desconto e custo.
        preco_lista_real = (
            preco_base
            * (1 + 0.0013 * indice_mes)
            * rng.normal(1.0, 0.008, QTD_SKUS)
        )

        desconto_real = np.clip(
            desconto_base
            + rng.normal(0, 0.006, QTD_SKUS),
            0.0,
            0.22
        )

        custo_unitario_real = (
            custo_base
            * (1 + 0.0020 * indice_mes)
            * rng.normal(1.0, 0.012, QTD_SKUS)
        )

        # O cenario so e aplicado no periodo final.
        periodo_com_desvio = (
            indice_mes >= QTD_MESES - 6
        )

        cenarios = cadastro[
            "cenario_simulado"
        ].to_numpy()

        if periodo_com_desvio:

            mascara_custo = np.isin(
                cenarios,
                [
                    "Aumento de custo",
                    "Deterioracao combinada"
                ]
            )

            mascara_preco = np.isin(
                cenarios,
                [
                    "Pressao de preco",
                    "Deterioracao combinada"
                ]
            )

            mascara_volume = np.isin(
                cenarios,
                [
                    "Queda de volume",
                    "Deterioracao combinada"
                ]
            )

            custo_unitario_real[mascara_custo] *= np.where(
                cenarios[mascara_custo]
                == "Deterioracao combinada",
                1.08,
                1.10
            )

            # Reduz o preco liquido efetivo.
            # A pressao fica registrada em coluna propria.
            pressao_preco_pct = np.zeros(QTD_SKUS)

            pressao_preco_pct[mascara_preco] = np.where(
                cenarios[mascara_preco]
                == "Deterioracao combinada",
                0.04,
                0.07
            )

            quantidade_real[mascara_volume] = np.rint(
                quantidade_real[mascara_volume]
                * np.where(
                    cenarios[mascara_volume]
                    == "Deterioracao combinada",
                    0.82,
                    0.75
                )
            ).astype(int)

        else:
            pressao_preco_pct = np.zeros(QTD_SKUS)

        preco_liquido_real = (
            preco_lista_real
            * (1 - desconto_real)
            * (1 - pressao_preco_pct)
        )

        # Calculo dos indicadores financeiros realizados.
        receita_liquida_real = (
            quantidade_real * preco_liquido_real
        )

        custo_produtos_real = (
            quantidade_real * custo_unitario_real
        )

        lucro_bruto_real = (
            receita_liquida_real - custo_produtos_real
        )

        custo_variavel_adicional_real = (
            receita_liquida_real * custo_variavel_pct
        )

        margem_contribuicao_real = (
            lucro_bruto_real
            - custo_variavel_adicional_real
        )

        # Calculo dos indicadores financeiros orcados.
        receita_liquida_orcada = (
            quantidade_orcada * preco_liquido_orcado
        )

        custo_produtos_orcado = (
            quantidade_orcada * custo_unitario_orcado
        )

        lucro_bruto_orcado = (
            receita_liquida_orcada - custo_produtos_orcado
        )

        custo_variavel_adicional_orcado = (
            receita_liquida_orcada * custo_variavel_pct
        )

        margem_contribuicao_orcada = (
            lucro_bruto_orcado
            - custo_variavel_adicional_orcado
        )

        # Montagem da base mensal.
        df_mes = pd.DataFrame({
            "mes": mes,

            "sku_id": cadastro["sku_id"].to_numpy(),
            "familia": familia_sku,
            "segmento": segmento_sku,
            "cenario_simulado": cenarios,

            "quantidade_real": quantidade_real,
            "quantidade_orcada": quantidade_orcada,

            "preco_lista_unitario": preco_lista_real,

            "desconto_pct": (
                1 - (preco_liquido_real / preco_lista_real)
            ),

            "pressao_preco_pct": pressao_preco_pct,
            "preco_liquido_unitario": preco_liquido_real,
            "custo_unitario_real": custo_unitario_real,

            "receita_liquida_real": receita_liquida_real,
            "custo_produtos_real": custo_produtos_real,
            "lucro_bruto_real": lucro_bruto_real,

            "margem_bruta_real_pct": np.divide(
                lucro_bruto_real,
                receita_liquida_real,
                out=np.zeros_like(lucro_bruto_real),
                where=receita_liquida_real != 0
            ),

            "custo_variavel_adicional_real": (
                custo_variavel_adicional_real
            ),

            "margem_contribuicao_real": (
                margem_contribuicao_real
            ),

            "margem_contribuicao_real_pct": np.divide(
                margem_contribuicao_real,
                receita_liquida_real,
                out=np.zeros_like(margem_contribuicao_real),
                where=receita_liquida_real != 0
            ),

            "preco_liquido_orcado_unitario": (
                preco_liquido_orcado
            ),

            "custo_unitario_orcado": custo_unitario_orcado,

            "receita_liquida_orcada": (
                receita_liquida_orcada
            ),

            "custo_produtos_orcado": (
                custo_produtos_orcado
            ),

            "lucro_bruto_orcado": lucro_bruto_orcado,

            "margem_bruta_orcada_pct": np.divide(
                lucro_bruto_orcado,
                receita_liquida_orcada,
                out=np.zeros_like(lucro_bruto_orcado),
                where=receita_liquida_orcada != 0
            ),

            "margem_contribuicao_orcada": (
                margem_contribuicao_orcada
            ),

            "desvio_receita_vs_orcado": (
                receita_liquida_real
                - receita_liquida_orcada
            ),

            "desvio_lucro_bruto_vs_orcado": (
                lucro_bruto_real
                - lucro_bruto_orcado
            ),

            "desvio_margem_bruta_pp": (
                np.divide(
                    lucro_bruto_real,
                    receita_liquida_real,
                    out=np.zeros_like(lucro_bruto_real),
                    where=receita_liquida_real != 0
                )
                - np.divide(
                    lucro_bruto_orcado,
                    receita_liquida_orcada,
                    out=np.zeros_like(lucro_bruto_orcado),
                    where=receita_liquida_orcada != 0
                )
            ) * 100,
        })

        historico.append(df_mes)

    historico_df = pd.concat(
        historico,
        ignore_index=True
    )

    cadastro["preco_lista_base"] = preco_base.round(2)
    cadastro["custo_unitario_base"] = custo_base.round(2)

    return cadastro, historico_df


def validar_base(
    cadastro: pd.DataFrame,
    historico: pd.DataFrame
) -> None:
    """Executa verificacoes simples antes de salvar os arquivos."""

    assert len(cadastro) == QTD_SKUS, (
        f"Esperados {QTD_SKUS} SKUs; "
        f"encontrados {len(cadastro)}."
    )

    assert cadastro["sku_id"].nunique() == QTD_SKUS, (
        "Existem SKUs duplicados no cadastro."
    )

    assert len(historico) == QTD_SKUS * QTD_MESES, (
        "Quantidade inesperada de linhas no historico."
    )

    assert historico[
        [
            "receita_liquida_real",
            "custo_produtos_real",
            "lucro_bruto_real"
        ]
    ].notna().all().all(), (
        "Ha valores ausentes nas metricas financeiras."
    )

    assert (
        historico["quantidade_real"] >= 0
    ).all(), "Ha quantidades negativas."

    diferenca_lucro = (
        historico["receita_liquida_real"]
        - historico["custo_produtos_real"]
        - historico["lucro_bruto_real"]
    ).abs().max()

    assert diferenca_lucro < 0.01, (
        "Falha na conciliacao do lucro bruto: "
        f"diferenca maxima {diferenca_lucro}."
    )


def main() -> None:
    pasta_projeto = Path(__file__).resolve().parent

    pasta_dados = pasta_projeto / "data"
    pasta_dados.mkdir(parents=True, exist_ok=True)

    print("Gerando cadastro e historico sintetico...")

    cadastro, historico = gerar_base()

    validar_base(cadastro, historico)

    caminho_cadastro = (
        pasta_dados / "cadastro_skus.csv"
    )

    caminho_historico = (
        pasta_dados / "historico_skus.csv"
    )

    cadastro.to_csv(
        caminho_cadastro,
        index=False,
        encoding="utf-8-sig",
        sep=";",
        float_format="%.4f"
    )

    historico.to_csv(
        caminho_historico,
        index=False,
        encoding="utf-8-sig",
        sep=";",
        float_format="%.4f"
    )

    print("\nBase criada e validada com sucesso!")

    print(
        f"SKUs unicos: "
        f"{cadastro['sku_id'].nunique():,}".replace(",", ".")
    )

    print(
        f"Meses: {historico['mes'].nunique()}"
    )

    print(
        f"Linhas historicas: "
        f"{len(historico):,}".replace(",", ".")
    )

    print(f"\nCadastro: {caminho_cadastro}")
    print(f"Historico: {caminho_historico}")

    print("\nCenarios incluidos para testar o diagnostico:")

    print(
        cadastro["cenario_simulado"]
        .value_counts()
        .to_string()
    )

    print(
        "\nObservacao: todos os registros sao sinteticos "
        "e nao representam dados reais de nenhuma empresa."
    )


if __name__ == "__main__":
    main()