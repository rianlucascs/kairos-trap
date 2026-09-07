

from pipelines.shared.interfaces.readers.reader_snapshot_parquet import ReaderSnapshotParquetInterface

from typing import Literal
from datetime import date


class ReaderSnapshotParquet(ReaderSnapshotParquetInterface):
    
    
    def __init__(
        self,
        cd_cvm: str,
        demonstration_code: Literal[
            'BPA_con', 'BPA_ind', 'BPP_con', 'BPP_ind', 'DFC_MD_con', 'DFC_MD_ind', 'DFC_MI_con', 'DFC_MI_ind', 'DMPL_con', 
            'DMPL_ind', 'DRA_con', 'DRA_ind', 'DRE_con', 'DRE_ind', 'DVA_con', 'DVA_ind'
        ],
        prefix: Literal["itr", "dfp"],
        use_latest_snapshot: bool = True,
    ) -> None:

        super().__init__(
            pipeline="cvm_formulario_por_cia",
            subdir_stage="to_processed",
            subdir_format=f"parquet/cia_aberta_{cd_cvm}/{prefix}",
            file_identifiers=f"{prefix}_cia_aberta_{demonstration_code}_2011-{date.today().year}.parquet",
            use_latest_snapshot=use_latest_snapshot
        )
        
