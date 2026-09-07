

from pipelines.shared.interfaces.pipelines.stage.transform.to_processed.cvm.to_processed_worker_A import ToProcessedWorkerInterfaceA

from pandas import DataFrame


class ToProcessedWorkerA(ToProcessedWorkerInterfaceA):
    
    
    def __init__(
        self,
        *,
        pipeline: str,
    ) -> None:
        
        super().__init__(
            pipeline=pipeline
        )

    
    def _add_derived_columns(self, df: DataFrame) -> DataFrame | None:
        """
        Adiciona colunas derivadas ao DataFrame.

        Retorna o DataFrame modificado ou None se nenhuma modificação for necessária.
        """
            
        return None


if __name__ == "__main__":
    
    from pipelines.shared.context import PipelineContext
    
    ToProcessedWorkerA(
        pipeline="cvm_formulario_de_referencia"
    ).main(ctx=PipelineContext())