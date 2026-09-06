"""
Worker:
    extractor_worker_a

Responsabilidades:
    ...
    
Notas:
    ...
"""


from pipelines.shared.context import PipelineContext
from pipelines.shared.interfaces.pipelines.stage.extract.extractor_workers import ExtractorWorkersInterface
from pipelines.shared.checkpoint_values import Stage, Status, Step, FailurePoint, Severity

import base64
import json
import requests


class ExtractorWorkerA(ExtractorWorkersInterface):


    process: str = "extractor_worker_a"


    def __init__(
        self,
        *,
        pipeline: str,
    ) -> None:
        
        super().__init__(pipeline=pipeline)
        

    def get_b3_index_portfolio(self, url_base: str, index: str = "IDIV", page_size: int = 120) -> dict:
        
        payload = {
            "language": "pt-br",
            "pageNumber": 1,
            "pageSize": page_size,
            "index": index,
            "segment": "1",
        }
        
        encoded = base64.b64encode(json.dumps(payload).encode()).decode()
        
        url = f"{url_base.format(encoded=encoded)}"
        
        resp = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=15)
        resp.raise_for_status()
        
        return resp.json()
    

    def _worker(self, ctx: PipelineContext) -> None:

        url_base: str = getattr(self.settings, "url", "")
        if not url_base:
            self.logger.error("URL não configurada.")
            return
            
        b3_indices_segmentos_setoriais: list[str] = getattr(self.settings, "b3_indices_segmentos_setoriais", [])
        if not b3_indices_segmentos_setoriais:
            self.logger.error("Lista de índices não configurada.")
            return

        raw_json_path = ctx.prepare_raw_path(
            ctx.current_snapshot_path(self.pipeline),
            subdir_format="json"
        )
        
        for index in b3_indices_segmentos_setoriais:

            portfolio = self.get_b3_index_portfolio(
                url_base=url_base, 
                index=index, 
                page_size=200
            )
            
            if not portfolio:
                
                self._write_checkpoint(
                    ctx=ctx,
                    stage=Stage.EXTRACT,
                    step=Step.DOWNLOAD,
                    filename=f"extractor_worker_a.failed_{index}.json",
                    status=Status.FAILED,
                    failure_point=FailurePoint.EMPTY_RESPONSE,
                    severity=Severity.ERROR,
                    source=getattr(self.settings, "url", self.pipeline),
                    extra={"index": index},
                )
                
                self.logger.warning(f"Portfolio vazio para o índice {index}.")
                
                continue

            filepath = raw_json_path / f"{index}.json"
            filepath.write_text(
                json.dumps(portfolio, ensure_ascii=False, indent=2),
                encoding="utf-8"
            )

            self._write_checkpoint(
                ctx=ctx,
                stage=Stage.EXTRACT,
                step=Step.DOWNLOAD,
                filename=f"extractor_worker_a.success_{index}.json",
                status=Status.SUCCESSFUL,
                failure_point=None,
                severity=Severity.INFO,
                source=getattr(self.settings, "url", self.pipeline),
                extra={"index": index},
            )

