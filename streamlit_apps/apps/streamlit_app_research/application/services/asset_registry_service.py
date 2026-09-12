

from streamlit_apps.apps.streamlit_app_research.infrastructure.repositories import *


from pandas import DataFrame
from dataclasses import dataclass



@dataclass(frozen=True)
class AssetRegistryDTO:
    
    ticker: str
    isin: str | None = None
    cd_cvm: str | None = None
    company_name: str | None = None
    website: str | None = None
    industry_classification: str | None = None
    activity: str | None = None
    cnpj_cia: str | None = None
    denom_social: str | None = None
    denom_comerc: str | None = None
    sit: str | None = None
    dt_ini_sit: str | None = None
    setor_ativ: str | None = None
    categ_reg: str | None = None
    controle_acionario: str | None = None


MANUAL_TRADING_CODES: list[AssetRegistryDTO] = [
    AssetRegistryDTO(
        ticker="^BVSP",
        isin=None,
        cd_cvm=None,
        company_name=None,
        website=None,
        industry_classification=None,
        activity=None,
        cnpj_cia=None,
        denom_social=None,
        denom_comerc=None,
        sit=None,
        dt_ini_sit=None,
        setor_ativ=None,
        categ_reg=None,
        controle_acionario=None,
    )
]


class AssetRegistryService:
    """Serviço que gerencia o registro de ativos e informações cadastrais das empresas."""
    
    def __init__(
        self
    ) -> None:

        b3_enriquecimento_cadastral_ativos_repository = B3EnriquecimentoCadastralAtivosRepository
        self.codes: DataFrame = b3_enriquecimento_cadastral_ativos_repository("codigos.parquet").read()
        self.company: DataFrame = b3_enriquecimento_cadastral_ativos_repository("empresas.parquet").read()
        
        self.cvm_cias_cad: DataFrame = CVMCIASAbertasInformacaoCadastralRepository().read()
        
        self.df: DataFrame
        
    
    def add_company_names(self) -> "AssetRegistryService":
        """
        Adiciona os nomes das empresas aos códigos de ativos.
        """
        
        company_names = (
            self.company
            .groupby("codeCVM")[["companyName", "website", "industryClassification", "activity"]]
            .agg(tuple)
            .reset_index()
        )

        data = self.codes.merge(
            company_names,
            how="left",
            on="codeCVM",
            validate="many_to_one",
        ).rename(columns={"codeCVM": "CD_CVM"})
        
        self.df = data
        
        return self
    
    
    def add_cvm_cias_cad(self) -> "AssetRegistryService":
        """
        Adiciona as informações cadastrais da CVM às empresas.
        """
        
        cvm_cias_cad_dedup = (
            self.cvm_cias_cad
            .sort_values("DT_INI_SIT", ascending=False)
            .drop_duplicates(subset="CD_CVM", keep="first")
        )   
        
        data = self.df.merge(
            cvm_cias_cad_dedup[["CD_CVM", "CNPJ_CIA", "DENOM_SOCIAL", "DENOM_COMERC",
                               "SIT", "DT_INI_SIT", "SETOR_ATIV", "CATEG_REG", "CONTROLE_ACIONARIO"
                               ]],
            how="left",
            on="CD_CVM",
            validate="many_to_one",
        )
        
        self.df = data
        
        return self
    
    
    def to_dto_list(self) -> list[AssetRegistryDTO]:
        """
        Converte o DataFrame final em uma lista de DTOs.
        """
        return MANUAL_TRADING_CODES + [
            AssetRegistryDTO(
                ticker=row.code+".SA",
                isin=row["isin"],
                cd_cvm=row.CD_CVM,
                company_name=row.companyName,
                website=row.website,
                industry_classification=row.industryClassification,
                activity=row.activity,
                cnpj_cia=row.CNPJ_CIA,
                denom_social=row.DENOM_SOCIAL,
                denom_comerc=row.DENOM_COMERC,
                sit=row.SIT,
                dt_ini_sit=row.DT_INI_SIT,
                setor_ativ=row.SETOR_ATIV,
                categ_reg=row.CATEG_REG,
                controle_acionario=row.CONTROLE_ACIONARIO,
            )
            for _, row in self.df.iterrows()
        ]
    

if __name__ == "__main__":
    
    service = AssetRegistryService()
    #print(service.company.columns)
    service.add_company_names().add_cvm_cias_cad()
    print(service.to_dto_list())
