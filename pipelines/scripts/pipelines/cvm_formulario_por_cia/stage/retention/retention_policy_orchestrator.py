

from pipelines.shared.context import PipelineContext
from pipelines.shared.interfaces.pipelines.stage.retention.retention_policy_workers import RetentionPolicyWorkersInterface
from pipelines.shared.interfaces.pipelines.stage.retention.retention_policy_orchestrator import RetentionPolicyOrchestratorInterface

from pipelines.scripts.pipelines.cvm_cias_abertas_informacao_cadastral.stage.retention.retention_policy_worker_A import RetentionPolicyWorkerA
from pipelines.scripts.pipelines.cvm_cias_abertas_informacao_cadastral.stage.retention.retention_policy_worker_B import RetentionPolicyWorkerB


class RetentionPolicyOrchestrator(RetentionPolicyOrchestratorInterface):


    def __init__(
        self,
        *,
        pipeline: str,
    ) -> None:
        
        super().__init__(
            pipeline=pipeline
        )


    def _build_workers(self, ctx: PipelineContext) -> list[RetentionPolicyWorkersInterface]:

        return [
            RetentionPolicyWorkerA(pipeline=self.pipeline),
            RetentionPolicyWorkerB(pipeline=self.pipeline),
        ]
        