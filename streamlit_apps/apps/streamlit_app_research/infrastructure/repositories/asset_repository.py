

from pipelines.readers.pipelines.b3_enriquecimento_cadastral_ativos.reader_parquet import ReaderSnapshotParquet as b3_cad
from pipelines.readers.pipelines.cvm_cias_abertas_informacao_cadastral.reader_parquet import ReaderSnapshotParquet as cvm_cad
from streamlit_apps.apps.streamlit_app_research.shared.dto.asset_dto import AssetTradingCodeDTO

from pandas import DataFrame


class AssetRepository:
    """
    Fornece acesso somente-leitura aos metadados cadastrais dos ativos
    (nome, ticker, setor, CNPJ, tipo de ativo, etc.), agregando dados
    provenientes das pipelines CVM/BCB já processadas.
    """
    
    
    def __init__(
        self
    ) -> None:
        
        self._codes: DataFrame | None = None
        self._companies: DataFrame | None = None
        self._cvm_cadastral: DataFrame | None = None


    def get_codes(self) -> DataFrame:
        
        if self._codes is None:
            
            self._codes = b3_cad(
                file_identifiers="codigos.parquet"
            ).read()

        return self._codes


    def get_companies(self) -> DataFrame:
        
        if self._companies is None:
            self._companies = b3_cad(
                file_identifiers="empresas.parquet"
            ).read()

        return self._companies


    def get_cadastral_data(self) -> DataFrame:
        
        if self._cvm_cadastral is None:
            self._cvm_cadastral = cvm_cad().read()

        return self._cvm_cadastral
    
    
    def list_trading_codes(self) -> list[AssetTradingCodeDTO]:
        codes = self.get_codes()
        companies = self.get_companies()

        company_names = (
            companies
            .groupby("codeCVM")["companyName"]
            .agg(list)
            .reset_index()
        )

        data = codes.merge(
            company_names,
            how="left",
            on="codeCVM",
            validate="many_to_one",
        )

        return [
            AssetTradingCodeDTO(
                trading_code=row.code,
                cvm_code=row.codeCVM,
                company_name=row.companyName,
            )
            for row in data[["code", "codeCVM", "companyName"]].itertuples(index=False)
        ]
        
    

