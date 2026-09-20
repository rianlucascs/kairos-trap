

from pipelines.shared.context import PipelineContext

from abc import ABC
from pathlib import Path
from datetime import date, timedelta
from dataclasses import dataclass
from typing import Literal
from pandas import read_parquet, DataFrame


@dataclass
class HistoricalDataLocation:
    
    pipeline: str
    snapshot_directory: str
    foldername: str
    filename: str
    snapshot: str | None = None


class HistoricalDataValidator:
    """
    Valida localizações e nomes de arquivos de dados históricos.
    """
    
    
    @staticmethod
    def validate_filename(historical_data_location: HistoricalDataLocation) -> None:
        
        if historical_data_location.snapshot_directory == "snapshot_drift" and not (
            "added" in historical_data_location.filename.lower() or
            "changed" in historical_data_location.filename.lower() or
            "removed" in historical_data_location.filename.lower()
        ):
            raise ValueError("O parâmetro 'filename' deve conter 'added', 'changed' ou 'removed' quando for igual a 'snapshot_drift'.")

        if ".parquet" in historical_data_location.foldername:
            raise ValueError("O parâmetro 'foldername' não deve conter a extensão '.parquet'.")
    
    
    @classmethod
    def validate_read_inputs(cls, historical_data_location: HistoricalDataLocation) -> None:
        cls.validate_filename(historical_data_location)
        
  
class ReaderHistoricalDataInterface(ABC):
    """
    Classe abstrata para leitura do histórico de mudanças dos pipelines.
    """
    
    
    def __init__(
        self,
        pipeline: str,
        snapshot_directory: Literal["snapshot_drift"],
        foldername: str,
        filename: str,
        snapshot: str | None = None
    ) -> None:
        
        self.pipeline = pipeline
        self.snapshot_directory = snapshot_directory
        self.foldername = foldername
        self.filename = filename
        self.snapshot = snapshot

        HistoricalDataValidator.validate_read_inputs(
            HistoricalDataLocation(
                pipeline=self.pipeline,
                snapshot_directory=self.snapshot_directory,
                foldername=self.foldername,
                filename=self.filename,
                snapshot=self.snapshot
            )
        )
        
        self.ctx = PipelineContext()


    def _build_parquet_path(self, snapshot: str | None = None) -> Path:
        """
        Retorna o caminho do arquivo Parquet no snapshot informado ou nos últimos 4 dias.
        
        Args:
            ``snapshot`` (str | None): Diretório do snapshot específico. (YYYY-MM-DD). Se None, busca nos últimos 4 dias.
        """
        
        
        for days in [0, 1, 2, 3]:
             
            file_path = (
                self.ctx.build_snapshot_drift_path(
                    pipeline=self.pipeline,
                    subdir=(date.today() - timedelta(days=days)).strftime("%Y-%m-%d") if snapshot is None else snapshot,
                )
                / self.foldername
                / self.filename
            )
            
            if file_path.exists():
                
                return file_path

            if self.snapshot is not None:
                # Se um snapshot específico foi fornecido e não existe, não continue procurando.
                raise FileNotFoundError(f"Para o snapshot específico '{snapshot}', o arquivo não foi encontrado.")
        
        raise FileNotFoundError(f"Arquivo '{file_path}' não encontrado.")
         
    
    def read(self) -> DataFrame:

        return read_parquet(
            self._build_parquet_path(self.snapshot),
            engine="pyarrow"
            )
        

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
        
        
if __name__ == "__main__":
    
    reader = ReaderHistoricalDataInterface(
        pipeline="cvm_formulario_informacoes_trimestrais",
        snapshot_directory="snapshot_drift",
        foldername="cad_cia_aberta",
        filename="cad_cia_aberta_changed.parquet",
        snapshot=None
    )
    
    print(reader.read()[["CD_CVM"]])
    
    df = reader.query_parquet(filters={"CD_CVM": 21016})
    print(df)