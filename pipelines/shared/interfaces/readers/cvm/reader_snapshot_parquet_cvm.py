

from pipelines.shared.interfaces.readers.reader_snapshot_parquet import ReaderSnapshotParquetInterface
 
from typing import Literal
from datetime import date


class ReaderSnapshotParquetCVMInterface(ReaderSnapshotParquetInterface):
    
    
    def __init__(
        self,
        pipeline: Literal["cvm_formulario_demonstracoes_financeiras_padronizadas", "cvm_formulario_informacoes_trimestrais"],
        prefix: Literal["dfp", "itr"],
        demonstration_code: Literal[
            'BPA_con', 'BPA_ind', 'BPP_con', 'BPP_ind', 'DFC_MD_con', 'DFC_MD_ind', 'DFC_MI_con', 'DFC_MI_ind', 'DMPL_con', 
            'DMPL_ind', 'DRA_con', 'DRA_ind', 'DRE_con', 'DRE_ind', 'DVA_con', 'DVA_ind'
        ]
    ) -> None:
        
        super().__init__(
            pipeline=pipeline,
            subdir_stage="to_processed",
            file_identifiers=f"{prefix}_cia_aberta_{demonstration_code}_2011-{date.today().year}.parquet",
            use_latest_snapshot=True
        )