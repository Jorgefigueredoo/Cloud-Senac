import numpy as np
import pandas as pd

rng = np.random.default_rng(42)
n = 5000

cidades = ["Recife", "Olinda", "Caruaru", "Petrolina", "Garanhuns"]
produtos = {
    "Bebidas": [("Café", 6.0), ("Suco de caju", 8.0), ("Caldo de cana", 7.0)],
    "Salgados": [("Coxinha", 7.5), ("Pastel", 8.0), ("Tapioca", 12.0)],
    "Doces": [("Bolo de rolo", 9.0), ("Cartola", 14.0), ("Cocada", 5.0)],
    "Pratos": [("Cuscuz com carne de sol", 22.0), ("Baião de dois", 28.0),
               ("Macaxeira com charque", 25.0)],
}
itens = [(cat, prod, preco) for cat, lista in produtos.items() for prod, preco in lista]
idx = rng.integers(0, len(itens), n)
datas = pd.to_datetime("2025-01-01") + pd.to_timedelta(rng.integers(0, 365, n), unit="D")
df = pd.DataFrame({
    "data": datas.strftime("%Y-%m-%d"),
    "hora": rng.integers(7, 22, n),
    "cidade": rng.choice(cidades, n, p=[0.35, 0.15, 0.2, 0.2, 0.1]),
    "categoria": [itens[i][0] for i in idx],
    "produto": [itens[i][1] for i in idx],
    "preco_unitario": [itens[i][2] for i in idx],
    "quantidade": rng.integers(1, 6, n),
    "pagamento": rng.choice(["Pix", "Crédito", "Débito", "Dinheiro"], n,
                            p=[0.45, 0.25, 0.2, 0.1]),
    "avaliacao": rng.integers(1, 6, n).astype(float),
})
df["total"] = (df["preco_unitario"] * df["quantidade"]).round(2)

df.loc[rng.choice(n, 60, replace=False), "avaliacao"] = np.nan

df.sort_values(["data", "hora"]).to_csv("vendas_sabor_do_sertao.csv", index=False)
print("Arquivo gerado:", len(df), "linhas")
