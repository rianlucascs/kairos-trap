

from pipelines.shared.interfaces.pipelines.stage.pipeline import PipelineBase


class Pipeline(PipelineBase):

    
    pipeline: str = "cvm_formulario_por_cia"


    def _build_stages(self) -> dict[str, str]:
        
        return {
            "transform.to_processed.to_processed_orchestrator": "ToProcessedOrchestrator",
            "retention.retention_policy_orchestrator": "RetentionPolicyOrchestrator"
        }
        

def main(env: str = "dev", run_id: str | None = None) -> None:
    
	Pipeline(env=env, run_id=run_id).run()


if __name__ == "__main__":
    
	main()



