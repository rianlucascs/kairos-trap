

from pipelines.readers.pipelines.cvm_cias_abertas_informacao_cadastral.reader_parquet import ReaderSnapshotParquet


class CVMCIASAbertasInformacaoCadastralRepository(ReaderSnapshotParquet):
    """Repositório para acessar os dados de informação cadastral das companhias abertas na CVM."""