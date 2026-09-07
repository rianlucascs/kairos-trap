"""
Worker:
    comparator_workers_a
    
Responsabilidades:
    Comparar arquivos Parquet entre snapshots consecutivos, identificando linhas adicionadas, removidas e alteradas.
    
    - Linhas adicionadas: presentes no snapshot atual, mas ausentes no snapshot anterior.
    - Linhas removidas: presentes no snapshot anterior, mas ausentes no snapshot atual.
    - Linhas alteradas: presentes em ambos os snapshots, mas com valores diferentes em colunas de valor (excluindo colunas-chave).
    
Notas:
    - O worker utiliza DuckDB para realizar operações de comparação entre os arquivos Parquet.
    
"""


from pipelines.shared.context import PipelineContext
from pipelines.shared.interfaces.pipelines.stage.compare.comparator_workers import ComparatorWorkersInterface
from pipelines.shared.utils.io_utils import clear_directory
from pipelines.shared.checkpoint_values import Stage, Step, Status


from datetime import date, timedelta
from pathlib import Path
import duckdb
from abc import ABC, abstractmethod


class DuckDBManager:
    """Classe auxiliar para gerenciar operações de comparação de arquivos Parquet usando DuckDB."""
    
    
    def __init__(
        self, 
        logging,
    ) -> None:
        
        self.logger = logging


    @staticmethod
    def _quote_identifier(identifier: str) -> str:
        escaped = identifier.replace('"', '""')
        return '"' + escaped + '"'
    

    @staticmethod
    def _quote_literal(value: Path) -> str:
        return str(value).replace("'", "''")

    
    def _copy_query_if_not_empty(
        self, con: duckdb.DuckDBPyConnection, query: str, output_path: Path
    ) -> int:
        """
        Executa a query e copia o resultado para um arquivo Parquet se houver resultados.
        Retorna o número de linhas copiadas.
        """
        
        
        output_literal = self._quote_literal(output_path)
        copy_sql = f"COPY ({query}) TO '{output_literal}' (FORMAT PARQUET)"
        
        try:
            
            con.execute(copy_sql)
            
        except Exception:
            
            self.logger.error(f"Falha ao executar query DuckDB:\n{copy_sql}")
            
            raise
        
        count = con.execute(f"SELECT COUNT(*) FROM read_parquet('{output_literal}')").fetchone()[0]
        
        if count == 0:
            
            output_path.unlink()
            
        return count
    
    
    def _find_snapshot_drift_duckdb(
        self,
        previous_path: Path,
        current_path: Path,
        output_dir: Path,
        output_stem: str,
        key_cols: list[str],
    ) -> tuple[int, int, int]:
        """
        Compara dois arquivos Parquet (snapshot anterior e atual) usando DuckDB para identificar linhas adicionadas, removidas e alteradas.
        Retorna uma tupla com o número de linhas adicionadas, removidas e alteradas.
        """
        
        
        previous_file = self._quote_literal(previous_path)
        current_file = self._quote_literal(current_path)

        with duckdb.connect() as con:
            
            con.execute("SET memory_limit = '3GB'")

            current_relation = f"read_parquet('{current_file}')"
            previous_relation = f"read_parquet('{previous_file}')"

            columns = [row[0] for row in con.execute(f"DESCRIBE SELECT * FROM {current_relation}").fetchall()]

            missing_key_cols = [column for column in key_cols if column not in columns]
            
            if missing_key_cols:
                raise ValueError(f"key_cols ausentes no parquet atual: {missing_key_cols}")
            
            if not key_cols:
                raise ValueError("key_cols não pode ser vazio")

            key_join = " AND ".join(
                f"c.{self._quote_identifier(column)} IS NOT DISTINCT FROM p.{self._quote_identifier(column)}"
                for column in key_cols
            )

            added_query = (
                f"SELECT c.* FROM {current_relation} c "
                f"WHERE NOT EXISTS ("
                f"  SELECT 1 FROM {previous_relation} p WHERE {key_join}"
                f")"
            )
            
            removed_query = (
                f"SELECT p.* FROM {previous_relation} p "
                f"WHERE NOT EXISTS ("
                f"  SELECT 1 FROM {current_relation} c WHERE {key_join}"
                f")"
            )

            added_count = self._copy_query_if_not_empty(
                con, added_query, output_dir / f"{output_stem}_added.parquet"
            )
            
            removed_count = self._copy_query_if_not_empty(
                con, removed_query, output_dir / f"{output_stem}_removed.parquet"
            )

            value_cols = [column for column in columns if column not in key_cols]
            
            if not value_cols:
                # sem colunas de valor, não há como haver linhas "changed"
                changed_count = 0
                
            else:
                
                changed_condition = " OR ".join(
                    f"c.{self._quote_identifier(column)} IS DISTINCT FROM p.{self._quote_identifier(column)}"
                    for column in value_cols
                )
                
                changed_query = (
                    f"SELECT c.* FROM {current_relation} AS c "
                    f"JOIN {previous_relation} AS p ON {key_join} "
                    f"WHERE {changed_condition}"
                )
                
                changed_count = self._copy_query_if_not_empty(
                    con, changed_query, output_dir / f"{output_stem}_changed.parquet"
                )

        return added_count, removed_count, changed_count


class ComparatorWorkerInterfaceA(ComparatorWorkersInterface, ABC):
    """
    Esta é a interface para os comparadores de DataFrames.

    Métodos que a subclasse deve implementar:
        ``_build_previous_data_path``: define a lógica para obter o caminho do snapshot anterior.
        ``_build_current_data_path``: define a lógica para obter o caminho do snapshot atual.
    """
    
    
    process: str = "comparator_worker_a"


    def __init__(
        self,
        *,
        pipeline: str,
    ) -> None:
        
        super().__init__(
            pipeline=pipeline
        )
        
        self.previous_snapshot = (date.today() - timedelta(days=1)).strftime("%Y-%m-%d")
        self.current_snapshot = date.today().strftime("%Y-%m-%d")
        
        
    @abstractmethod
    def _build_previous_data_path(self, ctx: PipelineContext) -> Path:
        """
        ``Path`` para o snapshot anterior, que será comparado com o snapshot atual.
        """
        ...
    
    
    @abstractmethod
    def _build_current_data_path(self, ctx: PipelineContext) -> Path:
        """
        ``Path`` para o snapshot atual, que será comparado com o snapshot anterior.
        """
        ...
    
    
    @abstractmethod
    def _key_cols(self) -> list[str]:
        """
        Retorna as colunas que identificam unicamente uma entidade entre snapshots.

        Essas colunas são usadas para relacionar os registros dos snapshots anterior
        e atual, classificar registros como adicionados ou removidos e localizar
        registros existentes que podem ter sofrido alterações. Elas não são
        comparadas como valores alterados; todas as demais colunas do dataset são
        avaliadas nessa comparação.
        """
        ...
        
        
    def _compare_directory_files(self, ctx: PipelineContext) -> tuple[set[str], set[str], set[str]]:
        
        previous_files = {path.name for path in self._build_previous_data_path(ctx).glob("*.parquet")}

        current_files = {path.name for path in self._build_current_data_path(ctx).glob("*.parquet")}

        common_files = previous_files & current_files
        only_in_previous = previous_files - current_files
        only_in_current = current_files - previous_files
        
        return common_files, only_in_previous, only_in_current
        
    
    def _worker(self, ctx: PipelineContext) -> None:
        
        prepare_snapshot_drift_path = ctx.prepare_snapshot_drift_path(self.pipeline, subdir=self.current_snapshot)
        
        clear_directory(prepare_snapshot_drift_path, logger=self.logger, remove_root=False)
        
        common_files, only_in_previous, only_in_current = self._compare_directory_files(ctx)
        
        if only_in_previous:
            self.logger.warning(f"Arquivos presentes `apenas` no snapshot anterior ({self.previous_snapshot}): {only_in_previous}")
        
        if only_in_current:
            self.logger.warning(f"Arquivos presentes `apenas` no snapshot atual ({self.current_snapshot}): {only_in_current}")
        
        if not common_files:
            self.logger.error(f"Não há arquivos em comum entre os snapshots {self.previous_snapshot} e {self.current_snapshot}.")
            return
        
        for filename in common_files:
            
            _filename = filename.removesuffix(".parquet")
            
            len_added_rows, len_removed_rows, len_changed_rows = None, None, None
            
            try:

                filename_folder_path = prepare_snapshot_drift_path / _filename
                filename_folder_path.mkdir(parents=True, exist_ok=True)
                key_cols: list = self._key_cols()

                len_added_rows, len_removed_rows, len_changed_rows = DuckDBManager(self.logger)._find_snapshot_drift_duckdb(
                    previous_path=self._build_previous_data_path(ctx) / filename,
                    current_path=self._build_current_data_path(ctx) / filename,
                    output_dir=filename_folder_path,
                    output_stem=_filename,
                    key_cols=key_cols,
                )
                
                self._write_checkpoint(
                    ctx=ctx,
                    stage=Stage.COMPARE,
                    step=Step.TRANSFORM,
                    filename=f"comparator_worker_a.success.{_filename}.json",
                    status=Status.SUCCESSFUL,
                    source=getattr(self.settings, "url", self.pipeline),
                    extra={
                        "previous_snapshot": self.previous_snapshot,
                        "current_snapshot": self.current_snapshot,
                        "filename": filename,
                        "common_files": list(common_files),
                        "only_in_previous": list(only_in_previous),
                        "only_in_current": list(only_in_current),
                        "len_added_rows": len_added_rows,
                        "len_removed_rows": len_removed_rows,
                        "len_changed_rows": len_changed_rows,
                    }
                )
        
            except Exception as e:
                
                self._write_checkpoint(
                    ctx=ctx,
                    stage=Stage.COMPARE,
                    step=Step.TRANSFORM,
                    filename=f"comparator_worker_a.failure.{_filename}.json",
                    status=Status.FAILED,
                    source=getattr(self.settings, "url", self.pipeline),
                    extra={
                        "previous_snapshot": self.previous_snapshot,
                        "current_snapshot": self.current_snapshot,
                        "common_files": list(common_files),
                        "only_in_previous": list(only_in_previous),
                        "only_in_current": list(only_in_current),
                        "error_message": str(e),
                    }
                )
                
                self.logger.error(f"Erro ao comparar arquivos do snapshot: {e}")
                