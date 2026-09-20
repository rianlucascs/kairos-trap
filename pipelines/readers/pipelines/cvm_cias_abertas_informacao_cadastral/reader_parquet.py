

from pipelines.shared.interfaces.readers.reader_snapshot_parquet import ReaderSnapshotParquetInterface


class ReaderSnapshotParquet(ReaderSnapshotParquetInterface):
    
    
    def __init__(
        self,
        use_latest_snapshot: bool = True,
    ) -> None:

        super().__init__(
            pipeline="cvm_cias_abertas_informacao_cadastral",
            file_identifiers="cad_cia_aberta.parquet",
            use_latest_snapshot=use_latest_snapshot
        )
        