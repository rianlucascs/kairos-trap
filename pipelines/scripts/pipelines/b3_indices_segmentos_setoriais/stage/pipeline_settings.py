"""
Settings:
    pipeline_settings

Responsabilidades:
    ...
    
Notas:
    ...
"""

url: str = f"https://sistemaswebb3-listados.b3.com.br/indexProxy/indexCall/GetPortfolioDay/{{encoded}}"


b3_indices_segmentos_setoriais: list[str] = [
    "IDIV", "MLCX", "SMLL", "IVBX", "AGFS", "IFNC", "IBEP", "IBEE", "IBHB", "IFIX",
    "IBLV", "IMOB", "UTIL", "ICON", "IEEX", "IFIL", "IMAT", "INDX", "IBSD", "BDRX",
]

