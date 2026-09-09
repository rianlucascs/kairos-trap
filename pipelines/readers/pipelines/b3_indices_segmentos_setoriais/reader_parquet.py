

from pipelines.shared.interfaces.readers.reader_snapshot_parquet import ReaderSnapshotParquetInterface

from typing import Literal


class ReaderSnapshotParquet(ReaderSnapshotParquetInterface):
    
    
    def __init__(
        self,
        file_identifiers=Literal["composicao.parquet", "indices.parquet"]
    ) -> None:

        super().__init__(
            pipeline="b3_indices_segmentos_setoriais",
            subdir_stage="to_interim",
            file_identifiers=file_identifiers,
            use_latest_snapshot=True
        )
        