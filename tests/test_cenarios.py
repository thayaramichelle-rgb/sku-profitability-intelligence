import unittest

import numpy as np
import pandas as pd

from cenarios import (
    ISSUE_LABELS,
    aplicar_cenarios_controlados,
    calcular_simulacao_recuperacao_margem,
)


def synthetic_history():
    """Build a deterministic 8,000-SKU, 24-month dataset for calculation tests."""
    rng = np.random.default_rng(123)
    sku_count = 8_000
    month_count = 24
    months = pd.date_range("2024-01-01", periods=month_count, freq="MS")
    sku_num = np.repeat(np.arange(1, sku_count + 1), month_count)
    month_num = np.tile(np.arange(month_count), sku_count)

    families = np.array([
        "Chapas", "Bobinas", "Perfis", "Extrudados",
        "Componentes", "Laminados", "Outros industriais",
    ])
    segments = np.array(["Industrial", "Distribuicao", "Grandes contas", "PME"])
    family_by_sku = rng.choice(families, size=sku_count)
    segment_by_sku = rng.choice(segments, size=sku_count)
    price_base = rng.uniform(100, 700, size=sku_count)
    cost_ratio = rng.uniform(0.50, 0.78, size=sku_count)
    quantity_base = rng.integers(50, 1_000, size=sku_count)

    quantity_budget = np.maximum(
        1, np.rint(np.repeat(quantity_base, month_count) * (1 + 0.002 * month_num))
    )
    price_budget = np.repeat(price_base, month_count) * (1 + 0.001 * month_num)
    cost_budget = price_budget * np.repeat(cost_ratio, month_count)
    revenue_budget = quantity_budget * price_budget
    product_cost_budget = quantity_budget * cost_budget
    gross_profit_budget = revenue_budget - product_cost_budget
    variable_cost_budget = revenue_budget * 0.03
    contribution_budget = gross_profit_budget - variable_cost_budget
    discount = np.full(len(sku_num), 0.05)

    return pd.DataFrame({
        "mes": np.tile(months, sku_count),
        "sku_id": np.char.add("SKU-", np.char.zfill(sku_num.astype(str), 5)),
        "familia": np.repeat(family_by_sku, month_count),
        "segmento": np.repeat(segment_by_sku, month_count),
        "cenario_simulado": "Sem desvio induzido",
        "quantidade_real": quantity_budget.copy(),
        "quantidade_orcada": quantity_budget,
        "preco_lista_unitario": price_budget / (1 - discount),
        "desconto_pct": discount,
        "pressao_preco_pct": np.zeros(len(sku_num)),
        "preco_liquido_unitario": price_budget.copy(),
        "preco_liquido_orcado_unitario": price_budget,
        "custo_unitario_real": cost_budget.copy(),
        "custo_unitario_orcado": cost_budget,
        "receita_liquida_real": revenue_budget.copy(),
        "receita_liquida_orcada": revenue_budget,
        "custo_produtos_real": product_cost_budget.copy(),
        "custo_produtos_orcado": product_cost_budget,
        "lucro_bruto_real": gross_profit_budget.copy(),
        "lucro_bruto_orcado": gross_profit_budget,
        "custo_variavel_adicional_real": variable_cost_budget.copy(),
        "custo_variavel_adicional_orcado": variable_cost_budget,
        "margem_contribuicao_real": contribution_budget.copy(),
        "margem_contribuicao_orcada": contribution_budget,
        "margem_bruta_real_pct": gross_profit_budget / revenue_budget,
        "margem_bruta_orcada_pct": gross_profit_budget / revenue_budget,
        "margem_contribuicao_real_pct": contribution_budget / revenue_budget,
        "margem_contribuicao_orcada_pct": contribution_budget / revenue_budget,
        "desvio_receita_vs_orcado": np.zeros(len(sku_num)),
        "desvio_lucro_bruto_vs_orcado": np.zeros(len(sku_num)),
        "desvio_margem_bruta_pp": np.zeros(len(sku_num)),
    })


class ControlledScenarioTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.history = aplicar_cenarios_controlados(synthetic_history())

    def test_exactly_2000_problem_skus_and_500_per_cause(self):
        per_sku = self.history[["sku_id", "familia", "segmento", "cenario_simulado"]].drop_duplicates("sku_id")
        counts = per_sku["cenario_simulado"].value_counts()
        self.assertEqual(int(counts.get("Sem desvio induzido", 0)), 6_000)
        for label in ISSUE_LABELS:
            self.assertEqual(int(counts.get(label, 0)), 500)
        self.assertEqual(per_sku.loc[per_sku["cenario_simulado"] != "Sem desvio induzido", "sku_id"].nunique(), 2_000)

        by_stratum = per_sku.groupby(["familia", "segmento"], dropna=False).agg(
            total=("sku_id", "nunique"),
            affected=("cenario_simulado", lambda s: int((s != "Sem desvio induzido").sum())),
        )
        self.assertTrue(((by_stratum["affected"] - by_stratum["total"] * 0.25).abs() <= 1).all())

    def test_only_problem_skus_have_negative_gross_profit_gap(self):
        gap = (
            self.history.groupby("sku_id")["lucro_bruto_real"].sum()
            - self.history.groupby("sku_id")["lucro_bruto_orcado"].sum()
        )
        self.assertEqual(int((gap < -0.01).sum()), 2_000)
        clean = self.history[self.history["cenario_simulado"] == "Sem desvio induzido"]
        self.assertTrue(np.allclose(clean["receita_liquida_real"], clean["receita_liquida_orcada"], atol=0.01))
        self.assertTrue(np.allclose(clean["custo_produtos_real"], clean["custo_produtos_orcado"], atol=0.01))
        self.assertTrue(np.allclose(clean["lucro_bruto_real"], clean["lucro_bruto_orcado"], atol=0.01))

    def test_financial_identities_reconcile(self):
        self.assertTrue(np.allclose(
            self.history["receita_liquida_real"] - self.history["custo_produtos_real"],
            self.history["lucro_bruto_real"],
            atol=0.01,
        ))
        self.assertTrue(np.allclose(
            self.history["lucro_bruto_real"] - self.history["custo_variavel_adicional_real"],
            self.history["margem_contribuicao_real"],
            atol=0.01,
        ))
        self.assertEqual(self.history["mes"].nunique(), 24)
        self.assertEqual(self.history["sku_id"].nunique(), 8_000)

    def test_zero_price_recovery_cannot_reduce_volume_or_profit(self):
        data = pd.DataFrame({
            "sku_id": ["A", "B", "C"],
            "quantidade_real": [100, 50, 80],
            "preco_liquido_unitario": [90.0, 100.0, 120.0],
            "preco_liquido_orcado_unitario": [100.0, 100.0, 110.0],
            "custo_unitario_real": [60.0, 60.0, 70.0],
        })
        result = calcular_simulacao_recuperacao_margem(data, 0, 80)
        self.assertTrue(np.allclose(result["volume_cenario_sim"], result["volume_base_sim"]))
        self.assertTrue(np.allclose(result["variacao_receita_sim"], 0))
        self.assertTrue(np.allclose(result["variacao_lucro_sim"], 0))

    def test_full_recovery_with_full_retention_matches_gap_times_volume(self):
        data = pd.DataFrame({
            "sku_id": ["A", "B", "C"],
            "quantidade_real": [100, 50, 80],
            "preco_liquido_unitario": [90.0, 100.0, 120.0],
            "preco_liquido_orcado_unitario": [100.0, 100.0, 110.0],
            "custo_unitario_real": [60.0, 60.0, 70.0],
        })
        result = calcular_simulacao_recuperacao_margem(data, 100, 100)
        expected = np.maximum(
            data["preco_liquido_orcado_unitario"] - data["preco_liquido_unitario"], 0
        ) * data["quantidade_real"]
        self.assertTrue(np.allclose(result["variacao_receita_sim"], expected))
        self.assertTrue(np.allclose(result["variacao_lucro_sim"], expected))

    def test_volume_retention_only_applies_when_price_is_adjusted(self):
        data = pd.DataFrame({
            "sku_id": ["gap", "no_gap"],
            "quantidade_real": [100, 80],
            "preco_liquido_unitario": [90.0, 120.0],
            "preco_liquido_orcado_unitario": [100.0, 110.0],
            "custo_unitario_real": [60.0, 70.0],
        })
        result = calcular_simulacao_recuperacao_margem(data, 50, 90)
        self.assertAlmostEqual(result.loc[0, "volume_cenario_sim"], 90)
        self.assertAlmostEqual(result.loc[1, "volume_cenario_sim"], 80)


if __name__ == "__main__":
    unittest.main()
