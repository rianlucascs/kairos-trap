

from pipelines.shared.interfaces.pipelines.stage.retention.retention_policy_worker_A import RetentionPolicyWorkerInterfaceA


class RetentionPolicyWorkerA(RetentionPolicyWorkerInterfaceA):
    
    
    def __init__(
        self,
        *,
        pipeline: str,
    ) -> None:
        
        super().__init__(
            pipeline=pipeline
        )
        