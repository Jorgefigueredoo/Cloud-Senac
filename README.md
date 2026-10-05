# Painel de Vendas: Sabor do Sertão

Painel interativo em Streamlit para analisar um ano de vendas da rede fictícia de lanchonetes Sabor do Sertão (Recife, Olinda, Caruaru, Petrolina e Garanhuns).

![Print do painel](print_painel.png)

## Como rodar

```bash
pip install -r requirements.txt
python gerar_dados.py      # gera vendas_sabor_do_sertao.csv
streamlit run app.py
```

Na barra lateral, envie o arquivo `vendas_sabor_do_sertao.csv`.

## O que o painel faz

- **Exploração:** primeiras linhas, resumo estatístico e valores ausentes por coluna. Os ausentes de `avaliacao` são preenchidos com a mediana (justificativa no próprio painel).
- **Indicadores:** faturamento total, número de vendas, ticket médio e avaliação média.
- **Filtros:** cidade, categoria e intervalo de datas. KPIs, gráficos, insights e exportação reagem aos filtros.
- **Gráficos:** faturamento mensal, faturamento por cidade, top 5 produtos, formas de pagamento e mapa de calor por dia da semana e hora.
- **Insights:** três conclusões para o gestor e botão para baixar o CSV filtrado.
- **Explorador livre:** aceita qualquer CSV e permite escolher eixo X, eixo Y e tipo de gráfico.

## Arquivos

| Arquivo | Descrição |
|---|---|
| `app.py` | Aplicação Streamlit |
| `gerar_dados.py` | Gera o CSV de vendas (semente fixa) |
| `requirements.txt` | Dependências |

## Dupla

- Nome: Jorge Antonio de Lima Figueredo
- Nome: Ygor Sampaio
