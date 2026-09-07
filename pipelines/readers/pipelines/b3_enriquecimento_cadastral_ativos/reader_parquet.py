

from pipelines.shared.interfaces.readers.reader_snapshot_parquet import ReaderSnapshotParquetInterface

from typing import Literal


class ReaderSnapshotParquet(ReaderSnapshotParquetInterface):
    
    
    def __init__(
        self,
        file_identifiers=Literal["codigos.parquet", "empresas.parquet"]
    ) -> None:

        super().__init__(
            pipeline="b3_enriquecimento_cadastral_ativos",
            file_identifiers=file_identifiers,
            use_latest_snapshot=True
        )
        