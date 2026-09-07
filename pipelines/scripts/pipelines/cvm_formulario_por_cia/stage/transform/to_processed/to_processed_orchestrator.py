

from pipelines.shared.context import PipelineContext
from pipelines.shared.interfaces.pipelines.stage.transform.to_processed.to_processed_orchestrator import ToProcessedOrchestratorInterface
from pipelines.shared.interfaces.pipelines.stage.transform.to_processed.to_processed_workers import ToProcessedWorkersInterface

from pipelines.scripts.pipelines.cvm_formulario_por_cia.stage.transform.to_processed.to_processed_worker_A import ToProcessedWorkerA


class ToProcessedOrchestrator(ToProcessedOrchestratorInterface):


    def __init__(
        self,
        *,
        pipeline: str,
    ) -> None:
        
        super().__init__(
            pipeline=pipeline
        )


    def _build_workers(self, ctx: PipelineContext) -> list[ToProcessedWorkersInterface]:
        
        return [
            ToProcessedWorkerA(pipeline=self.pipeline),
        ]
