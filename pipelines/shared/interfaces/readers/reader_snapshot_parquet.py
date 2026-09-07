

from pipelines.shared.context import PipelineContext

from abc import ABC
from pandas import read_parquet, DataFrame
from typing import Literal
from pathlib import Path


class ReaderSnapshotParquetInterface(ABC):

    def __init__(
        self,
        pipeline: str,
        ctx: PipelineContext | None = None,
        subdir_stage: Literal["to_interim", "to_processed"] = "to_interim",
        subdir_format: str = "parquet",
        file_identifiers: str | None = None,
        use_latest_snapshot: bool | None = None,
    ) -> None:

        self.ctx = ctx or PipelineContext()
        self.pipeline = pipeline
        self.subdir_stage = subdir_stage
        self.subdir_format = subdir_format
        self.use_latest_snapshot = use_latest_snapshot

        if file_identifiers is not None and not file_identifiers.endswith(".parquet"):
            file_identifiers = f"{file_identifiers}.parquet"
        self.file_identifiers = file_identifiers
        
        self._validate()


    def _validate(self) -> None:
        
        self.snapshot_path = self._resolve_snapshot_dir()
        if not self.snapshot_path.exists():
            raise FileNotFoundError(
                f"\nSnapshot directory not found: {self.snapshot_path}\n"
                f"Latest snapshot: {self._find_latest_snapshot()}"
            )
            
        self.file_path = self._build_parquet_path()
        if not self.file_path.exists():
            raise FileNotFoundError(
                f"\nParquet file not found: {self.file_path}\n"
                f"Snapshot directory: {self.snapshot_path}"
            )


    def _find_latest_snapshot(self) -> Path | None:
        
        snapshots_dir = self.ctx.data_dir / self.pipeline
        snapshots = [p for p in snapshots_dir.iterdir() if p.is_dir()]

        if not snapshots:
            return None

        return max(snapshots, key=lambda p: p.name)


    def _resolve_snapshot_dir(self) -> Path | None:
        
        if self.use_latest_snapshot:
            
            return self._find_latest_snapshot()
        
        # current_snapshot_path() returns a path relative to data_dir; resolve it to absolute here.
        return self.ctx.data_dir / self.ctx.current_snapshot_path(self.pipeline)


    def _build_parquet_path(self) -> Path:
        
        snapshot_dir = self._resolve_snapshot_dir()

        if snapshot_dir is None:
            raise FileNotFoundError(
                f"No snapshot found for pipeline: {self.pipeline}"
            )

        return (
            self.ctx.build_transformed_path(
                snapshot_dir,
                subdir_stage=self.subdir_stage,
                subdir_format=self.subdir_format,
            )
            / self.file_identifiers
        )


    def read(self) -> DataFrame:
        
        file_path = self._build_parquet_path()

        return read_parquet(file_path, engine="pyarrow")

    
    def query_parquet(
        self,
        columns: list[str] | None = None, # ["CD_CVM", "DT_REFER", "VL_CONTA"]
        filters: dict[str, object] | None = None, # {"CD_CVM": 16330, "DT_REFER": "2023-12-31"}
    ) -> DataFrame:
        """
        Executa uma query filtrada e/ou projetada sobre o arquivo parquet
        resolvido via `self._build_parquet_path()`, usando DuckDB.

        A query é montada dinamicamente: `columns` define o SELECT e
        `filters` define a cláusula WHERE. Valores de `filters` são passados
        como parâmetros (`?`) ao DuckDB, protegendo contra SQL injection.
        Nomes de colunas em `columns` e `filters` são interpolados
        diretamente na query (identificadores não podem ser parametrizados),
        portanto devem vir apenas de código interno controlado, nunca de
        input externo não validado.

        Args:
            columns: Lista de colunas a selecionar (SELECT). Se None,
                seleciona todas as colunas (`SELECT *`).
                Exemplo: ["CD_CVM", "DT_REFER", "VL_CONTA"]
            filters: Dicionário de condições de igualdade (WHERE), combinadas
                com AND. Se o valor for uma lista/tupla/set, gera uma
                cláusula IN em vez de igualdade simples. Se None, nenhum
                filtro é aplicado (lê o arquivo inteiro).
                Exemplo: {"CD_CVM": 16330, "DT_REFER": "2023-12-31"}
                Exemplo com IN: {"CD_CVM": [16330, 20010, 19348]}

        Returns:
            DataFrame com o resultado da query.
        """
        
        import duckdb
        
        file_path = self._build_parquet_path()

        cols = ", ".join(columns) if columns else "*"
        query = f"SELECT {cols} FROM read_parquet(?)"
        params: list[object] = [str(file_path)]

        if filters:
            
            conditions = []
            
            for col, val in filters.items():
                
                if isinstance(val, (list, tuple, set)):
                    
                    placeholders = ", ".join("?" for _ in val)
                    conditions.append(f"{col} IN ({placeholders})")
                    params.extend(val)
                    
                else:
                    
                    conditions.append(f"{col} = ?")
                    params.append(val)
                    
            query += " WHERE " + " AND ".join(conditions)

        with duckdb.connect() as con:
            
            return con.execute(query, params).df()