"""
master_orchestrator:
    Pipeline base para orquestração de estágios.

Responsabilidades:
    Executar o fluxo principal na ordem: ``extract`` -> ``to_interim`` -> ``to_processed`` -> ``load`` -> ``compare`` -> ``retention``.
    Executar apenas os estágios presentes em ``self._build_stages()``; estágios
    omitidos pela subclasse (ex: ``compare``, ``retention`` quando não implementados)
    simplesmente não são executados.
    Centralizar contexto de execução (env, run_id, paths e logging).
    Importar dinamicamente o módulo orquestrador de cada estágio a partir de
    ``self._build_stages()`` e instanciar a classe correspondente para executar seu ``main``.

Notas:
    Estágios cujo módulo ou classe orquestradora não sejam encontrados são
    registrados como warning e ignorados, sem interromper os demais estágios.
"""


from pipelines.shared.context import PipelineContext

from abc import ABC, abstractmethod
import importlib


class PipelineBase(ABC):
    """
    Classe base para pipelines orientadas a estágios.

    Implementa o fluxo de execução comum (Template Method): a subclasse só
    precisa declarar `pipeline` e implementar `_build_stages()`; o método
    `run()` cuida da importação dinâmica, instanciação e execução de cada
    estágio, com logging e tratamento de estágio ausente/malformado.

    Atributos:

        pipeline (str): nome da pipeline, usado para resolver o caminho dos
            módulos de estágio e propagado às classes orquestradoras.

        stages (dict): mapeamento entre nome do estágio e nome da classe
            orquestradora responsável por executá-lo. Construído por
            `_build_stages()` a cada chamada de `run()`.

        ctx: contexto de execução compartilhado entre os estágios.
    """
    
    
    pipeline: str # subclasse deve declarar (ex: pipeline = "pipeline_a")

    process: str = "master_orchestrator"    
    

    def __init__(
        self,
        env: str = "dev",
        run_id: str | None = None,
    ) -> None:

        self.ctx = PipelineContext(env=env, run_id=run_id)
        

    def __init_subclass__(cls, **kwargs) -> None:
        
        super().__init_subclass__(**kwargs)

        if "pipeline" not in cls.__dict__:
            raise TypeError(
                f"{cls.__name__} deve declarar o atributo de classe 'pipeline' "
                f"(ex: pipeline = \"pipeline_a\")."
            )
            

    @abstractmethod
    def _build_stages(self) -> dict[str, str]:
        """
        Retorna um dicionário mapeando os nomes dos estágios para as classes orquestradoras correspondentes.

        Retorno:
            dict[str, str]: mapeamento entre nome do estágio e nome da classe orquestradora.
        """
        # return {
        #     "extract.extractor_orchestrator": "ExtractorOrchestrator",
        #     "transform.to_interim.to_interim_orchestrator": "ToInterimOrchestrator",
        #     "transform.to_processed.to_processed_orchestrator": "ToProcessedOrchestrator",
        #     "load.loader_orchestrator": "LoaderOrchestrator",
        #     "compare.comparator_orchestrator": "ComparatorOrchestrator",
        #     "retention.retention_policy_orchestrator": "RetentionPolicyOrchestrator"
        # }
        ...
    
    
    def run(self) -> None:
        """
        Método principal da pipeline, responsável por orquestrar os orquestradores.

        Para cada estágio definido em `self._build_stages()`, importa dinamicamente
        o módulo correspondente em `pipelines.scripts.pipelines.{pipeline}.stage.{stage}`
        e instancia a classe orquestradora indicada, executando seu método `main`.

        Estágios cujo módulo não existe ou cuja classe orquestradora não é
        encontrada são registrados como warning e ignorados (`continue`), sem
        interromper a execução dos demais estágios.
        """
        
        self.ctx.configure_logging(pipeline=self.pipeline, process=self.process)
        self.logger = self.ctx.logger

        for stage_path, orchestrator_class_name in self._build_stages().items():
            
            module_name = f"pipelines.scripts.pipelines.{self.pipeline}.stage.{stage_path}"

            try:
                
                module = importlib.import_module(module_name)
                
            except ModuleNotFoundError:
                
                self.logger.exception(f"Módulo do orquestrador não encontrado: {module_name}")
                
                continue

            try:
                
                orchestrator_cls = getattr(module, orchestrator_class_name)
                
            except AttributeError:
                
                self.logger.exception(
                    f"Classe do orquestrador '{orchestrator_class_name}' não encontrada em {module_name}"
                )
                
                continue

            orchestrator = orchestrator_cls(pipeline=self.pipeline)
            orchestrator.main(ctx=self.ctx)
            
        
# def main(env: str = "dev", run_id: str | None = None):
#     """Entrypoint padrão para execução (local e container)."""
    
#     PipelineInterface(env=env, run_id=run_id).run()
    

# if __name__ == "__main__":
    
#     main()