

from pipelines.shared.interfaces.readers.cvm.reader_snapshot_parquet_cvm import ReaderSnapshotParquetCVMInterface

from typing import Literal


class ReaderSnapshotParquetDFP(ReaderSnapshotParquetCVMInterface):
    
    
    def __init__(
        self,
        demonstration_code: Literal[
            'BPA_con', 'BPA_ind', 'BPP_con', 'BPP_ind', 'DFC_MD_con', 'DFC_MD_ind', 'DFC_MI_con', 'DFC_MI_ind', 'DMPL_con', 
            'DMPL_ind', 'DRA_con', 'DRA_ind', 'DRE_con', 'DRE_ind', 'DVA_con', 'DVA_ind'
        ],
    ) -> None:

        super().__init__(
            pipeline="cvm_formulario_demonstracoes_financeiras_padronizadas",
            prefix="dfp",
            demonstration_code=demonstration_code,
        )