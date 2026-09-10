

from pipelines.readers.pipelines.cvm_formulario_demonstracoes_financeiras_padronizadas.reader_parquet import ReaderSnapshotParquet


class CVMFormularioDemonstracoesFinanceirasPadronizadasRepository(ReaderSnapshotParquet):
    """Repositório para acessar os dados do formulário de demonstrações financeiras padronizadas na CVM."""
