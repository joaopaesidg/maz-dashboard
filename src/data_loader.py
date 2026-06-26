import pandas as pd

def load_data(filepath: str):
    df = pd.read_excel(filepath, dtype=str)

    # Normaliza os nomes das colunas (remove espaços e padroniza maiúsculas)
    df.columns = df.columns.str.strip()

    # Renomeia colunas para os nomes esperados (ajuste se necessário)
    df.columns = [c.strip() for c in df.columns]

    df["Valor"] = pd.to_numeric(df["Valor"], errors="coerce").fillna(0)
    df["Data pgto"] = pd.to_datetime(df["Data pgto"], errors="coerce", dayfirst=True)
    df["Término Contrato"] = pd.to_datetime(df["Término Contrato"], errors="coerce", dayfirst=True)
    df["Dias vencimento"] = pd.to_numeric(df["Dias vencimento"], errors="coerce").fillna(0)

    df["Tipo"] = df["Tipo"].astype(str).str.strip().str.title()
    df["Status"] = df["Status"].astype(str).str.strip()
    df["Fornecedor"] = df["Fornecedor"].astype(str).str.strip()

    df_compras = df[df["Tipo"] == "Compra"].copy()
    df_pagamentos = df[df["Tipo"] == "Pagamento"].copy()

    return df_compras, df_pagamentos
