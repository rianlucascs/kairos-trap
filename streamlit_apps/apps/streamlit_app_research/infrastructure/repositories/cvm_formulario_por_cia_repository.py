

from pipelines.readers.pipelines.cvm_formulario_por_cia.reader_parquet import ReaderSnapshotParquet


class CVMFormularioPorCiaRepository(ReaderSnapshotParquet):
    """Repositório para acessar os dados do formulário por companhia na CVM."""
    