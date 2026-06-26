import pandas as pd

def load_data(filepath: str):
    # header=2 pula as 2 primeiras linhas (título e data) e usa a linha 3 como cabeçalho
    df = pd.read_excel(filepath, header=2, dtype={"Req. MXM": str, "Doc Fiscal": str})

    # Normaliza os nomes das colunas
    df.columns = df.columns.str.strip()

    # Remove linhas completamente vazias
    df = df.dropna(how="all")

    df["Tipo"] = df["Tipo"].astype(str).str.strip().str.title()
    df["Status"] = df["Status"].astype(str).str.strip()
    df["Fornecedor"] = df["Fornecedor"].astype(str).str.strip()
    df["Valor"] = pd.to_numeric(df["Valor"], errors="coerce").fillna(0)
    df["Data pgto"] = pd.to_datetime(df["Data pgto"], errors="coerce", dayfirst=True)
    df["Término Contrato"] = pd.to_datetime(df["Término Contrato"], errors="coerce", dayfirst=True)
    df["Dias vencimento"] = pd.to_numeric(df["Dias vencimento"], errors="coerce").fillna(0)

    df_compras = df[df["Tipo"] == "Compra"].copy()
    df_pagamentos = df[df["Tipo"] == "Pagamento"].copy()

    return df_compras, df_pagamentos
