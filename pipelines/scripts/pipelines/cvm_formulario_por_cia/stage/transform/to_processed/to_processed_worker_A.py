

from pipelines.shared.context import PipelineContext
from pipelines.shared.interfaces.pipelines.stage.transform.to_processed.to_processed_workers import ToProcessedWorkersInterface

from pipelines.readers.pipelines.cvm_cias_abertas_informacao_cadastral.reader_parquet import ReaderSnapshotParquet as cias_cad
from pipelines.readers.pipelines.cvm_formulario_informacoes_trimestrais.reader_parquet import ReaderSnapshotParquet as itr
from pipelines.readers.pipelines.cvm_formulario_demonstracoes_financeiras_padronizadas.reader_parquet import ReaderSnapshotParquet as dfp
from pipelines.shared.utils.io_utils import clear_directory
from pipelines.shared.checkpoint_values import Stage, Status, Step, FailurePoint, Severity

from pandas import DataFrame
from datetime import date
import gc


class ToProcessedWorkerError(Exception):
    """Erro base para falhas no worker de transformação to_processed."""


class MissingPipelineSettingsError(ToProcessedWorkerError):
    """Levantado quando uma configuração obrigatória não está presente em pipeline_settings."""


class DemonstrationProcessingError(ToProcessedWorkerError):
    """Erro ao processar demonstração financeira de uma companhia específica."""

    def __init__(self, demonstration_code: str, cd_cvm: str, original_error: Exception) -> None:
        self.demonstration_code = demonstration_code
        self.cd_cvm = cd_cvm
        self.original_error = original_error
        super().__init__(
            f"Falha ao processar a demonstração '{demonstration_code}' "
            f"para a cia aberta '{cd_cvm}': {original_error}"
        )
        
    
class ToProcessedWorkerA(ToProcessedWorkersInterface):
    """
    Worker A para transformação to_processed no pipeline cvm_formulario_por_cia.

    Responsabilidades:
        - Processar dados de demonstrações financeiras padronizadas (DFP) e informações trimestrais (ITR) de companhias abertas.
        - Filtrar apenas companhias ativas.
        - Salvar os dados processados em formato Parquet.
    """
    
    
    process: str = "to_processed_worker_a"
    
    
    def __init__(
        self,
        *,
        pipeline: str,
    ) -> None:
        
        super().__init__(
            pipeline=pipeline
        )

    
    def _worker(self, ctx: PipelineContext) -> None:
        
        demonstration_codes = getattr(self.settings, "demonstration_codes", [])
        if not demonstration_codes:
            raise MissingPipelineSettingsError(
                f"demonstration_codes não configurado em pipeline_settings para o pipeline '{self.pipeline}'."
            )
        
        processed_parquet_path = ctx.prepare_transformed_path(
            ctx.current_snapshot_path(self.pipeline),
            subdir_stage="to_processed",
            subdir_format="parquet"
        )
        
        clear_directory(processed_parquet_path, logger=self.logger, remove_root=True)
        
        cias_abertas_cvm: DataFrame = cias_cad().read()[["CD_CVM", "SIT"]].drop_duplicates(subset=["CD_CVM"])
        
        for raw in cias_abertas_cvm.itertuples():
            
            if raw.SIT != "ATIVO":
                continue

            cd_cvm = str(raw.CD_CVM).zfill(6)

            for demonstration_code in demonstration_codes:
                
                try:
                    
                    cias_itr: DataFrame = itr(demonstration_code=demonstration_code).query_parquet(
                        filters={"CD_CVM": cd_cvm}
                    )
                    
                    cias_dfp: DataFrame = dfp(demonstration_code=demonstration_code).query_parquet(
                        filters={"CD_CVM": cd_cvm}
                    )
                    
                    cias_dfp_path = (
                        processed_parquet_path 
                        / f"cia_aberta_{raw.CD_CVM}" 
                        / "dfp" 
                    )
                    
                    cias_itr_path = (
                        processed_parquet_path 
                        / f"cia_aberta_{raw.CD_CVM}" 
                        / "itr" 
                    )
                    
                    cias_dfp_path.mkdir(parents=True, exist_ok=True)
                    cias_itr_path.mkdir(parents=True, exist_ok=True)
                    
                    cias_dfp.to_parquet(
                        cias_dfp_path 
                        / f"dfp_cia_aberta_{demonstration_code}_2011-{date.today().year}.parquet"
                        , index=False
                    )
                    
                    cias_itr.to_parquet(
                        cias_itr_path 
                        / f"itr_cia_aberta_{demonstration_code}_2011-{date.today().year}.parquet"
                        , index=False
                    )
                    
                    del cias_itr, cias_dfp, cias_dfp_path, cias_itr_path
                    gc.collect()
                    
                    self._write_checkpoint(
                        ctx=ctx,
                        stage=Stage.EXTRACT,
                        step=Step.DOWNLOAD,
                        filename=f"extractor_worker_a.success_{raw.CD_CVM}.json",
                        status=Status.SUCCESSFUL,
                        failure_point=None,
                        severity=Severity.INFO,
                        source=getattr(self.settings, "url", self.pipeline),
                        extra={"cd_cvm": raw.CD_CVM},
                    )
                
                except Exception as e:
                    
                    err = DemonstrationProcessingError(demonstration_code, raw.CD_CVM, e)
                    
                    self.logger.error(err)
                    
                    self._write_checkpoint(
                        ctx=ctx,
                        stage=Stage.EXTRACT,
                        step=Step.DOWNLOAD,
                        filename=f"extractor_worker_a.failure_{raw.CD_CVM}.json",
                        status=Status.FAILED,
                        failure_point=FailurePoint.PROCESSING_ERROR,
                        severity=Severity.ERROR,
                        source=getattr(self.settings, "url", self.pipeline),
                        extra={
                            "cd_cvm": raw.CD_CVM,
                            "error": str(err),
                        },
                    )
