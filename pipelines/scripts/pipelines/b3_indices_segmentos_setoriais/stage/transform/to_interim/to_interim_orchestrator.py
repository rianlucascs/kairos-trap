from pipelines.shared.context import PipelineContext
from pipelines.shared.interfaces.pipelines.stage.transform.to_interim.to_interim_orchestrator import ToInterimOrchestratorInterface
from pipelines.shared.interfaces.pipelines.stage.transform.to_interim.to_interim_workers import ToInterimWorkersInterface

from pipelines.scripts.pipelines.b3_indices_segmentos_setoriais.stage.transform.to_interim.to_interim_worker_A import ToInterimWorkerA


class ToInterimOrchestrator(ToInterimOrchestratorInterface):

    def __init__(
        self,
        *,
        pipeline: str,
    ) -> None:
        super().__init__(pipeline=pipeline)

    def _build_workers(self, ctx: PipelineContext) -> list[ToInterimWorkersInterface]:
        return [
            ToInterimWorkerA(pipeline=self.pipeline),
        ]
