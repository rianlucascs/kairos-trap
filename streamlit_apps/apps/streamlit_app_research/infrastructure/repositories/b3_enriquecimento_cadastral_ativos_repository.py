

from pipelines.readers.pipelines.b3_enriquecimento_cadastral_ativos.reader_parquet import ReaderSnapshotParquet


class B3EnriquecimentoCadastralAtivosRepository(ReaderSnapshotParquet):
    """Repositório para acessar os dados de enriquecimento cadastral de ativos na B3."""