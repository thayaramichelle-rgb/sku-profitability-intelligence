# SKU Profitability Intelligence

Dashboard analítico em Python, Pandas, Plotly e Streamlit para investigar rentabilidade por SKU, desvios frente ao orçamento, pressão de preço, volume, custos e oportunidades comerciais.

**Aplicativo:** https://sku-profitability-intelligence.streamlit.app/

## Escopo da base demonstrativa

- 8.000 SKUs sintéticos, distribuídos entre famílias e segmentos.
- Histórico mensal de 24 meses.
- Exatamente 2.000 SKUs com desvios de rentabilidade induzidos, estratificados proporcionalmente entre família e segmento.
- 6.000 SKUs permanecem alinhados ao orçamento.
- Os desvios aparecem nos seis meses finais e são divididos em quatro grupos de 500 SKUs: aumento de custo, pressão de preço, queda de volume e deterioração combinada.

Os dados são inteiramente fictícios e não representam dados de nenhuma empresa. As oportunidades e simulações são indicativas, não previsões de recuperação garantida.

## Validações financeiras

A rotina `cenarios.py` reconcilia os totais com preço, volume e custo unitário e valida que:

1. Receita realizada = volume realizado × preço líquido realizado.
2. Custo dos produtos = volume realizado × custo unitário realizado.
3. Lucro bruto = receita líquida − custo dos produtos.
4. Margem de contribuição = lucro bruto − custos variáveis adicionais representados na base.
5. Apenas os 2.000 SKUs definidos no cenário apresentam gap negativo de lucro bruto no histórico completo.
6. Não há duplicidade de chave SKU + mês.

O simulador de recuperação de margem considera o percentual de gap de preço recuperado e a retenção de volume escolhida. Com recuperação de preço em 0%, o cenário não aplica perda de volume.

## Executar localmente

Instale as dependências listadas em `requirements.txt` e execute:

```bash
streamlit run app.py
```

Para regenerar o cadastro e o histórico sintético:

```bash
python gerar_base.py
```

## Testes automáticos

Os testes verificam a distribuição dos cenários, a reconciliação das métricas e o comportamento do simulador:

```bash
python -m pip install numpy pandas
python -m py_compile app.py gerar_base.py cenarios.py tests/test_cenarios.py
python -m unittest discover -s tests -v
```

O GitHub Actions executa essas validações automaticamente em atualizações da branch principal.
