

from pipelines.readers.pipelines.b3_indices_segmentos_setoriais.reader_parquet import ReaderSnapshotParquet


class B3IndicesSegmentosSetoriaisRepository(ReaderSnapshotParquet):
    """Repositório para acessar os dados de índices e segmentos setoriais da B3."""