

from pipelines.shared.interfaces.pipelines.stage.pipeline_v2 import PipelineBase


class Pipeline(PipelineBase):

    
    pipeline: str = "cvm_formulario_demonstracoes_financeiras_padronizadas"


    def _build_stages(self) -> dict[str, str]:
        
        return {
            "extract.extractor_orchestrator": "ExtractorOrchestrator",
            "transform.to_interim.to_interim_orchestrator": "ToInterimOrchestrator",
            "transform.to_processed.to_processed_orchestrator": "ToProcessedOrchestrator",
            "compare.comparator_orchestrator": "ComparatorOrchestrator",
            "retention.retention_policy_orchestrator": "RetentionPolicyOrchestrator"
        }
        

def main(env: str = "dev", run_id: str | None = None) -> None:
    
	Pipeline(env=env, run_id=run_id).run()


if __name__ == "__main__":
    
	main()



