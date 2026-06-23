import pandas as pd

def load_data(filepath: str):
    """
    Carrega a planilha e separa em duas camadas:
    - df_compras: orçamento total dos contratos
    - df_pagamentos: parcelas e fluxo de caixa real
    """
    df = pd.read_excel(filepath, dtype={"Req. MXM": str, "Doc Fiscal": str})

    # Limpeza e padronização
    df["Tipo"] = df["Tipo"].astype(str).str.strip().str.title()
    df["Status"] = df["Status"].astype(str).str.strip()
    df["Fornecedor"] = df["Fornecedor"].astype(str).str.strip()
    df["Valor"] = pd.to_numeric(df["Valor"], errors="coerce").fillna(0)
    df["Data pgto"] = pd.to_datetime(df["Data pgto"], errors="coerce", dayfirst=True)
    df["Término Contrato"] = pd.to_datetime(df["Término Contrato"], errors="coerce", dayfirst=True)
    df["Dias vencimento"] = pd.to_numeric(df["Dias vencimento"], errors="coerce").fillna(0)

    # Separação crucial — evita duplicidade de valores
    df_compras = df[df["Tipo"] == "Compra"].copy()
    df_pagamentos = df[df["Tipo"] == "Pagamento"].copy()

    return df_compras, df_pagamentos
