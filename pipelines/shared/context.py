

from dataclasses import dataclass
from pathlib import Path
import os
import uuid
import logging
from json import dump
from logging.handlers import RotatingFileHandler
from typing import Literal
from pandas import NA, NaT
from numpy import generic
from datetime import date


@dataclass
class PipelineContext:
    """Contexto do pipeline, com informações sobre ambiente, execução e diretórios.

    Diretórios de dados e estado são resolvidos em `__post_init__` a partir de
    `project_root`, então não devem ser passados no construtor.

    Attributes:
        env: Ambiente de execução (`dev`, `prod`, etc). Lido de `PIPELINE_ENV`
            se não informado.
        run_id: Identificador único da execução. Gerado automaticamente se
            não informado.
        project_root: Raiz do projeto, resolvida a partir da localização deste arquivo.
        pipelines_dir: Diretório raiz dos pipelines.
        data_dir: Diretório de snapshots do pipeline (raw/interim/processed),
            sujeitos a política de retenção — podem ser removidos com o tempo.
        historical_data_dir: Diretório da série histórica de mudanças entre
            snapshots (drift). Não sujeito a retenção: cada entrada é um
            evento único, não reconstruível a partir de outra pasta.
        logs_dir: Diretório de logs de execução.
        state_dir: Diretório de estado do pipeline.
        checkpoints_dir: Diretório de checkpoints (`CheckpointPayload`).
    """


    env: str | None = None
    run_id: str | None = None


    def __post_init__(self) -> None:
        
        if self.env is None:
            self.env = os.getenv("PIPELINE_ENV", "dev")
    
        if self.run_id is None:
            self.run_id = uuid.uuid4().hex[:10]
            
        self.project_root = Path(__file__).resolve().parents[2]
        
        self.pipelines_dir = self.project_root / "pipelines"
        
        self.data_dir = self.pipelines_dir / "data"
        self.historical_data_dir = self.pipelines_dir / "historical_data"
        self.logs_dir = self.pipelines_dir / "logs"
        self.state_dir = self.pipelines_dir / "state"
        self.checkpoints_dir = self.pipelines_dir / "checkpoints"
        
    
    
    def build_raw_path(self, pipeline: str, subdir_format: Literal["csv", "html", "text", "zip", "parquet", "json"] | None = None) -> Path:
        """Constrói o caminho para o diretório ``raw`` de um pipeline.

        Returns:
            pipelines/data/<pipeline>/raw/`<subdir_format>`
            ou 
            pipelines/data/<pipeline>/raw quando subdir_format é None.
        """
        
        base = self.data_dir / pipeline / "raw"

        if subdir_format is None:
            return base
        
        else:
            return base / subdir_format
        
    
    def build_transformed_path(
        self, 
        pipeline: str, 
        subdir_stage: Literal["to_interim", "to_processed"], 
        subdir_format: str | None = None,  # "csv", "html", "text", "zip", "parquet"
    ) -> Path:
        """Constrói o caminho para o diretório ``transform`` de um pipeline.
        
        Returns:
            pipelines/data/<pipeline>/transform/<subdir_stage>/`<subdir_format>`
            ou
            pipelines/data/<pipeline>/transform/<subdir_stage> quando subdir_format é None.
        """
        
        base = self.data_dir / pipeline / "transform"
        
        if subdir_stage not in ["to_interim", "to_processed"]:
            raise ValueError(f"subdir_stage must be 'to_interim' or 'to_processed', got '{subdir_stage}'")
        
        base = base / subdir_stage

        if subdir_format is None:
            return base
        
        else:
            return base / subdir_format
    
    
    def build_load_path(self, pipeline: str) -> Path:
        """Constrói o caminho para o diretório ``load`` de um pipeline.
        
        Returns:
            pipelines/data/<pipeline>/load
        """
        
        return self.data_dir / pipeline / "load"
    
    
    def build_logs_path(self, pipeline: str, run_id: str | None = None) -> Path:
        """Constrói o caminho para o diretório ``logs`` de um pipeline.
        
        - Se ``run_id`` for None, será usado o run_id do contexto atual.
        - Se ``run_id`` for fornecido, será usado o run_id fornecido.
        
        Returns:
            pipelines/logs/<pipeline>
        """
        
        if run_id is None:
            return self.logs_dir / pipeline / self.run_id
        
        return self.logs_dir / pipeline / run_id
    
    
    def build_snapshot_drift_path(self, pipeline: str, subdir: str | None = None) -> Path:
        """Constrói o caminho para o diretório ``compare_history`` de um pipeline.

        Returns:
            pipelines/data/<pipeline>/compare_history
        """

        if subdir is None:
            return self.historical_data_dir / pipeline / "snapshot_drift"
        else:
            return self.historical_data_dir / pipeline / "snapshot_drift" / subdir
    
    
    def  prepare_raw_path(self, pipeline: str, subdir_format: Literal["csv", "html", "text", "zip", "json"] | None = None) -> Path:
        """Prepara o diretório ``raw`` de um pipeline.

        Returns:
            O caminho para o diretório ``raw`` preparado.
        """
        
        path = self.build_raw_path(pipeline, subdir_format)
        path.mkdir(parents=True, exist_ok=True)
        
        return path


    def prepare_transformed_path(self, pipeline: str, subdir_stage: Literal["to_interim", "to_processed"], 
                                 subdir_format: Literal["csv", "html", "text", "parquet"] | None = None) -> Path:
        """Prepara o diretório ``transform`` de um pipeline.

        Returns:
            O caminho para o diretório ``transform`` preparado.
        """
        
        path = self.build_transformed_path(pipeline, subdir_stage, subdir_format)
        path.mkdir(parents=True, exist_ok=True)
        
        return path
    
    
    def prepare_load_path(self, pipeline: str) -> Path:
        """Prepara o diretório ``load`` de um pipeline.

        Returns:
            O caminho para o diretório ``load`` preparado.
        """
        
        path = self.build_load_path(pipeline)
        path.mkdir(parents=True, exist_ok=True)
        
        return path
    
    
    def prepare_checkpoint_path(self, pipeline: str, stage: str, step: str) -> Path:
        """Prepara o diretório ``checkpoints`` de um pipeline.

        Returns:
            O caminho para o diretório ``checkpoints`` preparado.
        """
        
        path = self.checkpoints_dir / pipeline / stage / step
        path.mkdir(parents=True, exist_ok=True)
        
        return path
    
    
    def prepare_checkpoint_file(self, pipeline: str, stage: str, step: str, filename: str) -> Path:
        """Prepara o arquivo de checkpoint de um pipeline.

        Returns:
            O caminho para o arquivo de checkpoint preparado.
        """
        
        if not filename.endswith(".json"):
            filename += ".json"
        
        return self.prepare_checkpoint_path(pipeline, stage, step) / f"{filename}"
    
    
    def prepare_logs_path(self, pipeline: str) -> Path:
        """Prepara o diretório ``logs`` de um pipeline.

        Returns:
            O caminho para o diretório ``logs`` preparado.
        """
        
        path = self.build_logs_path(pipeline)
        path.mkdir(parents=True, exist_ok=True)
        
        return path
    
    
    def prepare_snapshot_drift_path(self, pipeline: str, subdir: str | None = None) -> Path:
        """Prepara o diretório ``snapshot_drift`` de um pipeline.

        Returns:
            O caminho para o diretório ``snapshot_drift`` preparado.
        """
        
        path = self.build_snapshot_drift_path(pipeline, subdir)
        path.mkdir(parents=True, exist_ok=True)
        
        return path


    @staticmethod
    def _json_default(value):
        """Serializa tipos comuns do ecossistema pandas/numpy para JSON."""

        if isinstance(value, Path):
            return str(value)

        if isinstance(value, generic):
            return value.item()

        if value is NA or value is NaT:
            return None

        if hasattr(value, "isoformat"):
            try:
                return value.isoformat()
            except Exception:
                pass

        return str(value)

    
    def write_checkpoint(self, pipeline: str, stage: str, step: str, filename: str, data: dict) -> None:
        """Escreve um arquivo de checkpoint de um pipeline."""
        
        checkpoint_file = self.prepare_checkpoint_file(pipeline, stage, step, filename)
        tmp_file = checkpoint_file.with_suffix(".tmp")
        
        with open(tmp_file, "w") as f:
            dump(data, f, indent=4, default=self._json_default)
            
        tmp_file.replace(checkpoint_file)
            
            
    def current_snapshot_path(self, pipeline: str, current_date: str | None = None) -> Path:
        """Retorna o caminho do snapshot atual.
        
        Pode-se passar a data do snapshot atual como string no formato YYYY-MM-DD. Se não for passado, será usado o dia atual.
        
        Returns:
            Path(pipeline) / date.today().strftime("%Y-%m-%d"): Caminho do snapshot atual.
        """
        
        if current_date is None:
            current_date = date.today().strftime("%Y-%m-%d")
            
        return Path(pipeline) / current_date


    def configure_logging(self, pipeline: str, process: str, level: int = logging.INFO,
                          max_bytes: int = 5 * 1024 * 1024, backup_count: int = 5):
        """Configura o logger para o pipeline/processo atual."""
        
        logger_name = f"{pipeline}.{process}"
        logger = logging.getLogger(logger_name)

        # avoid re-configuring the same logger
        if getattr(logger, "_configured", False):
            self.logger = logger
            return logger

        logger.setLevel(level)

        log_dir = self.prepare_logs_path(pipeline)
        file_path = log_dir / f"{pipeline}.{process}.{self.run_id}.log"

        fh = RotatingFileHandler(filename=str(file_path), maxBytes=max_bytes,
                                 backupCount=backup_count, encoding="utf-8")
        
        fmt = logging.Formatter("%(asctime)s | %(name)s | %(levelname)s | %(message)s")
        
        fh.setFormatter(fmt)
        logger.addHandler(fh)

        sh = logging.StreamHandler()
        sh.setFormatter(fmt)
        logger.addHandler(sh)

        logger.propagate = False
        logger._configured = True

        self.logger = logger
        
        return logger
    