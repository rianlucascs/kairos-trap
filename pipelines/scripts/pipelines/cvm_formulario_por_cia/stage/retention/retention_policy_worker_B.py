

from pipelines.shared.interfaces.pipelines.stage.retention.retention_policy_worker_B import RetentionPolicyWorkerInterfaceB


class RetentionPolicyWorkerB(RetentionPolicyWorkerInterfaceB):
    
    
    def __init__(
        self,
        *,
        pipeline: str,
    ) -> None:
        
        super().__init__(
            pipeline=pipeline
        )
        
    
    
