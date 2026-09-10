

from pipelines.readers.pipelines.cvm_formulario_informacoes_trimestrais.reader_parquet import ReaderSnapshotParquet


class CVMFormularioInformacoesTrimestraisRepository(ReaderSnapshotParquet):
    """Repositório para acessar os dados do formulário de informações trimestrais na CVM."""