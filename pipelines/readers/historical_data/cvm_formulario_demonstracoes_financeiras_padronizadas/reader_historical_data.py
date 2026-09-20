

from pipelines.shared.interfaces.readers.reader_historical_data import ReaderHistoricalDataInterface

from typing import Literal
from datetime import date


class ReaderHistoricalDataCVMDFP(ReaderHistoricalDataInterface):
    
    
    def __init__(
        self,
        demonstration_code: Literal[ 
                                    'BPA_con', 'BPA_ind', 
                                    'BPP_con', 'BPP_ind', 
                                    'DFC_MD_con', 'DFC_MD_ind', 
                                    'DFC_MI_con', 'DFC_MI_ind', 
                                    'DMPL_con', 'DMPL_ind', 
                                    'DRA_con', 'DRA_ind', 
                                    'DRE_con', 'DRE_ind', 
                                    'DVA_con', 'DVA_ind'
                                    ],
        comparation: Literal["added", "changed", "removed"],
        snapshot: str | None = None # YYYY-MM-DD
        
    ) -> None:
            
        super().__init__(
            pipeline="cvm_formulario_demonstracoes_financeiras_padronizadas",
            snapshot_directory="snapshot_drift", 
            foldername=f"dfp_cia_aberta_{demonstration_code}_2011-{date.today().year}",
            filename=f"dfp_cia_aberta_{demonstration_code}_2011-{date.today().year}_{comparation}.parquet",
            snapshot=snapshot
        )
 