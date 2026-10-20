"""Controlled, reproducible synthetic scenarios for SKU profitability.

The portfolio contains 8,000 synthetic SKUs. Exactly 2,000 are assigned a
controlled profitability issue, stratified across product family and segment.
Only the last six months contain the injected issues.
"""
from __future__ import annotations

import numpy as np
import pandas as pd


TOTAL_SKUS = 8_000
PROBLEM_SKUS = 2_000
SEED = 20261019
ISSUE_LABELS = (
    "Aumento de custo",
    "Pressao de preco",
    "Queda de volume",
    "Deterioracao combinada",
)


def calcular_simulacao_recuperacao_margem(
    data: pd.DataFrame,
    recuperacao_gap_pct: float,
    retencao_volume_pct: float,
) -> pd.DataFrame:
    """Calculate a price-recovery scenario with an explicit volume-retention assumption."""
    if not 0 <= recuperacao_gap_pct <= 100:
        raise ValueError("A recuperação do gap deve estar entre 0% e 100%.")
    if not 0 <= retencao_volume_pct <= 100:
        raise ValueError("A retenção de volume deve estar entre 0% e 100%.")

    required = {
        "quantidade_real", "preco_liquido_unitario",
        "preco_liquido_orcado_unitario", "custo_unitario_real",
    }
    missing = sorted(required - set(data.columns))
    if missing:
        raise ValueError("Colunas ausentes para simular recuperação de margem: " + ", ".join(missing))

    sim = data.copy()
    sim["volume_base_sim"] = pd.to_numeric(sim["quantidade_real"], errors="coerce").fillna(0).clip(lower=0)
    sim["preco_base_sim"] = pd.to_numeric(sim["preco_liquido_unitario"], errors="coerce").fillna(0)
    sim["preco_orcado_sim"] = pd.to_numeric(sim["preco_liquido_orcado_unitario"], errors="coerce").fillna(0)
    sim["custo_unitario_sim"] = pd.to_numeric(sim["custo_unitario_real"], errors="coerce").fillna(0)
    sim["gap_positivo_sim"] = (sim["preco_orcado_sim"] - sim["preco_base_sim"]).clip(lower=0)
    sim["sku_reajustado_sim"] = sim["gap_positivo_sim"] > 0
    sim["ajuste_unitario_sim"] = sim["gap_positivo_sim"] * (recuperacao_gap_pct / 100)
    sim["gap_x_volume_sim"] = sim["gap_positivo_sim"] * sim["volume_base_sim"]

    # No price adjustment means no simulated volume loss.
    sim["volume_cenario_sim"] = np.where(
        sim["sku_reajustado_sim"] & (recuperacao_gap_pct > 0),
        sim["volume_base_sim"] * (retencao_volume_pct / 100),
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
    return sim


def _select_stratified_skus(master: pd.DataFrame, target_count: int, rng) -> list[str]:
    """Select exactly target_count SKUs proportionally within family/segment strata."""
    groups = list(master.groupby(["familia", "segmento"], dropna=False, sort=True).indices.items())
    sizes = np.array([len(indices) for _, indices in groups], dtype=int)
    exact = sizes * (target_count / len(master))
    quotas = np.floor(exact).astype(int)
    remainder = target_count - int(quotas.sum())

    if remainder:
        fractional = exact - quotas
        for idx in np.argsort(-fractional, kind="stable")[:remainder]:
            quotas[idx] += 1

    selected = []
    sku_values = master["sku_id"].astype(str).to_numpy()
    for (_, positions), quota in zip(groups, quotas):
        if quota <= 0:
            continue
        positions = np.asarray(positions, dtype=int)
        chosen = rng.choice(positions, size=int(quota), replace=False)
        selected.extend(sku_values[chosen].tolist())

    if len(selected) != target_count or len(set(selected)) != target_count:
        raise ValueError("Falha ao selecionar exatamente a quantidade planejada de SKUs problemáticos.")
    return selected


def aplicar_cenarios_controlados(historico: pd.DataFrame) -> pd.DataFrame:
    """Rebuild coherent budget/actual values and inject issues into exactly 2,000 SKUs.

    This is applied both when generating the source CSVs and when loading the
    currently versioned CSV chunks in Streamlit, so both paths stay consistent.
    """
    required = {
        "mes", "sku_id", "familia", "segmento", "quantidade_orcada",
        "preco_liquido_orcado_unitario", "custo_unitario_orcado",
        "receita_liquida_orcada", "custo_produtos_orcado", "lucro_bruto_orcado",
    }
    missing = sorted(required - set(historico.columns))
    if missing:
        raise ValueError("Colunas necessárias para os cenários ausentes: " + ", ".join(missing))

    data = historico.copy()
    master = data[["sku_id", "familia", "segmento"]].drop_duplicates().sort_values("sku_id").reset_index(drop=True)
    if master["sku_id"].nunique() != len(master):
        raise ValueError("Um SKU está associado a mais de uma família/segmento.")
    if len(master) != TOTAL_SKUS:
        raise ValueError(f"A base deve conter {TOTAL_SKUS:,} SKUs únicos; foram encontrados {len(master):,}.")

    month_values = pd.to_datetime(data["mes"], errors="coerce")
    months = sorted(month_values.dropna().unique())
    if len(months) != 24:
        raise ValueError(f"A base deve conter 24 meses; foram encontrados {len(months)}.")
    if len(months) < 6:
        raise ValueError("A base precisa conter pelo menos seis meses para aplicar os cenários.")

    rng = np.random.default_rng(SEED)
    selected_ids = _select_stratified_skus(master, PROBLEM_SKUS, rng)
    shuffled_ids = np.asarray(selected_ids, dtype=object)
    rng.shuffle(shuffled_ids)

    labels = np.repeat(ISSUE_LABELS, PROBLEM_SKUS // len(ISSUE_LABELS))
    if len(labels) < PROBLEM_SKUS:
        labels = np.concatenate([labels, np.resize(np.asarray(ISSUE_LABELS, dtype=object), PROBLEM_SKUS - len(labels))])
    rng.shuffle(labels)
    scenario_by_sku = dict(zip(shuffled_ids.tolist(), labels.tolist()))

    data["mes"] = month_values
    data["cenario_simulado"] = data["sku_id"].astype(str).map(scenario_by_sku).fillna("Sem desvio induzido")
    is_problem = data["cenario_simulado"].ne("Sem desvio induzido")
    is_recent = data["mes"].isin(months[-6:])
    scenario = data["cenario_simulado"]

    # Capture the source's discount and variable-cost rates before rebuilding
    # realized/budget totals from the rounded unit prices and costs.
    if "desconto_pct" in data.columns:
        base_discount = pd.to_numeric(data["desconto_pct"], errors="coerce").fillna(0).clip(0, 0.30)
    else:
        base_discount = pd.Series(0.05, index=data.index, dtype=float)

    old_budget_revenue = pd.to_numeric(data["receita_liquida_orcada"], errors="coerce").fillna(0)
    if "custo_variavel_adicional_orcado" in data.columns:
        old_variable_cost = pd.to_numeric(data["custo_variavel_adicional_orcado"], errors="coerce").fillna(0)
        variable_cost_rate = np.divide(
            old_variable_cost.to_numpy(),
            old_budget_revenue.to_numpy(),
            out=np.zeros(len(data), dtype=float),
            where=old_budget_revenue.to_numpy() != 0,
        )
    elif "margem_contribuicao_orcada" in data.columns:
        old_contribution = pd.to_numeric(data["margem_contribuicao_orcada"], errors="coerce").fillna(0)
        old_gross_profit = pd.to_numeric(data["lucro_bruto_orcado"], errors="coerce").fillna(0)
        variable_cost_rate = np.divide(
            (old_gross_profit - old_contribution).to_numpy(),
            old_budget_revenue.to_numpy(),
            out=np.zeros(len(data), dtype=float),
            where=old_budget_revenue.to_numpy() != 0,
        )
    else:
        variable_cost_rate = np.zeros(len(data), dtype=float)

    # Reconcile budget totals to the published unit prices/costs, avoiding
    # small artificial gaps caused by CSV decimal rounding.
    data["quantidade_orcada"] = pd.to_numeric(data["quantidade_orcada"], errors="coerce").fillna(0).clip(lower=0)
    data["preco_liquido_orcado_unitario"] = pd.to_numeric(data["preco_liquido_orcado_unitario"], errors="coerce").fillna(0).clip(lower=0)
    data["custo_unitario_orcado"] = pd.to_numeric(data["custo_unitario_orcado"], errors="coerce").fillna(0).clip(lower=0)
    data["receita_liquida_orcada"] = data["quantidade_orcada"] * data["preco_liquido_orcado_unitario"]
    data["custo_produtos_orcado"] = data["quantidade_orcada"] * data["custo_unitario_orcado"]
    data["lucro_bruto_orcado"] = data["receita_liquida_orcada"] - data["custo_produtos_orcado"]

    # Start with a clean, exactly reconciled baseline for all 8,000 SKUs.
    data["quantidade_real"] = data["quantidade_orcada"].copy()
    data["preco_liquido_unitario"] = data["preco_liquido_orcado_unitario"].copy()
    data["custo_unitario_real"] = data["custo_unitario_orcado"].copy()
    data["receita_liquida_real"] = data["quantidade_real"] * data["preco_liquido_unitario"]
    data["custo_produtos_real"] = data["quantidade_real"] * data["custo_unitario_real"]
    data["lucro_bruto_real"] = data["receita_liquida_real"] - data["custo_produtos_real"]

    # Keep a consistent list price/discount relationship in the baseline.
    if "preco_lista_unitario" in data.columns:
        data["preco_lista_unitario"] = np.divide(
            data["preco_liquido_orcado_unitario"].to_numpy(),
            1 - base_discount.to_numpy(),
            out=data["preco_liquido_orcado_unitario"].to_numpy().copy(),
            where=(1 - base_discount.to_numpy()) > 0,
        )
    if "pressao_preco_pct" in data.columns:
        data["pressao_preco_pct"] = 0.0

    masks = {
        label: is_problem & is_recent & scenario.eq(label)
        for label in ISSUE_LABELS
    }
    cost_mask = masks["Aumento de custo"]
    price_mask = masks["Pressao de preco"]
    volume_mask = masks["Queda de volume"]
    combined_mask = masks["Deterioracao combinada"]

    data.loc[cost_mask, "custo_unitario_real"] *= 1.10
    data.loc[price_mask, "preco_liquido_unitario"] *= 0.93
    data.loc[volume_mask, "quantidade_real"] = np.rint(
        data.loc[volume_mask, "quantidade_orcada"] * 0.75
    )
    data.loc[combined_mask, "custo_unitario_real"] *= 1.08
    data.loc[combined_mask, "preco_liquido_unitario"] *= 0.96
    data.loc[combined_mask, "quantidade_real"] = np.rint(
        data.loc[combined_mask, "quantidade_orcada"] * 0.82
    )

    if "pressao_preco_pct" in data.columns:
        data.loc[price_mask, "pressao_preco_pct"] = 0.07
        data.loc[combined_mask, "pressao_preco_pct"] = 0.04

    data["receita_liquida_real"] = data["quantidade_real"] * data["preco_liquido_unitario"]
    data["custo_produtos_real"] = data["quantidade_real"] * data["custo_unitario_real"]
    data["lucro_bruto_real"] = data["receita_liquida_real"] - data["custo_produtos_real"]

    if "custo_variavel_adicional_orcado" in data.columns:
        data["custo_variavel_adicional_orcado"] = data["receita_liquida_orcada"] * variable_cost_rate
    if "margem_contribuicao_orcada" in data.columns:
        if "custo_variavel_adicional_orcado" in data.columns:
            data["margem_contribuicao_orcada"] = (
                data["lucro_bruto_orcado"] - data["custo_variavel_adicional_orcado"]
            )
    if "custo_variavel_adicional_real" in data.columns:
        data["custo_variavel_adicional_real"] = data["receita_liquida_real"] * variable_cost_rate
    if "margem_contribuicao_real" in data.columns:
        if "custo_variavel_adicional_real" in data.columns:
            data["margem_contribuicao_real"] = (
                data["lucro_bruto_real"] - data["custo_variavel_adicional_real"]
            )
        elif "margem_contribuicao_orcada" in data.columns:
            data["margem_contribuicao_real"] = (
                data["lucro_bruto_real"] - (data["lucro_bruto_orcado"] - data["margem_contribuicao_orcada"])
            )

    if "preco_lista_unitario" in data.columns:
        data["desconto_pct"] = np.where(
            data["preco_lista_unitario"] > 0,
            1 - data["preco_liquido_unitario"] / data["preco_lista_unitario"],
            0.0,
        ).clip(0, 0.99)
    elif "desconto_pct" in data.columns:
        data["desconto_pct"] = base_discount

    if "margem_bruta_real_pct" in data.columns:
        data["margem_bruta_real_pct"] = np.divide(
            data["lucro_bruto_real"].to_numpy(),
            data["receita_liquida_real"].to_numpy(),
            out=np.zeros(len(data), dtype=float),
            where=data["receita_liquida_real"].to_numpy() != 0,
        )
    if "margem_bruta_orcada_pct" in data.columns:
        data["margem_bruta_orcada_pct"] = np.divide(
            data["lucro_bruto_orcado"].to_numpy(),
            data["receita_liquida_orcada"].to_numpy(),
            out=np.zeros(len(data), dtype=float),
            where=data["receita_liquida_orcada"].to_numpy() != 0,
        )
    if "margem_contribuicao_real_pct" in data.columns and "margem_contribuicao_real" in data.columns:
        data["margem_contribuicao_real_pct"] = np.divide(
            data["margem_contribuicao_real"].to_numpy(),
            data["receita_liquida_real"].to_numpy(),
            out=np.zeros(len(data), dtype=float),
            where=data["receita_liquida_real"].to_numpy() != 0,
        )
    if "margem_contribuicao_orcada_pct" in data.columns and "margem_contribuicao_orcada" in data.columns:
        data["margem_contribuicao_orcada_pct"] = np.divide(
            data["margem_contribuicao_orcada"].to_numpy(),
            data["receita_liquida_orcada"].to_numpy(),
            out=np.zeros(len(data), dtype=float),
            where=data["receita_liquida_orcada"].to_numpy() != 0,
        )

    if "desvio_receita_vs_orcado" in data.columns:
        data["desvio_receita_vs_orcado"] = data["receita_liquida_real"] - data["receita_liquida_orcada"]
    if "desvio_lucro_bruto_vs_orcado" in data.columns:
        data["desvio_lucro_bruto_vs_orcado"] = data["lucro_bruto_real"] - data["lucro_bruto_orcado"]
    if "desvio_margem_bruta_pp" in data.columns:
        real_margin = np.divide(
            data["lucro_bruto_real"].to_numpy(),
            data["receita_liquida_real"].to_numpy(),
            out=np.zeros(len(data), dtype=float),
            where=data["receita_liquida_real"].to_numpy() != 0,
        )
        budget_margin = np.divide(
            data["lucro_bruto_orcado"].to_numpy(),
            data["receita_liquida_orcada"].to_numpy(),
            out=np.zeros(len(data), dtype=float),
            where=data["receita_liquida_orcada"].to_numpy() != 0,
        )
        data["desvio_margem_bruta_pp"] = (real_margin - budget_margin) * 100

    # Hard validations: no duplicates, exactly 2,000 issue SKUs, reconciled profit,
    # and negative profit gaps only for those 2,000 SKUs in the full history.
    if data.duplicated(["mes", "sku_id"]).any():
        raise ValueError("Há registros duplicados para o mesmo SKU e mês.")
    scenario_counts = data[["sku_id", "cenario_simulado"]].drop_duplicates("sku_id")["cenario_simulado"].value_counts()
    if int(scenario_counts.get("Sem desvio induzido", 0)) != TOTAL_SKUS - PROBLEM_SKUS:
        raise ValueError("A base deve conter exatamente 6.000 SKUs sem desvio induzido.")
    for label in ISSUE_LABELS:
        if int(scenario_counts.get(label, 0)) != PROBLEM_SKUS // len(ISSUE_LABELS):
            raise ValueError(f"O cenário '{label}' não tem a quantidade planejada de SKUs.")
    reconciliation = (
        data["receita_liquida_real"] - data["custo_produtos_real"] - data["lucro_bruto_real"]
    ).abs().max()
    if not np.isfinite(reconciliation) or reconciliation > 0.01:
        raise ValueError(f"Falha na conciliação de lucro bruto (diferença máxima: {reconciliation}).")

    if {"custo_variavel_adicional_real", "margem_contribuicao_real"}.issubset(data.columns):
        contribution_reconciliation = (
            data["lucro_bruto_real"]
            - data["custo_variavel_adicional_real"]
            - data["margem_contribuicao_real"]
        ).abs().max()
        if not np.isfinite(contribution_reconciliation) or contribution_reconciliation > 0.01:
            raise ValueError(
                "Falha na conciliação da margem de contribuição "
                f"(diferença máxima: {contribution_reconciliation})."
            )

    clean = data["cenario_simulado"].eq("Sem desvio induzido")
    for actual_col, budget_col in (
        ("receita_liquida_real", "receita_liquida_orcada"),
        ("custo_produtos_real", "custo_produtos_orcado"),
        ("lucro_bruto_real", "lucro_bruto_orcado"),
    ):
        clean_gap = (
            data.loc[clean, actual_col] - data.loc[clean, budget_col]
        ).abs().max()
        if not np.isfinite(clean_gap) or clean_gap > 0.01:
            raise ValueError(
                f"Os SKUs sem desvio induzido têm diferença inesperada em {actual_col}: {clean_gap}."
            )

    sku_gaps = data.groupby("sku_id")["lucro_bruto_real"].sum() - data.groupby("sku_id")["lucro_bruto_orcado"].sum()
    negative_count = int((sku_gaps < -0.01).sum())
    if negative_count != PROBLEM_SKUS:
        raise ValueError(f"Esperados {PROBLEM_SKUS} SKUs com gap negativo; encontrados {negative_count}.")

    return data
