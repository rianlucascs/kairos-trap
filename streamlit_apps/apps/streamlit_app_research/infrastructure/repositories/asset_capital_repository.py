
from pipelines.readers.pipelines.cvm_formulario_de_referencia.reader_parquet import ReaderSnapshotParquet as fre
from streamlit_apps.apps.streamlit_app_research.infrastructure.repositories.asset_repository import AssetRepository

from pandas import DataFrame, to_numeric


class AssetCapitalRepository:
    """
    Fornece acesso a capital social (nº de ações) e dividendos distribuídos, a partir do
    Formulário de Referência (CVM), que é indexado por CNPJ, não por CD_CVM.
    """


    def __init__(self) -> None:

        self.asset_repository = AssetRepository()


    def _resolve_cnpj(self, cd_cvm: str) -> str:

        cadastral = self.asset_repository.get_cadastral_data()
        match = cadastral[cadastral["CD_CVM"].astype(str).astype(int) == int(cd_cvm)]

        if match.empty:
            raise ValueError(f"CNPJ não encontrado para cd_cvm={cd_cvm!r}.")

        return match["CNPJ_CIA"].iloc[0]


    def get_quantidade_total_acoes(self, cd_cvm: str) -> DataFrame:

        cnpj = self._resolve_cnpj(cd_cvm)
        empresa = fre(file_identifiers="capital_social").read().pipe(lambda df: df[df["CNPJ_Companhia"] == cnpj])

        # Prioriza "Capital Emitido" (nº de ações emitidas, base usual de mercado); usa
        # alternativas apenas se a companhia não reportar esse tipo em nenhum período.
        for tipo_capital in ("Capital Emitido", "Capital Subscrito", "Capital Integralizado"):

            filtrado = empresa[empresa["Tipo_Capital"] == tipo_capital]

            if not filtrado.empty:
                break

        else:
            raise ValueError(f"Nenhum registro de capital social encontrado para cd_cvm={cd_cvm!r}.")

        return (
            filtrado
            .sort_values("Data_Referencia")
            .drop_duplicates(subset=["Data_Referencia"], keep="last")
            [["Data_Referencia", "Quantidade_Total_Acoes"]]
            .rename(columns={"Data_Referencia": "DT_REFER", "Quantidade_Total_Acoes": "VL_CONTA_TRI"})
            .reset_index(drop=True)
        )


    def get_dividendos_pagos(self, cd_cvm: str) -> DataFrame:

        cnpj = self._resolve_cnpj(cd_cvm)
        empresa = fre(file_identifiers="distribuicao_dividendos").read().pipe(lambda df: df[df["CNPJ_Companhia"] == cnpj])

        return (
            empresa
            .sort_values("Data_Referencia")
            # cada FRE anual reporta o exercício do próprio ano e alguns anteriores; mantém a
            # versão mais recente (Data_Referencia mais alta) de cada exercício (Data_Fim_Exercicio_Social).
            .drop_duplicates(subset=["Data_Fim_Exercicio_Social"], keep="last")
            [["Data_Fim_Exercicio_Social", "Dividendo_Distribuido_Total"]]
            .rename(columns={"Data_Fim_Exercicio_Social": "DT_REFER", "Dividendo_Distribuido_Total": "VL_CONTA_TRI"})
            .assign(VL_CONTA_TRI=lambda df: to_numeric(df["VL_CONTA_TRI"], errors="coerce"))
            .sort_values("DT_REFER")
            .reset_index(drop=True)
        )
