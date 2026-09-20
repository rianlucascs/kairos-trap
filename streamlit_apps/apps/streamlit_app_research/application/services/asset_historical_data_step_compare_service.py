


from streamlit_apps.apps.streamlit_app_research.infrastructure.repositories.historical_data_repository import HistoricalDataRepository

from typing import Literal
from datetime import date
from pandas import DataFrame

class AssetHistoricalDataStepCompareService:
    """Serviço para consultar as diferenças entre snapshots de dados históricos.

    Os arquivos de diferença são gerados na etapa COMPARE e representam:
    - ``added``: linhas presentes no snapshot atual, mas ausentes no anterior.
    - ``removed``: linhas presentes no snapshot anterior, mas ausentes no atual.
    - ``changed``: linhas presentes nos dois snapshots, mas com valores diferentes.
    """
    
    
    def __init__(self):
        
        pass
        
    
    def get_cvm_formulario_informacoes_trimestrais_by_cd_cvm(self, cd_cvm,  demonstration_code: Literal[
        'BPA_con', 'BPA_ind', 'BPP_con', 'BPP_ind', 'DFC_MD_con', 'DFC_MD_ind', 'DFC_MI_con', 'DFC_MI_ind', 'DMPL_con', 
        'DMPL_ind', 'DRA_con', 'DRA_ind', 'DRE_con', 'DRE_ind', 'DVA_con', 'DVA_ind'
        ], filename: Literal["added", "changed", "removed"],
    ) -> DataFrame:
        
        try:
            
            return (
                HistoricalDataRepository(
                    pipeline="cvm_formulario_informacoes_trimestrais",
                    snapshot_directory="snapshot_drift",
                    foldername=f"itr_cia_aberta_{demonstration_code}_2011-{date.today().year}",
                    filename=f"itr_cia_aberta_{demonstration_code}_{filename}.parquet",
                ).query_parquet(filters={"CD_CVM": cd_cvm})
            )
            
        except FileNotFoundError:
            
            return DataFrame()