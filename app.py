import pandas as pd
import plotly.express as px
import streamlit as st

st.set_page_config(page_title="Sabor do Sertão", layout="wide")
st.title("Painel de Vendas: Sabor do Sertão")


@st.cache_data
def carregar(arquivo):
    return pd.read_csv(arquivo, parse_dates=["data"])


def brl(valor):
    """Formata número no padrão brasileiro: R$ 1.234,56"""
    return "R$ " + f"{valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


arquivo = st.sidebar.file_uploader("Envie o CSV de vendas", type="csv")
if arquivo is None:
    st.info("Envie o arquivo para começar.")
    st.stop()

df = carregar(arquivo)

# ---------------------------------------------------------------------------
# NÍVEL 1: Exploração
# ---------------------------------------------------------------------------
st.header("1. Exploração dos dados")

with st.expander("Ver exploração inicial", expanded=False):
    st.subheader("Primeiras linhas")
    st.dataframe(df.head(10))

    col_a, col_b = st.columns([2, 1])
    with col_a:
        st.subheader("Resumo estatístico")
        st.dataframe(df.describe(include="number"))
    with col_b:
        st.subheader("Valores ausentes por coluna")
        st.dataframe(df.isna().sum().rename("ausentes"))

# Tratamento dos ausentes em "avaliacao"
n_ausentes = int(df["avaliacao"].isna().sum())
mediana = df["avaliacao"].median()
pct_ausentes = f"{n_ausentes / len(df):.1%}".replace(".", ",")
df["avaliacao"] = df["avaliacao"].fillna(mediana)

st.caption(
    f"Tratamento: a coluna `avaliacao` tinha {n_ausentes} valores ausentes "
    f"({pct_ausentes} das linhas), preenchidos com a mediana ({mediana:.0f}). "
    "Não removemos as linhas porque cada uma é uma venda real e apagá-las reduziria o "
    "faturamento e o número de vendas. Escolhemos a mediana em vez da média porque a nota "
    "é uma escala de 1 a 5 em números inteiros: a mediana é sempre uma nota válida e é "
    "menos sensível a valores extremos."
)

# ---------------------------------------------------------------------------
# NÍVEL 3: Filtros (definidos antes dos KPIs para que tudo reaja a eles)
# ---------------------------------------------------------------------------
st.sidebar.header("Filtros")

cidades_opcoes = sorted(df["cidade"].unique())
cidades_sel = st.sidebar.multiselect("Cidade", cidades_opcoes, default=cidades_opcoes)

categorias_opcoes = sorted(df["categoria"].unique())
categorias_sel = st.sidebar.multiselect("Categoria", categorias_opcoes, default=categorias_opcoes)

data_min, data_max = df["data"].min().date(), df["data"].max().date()
periodo = st.sidebar.date_input(
    "Intervalo de datas",
    value=(data_min, data_max),
    min_value=data_min,
    max_value=data_max,
    format="DD/MM/YYYY",
)
# Enquanto o usuário escolheu só a primeira data, o widget devolve 1 elemento
if isinstance(periodo, (list, tuple)) and len(periodo) == 2:
    inicio, fim = periodo
else:
    st.sidebar.warning("Selecione a data inicial e a data final.")
    st.stop()

df_f = df[
    df["cidade"].isin(cidades_sel)
    & df["categoria"].isin(categorias_sel)
    & (df["data"].dt.date >= inicio)
    & (df["data"].dt.date <= fim)
].copy()

if df_f.empty:
    st.warning("Nenhuma venda encontrada com os filtros selecionados.")
    st.stop()

# ---------------------------------------------------------------------------
# NÍVEL 2: Indicadores
# ---------------------------------------------------------------------------
st.header("2. Indicadores")

faturamento = df_f["total"].sum()
n_vendas = len(df_f)
ticket_medio = faturamento / n_vendas
avaliacao_media = df_f["avaliacao"].mean()

k1, k2, k3, k4 = st.columns(4)
k1.metric("Faturamento total", brl(faturamento))
k2.metric("Número de vendas", f"{n_vendas:,}".replace(",", "."))
k3.metric("Ticket médio", brl(ticket_medio))
k4.metric("Avaliação média", f"{avaliacao_media:.2f}".replace(".", ",") + " / 5")

# ---------------------------------------------------------------------------
# NÍVEL 4: Gráficos (+ bônus: explorador livre)
# ---------------------------------------------------------------------------
st.header("3. Gráficos")

aba_mes, aba_cidade, aba_prod, aba_pag, aba_calor, aba_livre = st.tabs(
    ["Faturamento mensal", "Por cidade", "Top 5 produtos", "Pagamentos",
     "Mapa de calor", "Explorador livre"]
)

with aba_mes:
    mensal = df_f.groupby(df_f["data"].dt.to_period("M"))["total"].sum()
    mensal.index = mensal.index.astype(str)
    mensal = mensal.reset_index()
    mensal.columns = ["mes", "total"]
    fig = px.line(
        mensal, x="mes", y="total", markers=True,
        title="Faturamento mensal",
        labels={"mes": "Mês", "total": "Faturamento (R$)"},
    )
    fig.update_xaxes(type="category")
    st.plotly_chart(fig)

with aba_cidade:
    por_cidade = (
        df_f.groupby("cidade")["total"].sum().sort_values(ascending=False).reset_index()
    )
    fig = px.bar(
        por_cidade, x="cidade", y="total", text_auto=".2s",
        title="Faturamento por cidade",
        labels={"cidade": "Cidade", "total": "Faturamento (R$)"},
    )
    st.plotly_chart(fig)

with aba_prod:
    top5 = df_f.groupby("produto")["quantidade"].sum().nlargest(5).sort_values().reset_index()
    fig = px.bar(
        top5, x="quantidade", y="produto", orientation="h", text_auto=True,
        title="Top 5 produtos mais vendidos (em quantidade)",
        labels={"quantidade": "Unidades vendidas", "produto": "Produto"},
    )
    st.plotly_chart(fig)

with aba_pag:
    pagamentos = df_f["pagamento"].value_counts().reset_index()
    pagamentos.columns = ["pagamento", "vendas"]
    fig = px.pie(
        pagamentos, names="pagamento", values="vendas", hole=0.35,
        title="Participação de cada forma de pagamento (nº de vendas)",
    )
    fig.update_traces(textinfo="percent+label")
    st.plotly_chart(fig)

with aba_calor:
    dias = ["Segunda", "Terça", "Quarta", "Quinta", "Sexta", "Sábado", "Domingo"]
    calor = df_f.assign(
        dia_semana=df_f["data"].dt.dayofweek.map(dict(enumerate(dias))),
        hora_txt=df_f["hora"].astype(int).astype(str).str.zfill(2) + "h",
    )
    fig = px.density_heatmap(
        calor, x="hora_txt", y="dia_semana",
        category_orders={"dia_semana": dias, "hora_txt": sorted(calor["hora_txt"].unique())},
        color_continuous_scale="YlOrRd", text_auto=True,
        title="Número de vendas por dia da semana e hora",
        labels={"hora_txt": "Hora", "dia_semana": "Dia da semana"},
    )
    fig.update_layout(coloraxis_colorbar_title="Vendas")
    st.plotly_chart(fig)

with aba_livre:
    st.write(
        "Envie qualquer CSV e monte o seu gráfico. "
        "Se nada for enviado, usamos as vendas já filtradas."
    )
    outro = st.file_uploader("CSV para explorar (opcional)", type="csv", key="livre")
    dados = df_f
    if outro is not None:
        try:
            dados = pd.read_csv(outro, sep=None, engine="python")
        except Exception as erro:
            st.error(f"Não foi possível ler o arquivo: {erro}")
            dados = None

    if dados is not None and not dados.empty:
        colunas = list(dados.columns)
        c1, c2, c3 = st.columns(3)
        eixo_x = c1.selectbox("Eixo X", colunas, index=0)
        eixo_y = c2.selectbox("Eixo Y", colunas, index=min(1, len(colunas) - 1))
        tipo = c3.selectbox(
            "Tipo de gráfico", ["Barras", "Linha", "Dispersão", "Boxplot", "Histograma"]
        )
        try:
            titulo = f"{tipo}: {eixo_y} por {eixo_x}"
            if tipo == "Barras":
                fig = px.bar(dados, x=eixo_x, y=eixo_y, title=titulo)
            elif tipo == "Linha":
                fig = px.line(dados.sort_values(eixo_x), x=eixo_x, y=eixo_y, title=titulo)
            elif tipo == "Dispersão":
                fig = px.scatter(dados, x=eixo_x, y=eixo_y, title=titulo)
            elif tipo == "Boxplot":
                fig = px.box(dados, x=eixo_x, y=eixo_y, title=titulo)
            else:
                st.caption("O histograma usa apenas o eixo X.")
                fig = px.histogram(dados, x=eixo_x, title=f"Histograma de {eixo_x}")
            st.plotly_chart(fig)
        except Exception as erro:
            st.error(f"Não foi possível montar esse gráfico com as colunas escolhidas: {erro}")
        with st.expander("Ver dados"):
            st.dataframe(dados.head(100))

# ---------------------------------------------------------------------------
# NÍVEL 5: Insights e exportação
# ---------------------------------------------------------------------------
st.header("4. Insights")

fat_cidade = df_f.groupby("cidade")["total"].sum().sort_values(ascending=False)
fat_categoria = df_f.groupby("categoria")["total"].sum().sort_values(ascending=False)
qtd_categoria = df_f.groupby("categoria")["quantidade"].sum()
pag = df_f["pagamento"].value_counts(normalize=True)
digitais = pag.reindex(["Pix", "Crédito", "Débito"]).fillna(0).sum()

cat_top = fat_categoria.index[0]

st.markdown(
    f"""
Conclusões para o período e os filtros selecionados:

- **Onde vendemos mais:** {fat_cidade.index[0]} lidera com {brl(fat_cidade.iloc[0])}
  ({fat_cidade.iloc[0] / faturamento:.0%} do faturamento), enquanto {fat_cidade.index[-1]}
  fica com {fat_cidade.iloc[-1] / faturamento:.0%}. Ações de marketing e reforço de equipe
  rendem mais na cidade líder; a última da lista merece uma análise de potencial.
- **O que sustenta o caixa:** a categoria {cat_top} gera {fat_categoria.iloc[0] / faturamento:.0%}
  do faturamento com {qtd_categoria[cat_top] / qtd_categoria.sum():.0%} das unidades vendidas.
  Itens de maior preço pesam mais na receita do que no volume, então combos que juntem
  bebidas, salgados ou doces a um prato tendem a elevar o ticket médio ({brl(ticket_medio)}).
- **Como o cliente paga:** {pag.index[0]} é a forma mais usada ({pag.iloc[0]:.0%} das vendas)
  e os meios eletrônicos somam {digitais:.0%}. Vale priorizar a estabilidade das maquininhas
  e do Pix e manter menos troco em caixa.
"""
)

st.download_button(
    "Baixar CSV filtrado",
    data=df_f.to_csv(index=False).encode("utf-8"),
    file_name="vendas_filtradas.csv",
    mime="text/csv",
)
