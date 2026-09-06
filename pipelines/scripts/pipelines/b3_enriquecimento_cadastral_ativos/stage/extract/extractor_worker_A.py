"""
Worker:
    extractor_worker_a

Responsabilidades:
    Consultar a API da B3 (por codeCVM) para obter os dados cadastrais/de negociação
    de cada empresa ativa presente no snapshot de `cvm_cias_abertas_informacao_cadastral`,
    persistindo a resposta bruta em JSON.

Notas:
    Este pipeline não é atualizado diariamente, então, caso seja executado no mesmo dia
    de um snapshot já processado, pode não haver novas informações disponíveis.

    Diferente de outros pipelines, que fazem retention ao reexecutar no mesmo dia, aqui os
    arquivos não são apagados nem sobrescritos: antes de consultar a API, verificamos se o
    arquivo JSON da empresa já existe. Se existir, pulamos para a próxima; se não existir,
    refazemos o download dos dados.

    Faz sentido usar o `failure_point` aqui: nenhuma exclusão é feita em caso de reexecução
    no mesmo dia, apenas continuamos de onde paramos. A remoção de dados (retenção) é
    deixada para o estágio de `retention`, não para este worker.
"""


from pipelines.shared.context import PipelineContext
from pipelines.shared.interfaces.pipelines.stage.extract.extractor_workers import ExtractorWorkersInterface
from pipelines.shared.utils.selenium_utils.delays import jittered_delay
from pipelines.shared.checkpoint_values import Stage, Status, Step, FailurePoint, Severity

from pipelines.readers.pipelines.cvm_cias_abertas_informacao_cadastral.reader_parquet_cvm import ReaderSnapshotParquet

from time import sleep, monotonic
import requests
import base64
import json


class B3APIError(Exception):
    """Erro base para falhas na API da B3."""


class CompanyNotFoundError(B3APIError):
    """codigo_cvm não encontrado na base da B3."""


class B3APIRateLimitedError(B3APIError):
    """API retornou 429 - rate limit atingido."""


class B3APIUnavailableError(B3APIError):
    """API retornou 5xx - indisponível no momento."""
    
    
class ExtractorWorkerA(ExtractorWorkersInterface):
    """
    Depende do pipeline `cvm_cias_abertas_informacao_cadastral` para obter informações cadastrais das empresas.
    """
    
    process: str = "extractor_worker_a"


    def __init__(
        self,
        *,
        pipeline: str,
    ) -> None:
        
        super().__init__(pipeline=pipeline)
    

    def get_company_by_cvm_code(self, codigo_cvm: str) -> dict:
        
        url_base = getattr(self.settings, "url", "")
        if not url_base:
            raise ValueError("URL não configurada.")

        payload = {"codeCVM": codigo_cvm, "language": "pt-br"}
        encoded = base64.b64encode(json.dumps(payload).encode("ascii")).decode("ascii")
        url = f"{url_base}{encoded}"

        try:
            
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            
        except requests.exceptions.HTTPError as e:
            
            status = e.response.status_code
            
            if status == 404:
                
                raise CompanyNotFoundError(f"codigo_cvm={codigo_cvm} não encontrado.") from e
            
            if status == 429:
                
                raise B3APIRateLimitedError(f"Rate limit atingido para codigo_cvm={codigo_cvm}.") from e
            
            if status >= 500:
                
                raise B3APIUnavailableError(f"API da B3 indisponível (status={status}).") from e
            
            raise B3APIError(f"Erro HTTP inesperado (status={status}) para codigo_cvm={codigo_cvm}.") from e
        
        except requests.exceptions.RequestException as e:
            
            raise B3APIError(f"Falha de conexão ao consultar codigo_cvm={codigo_cvm}: {e}") from e

        try:
            
            return response.json()
        
        except json.JSONDecodeError as e:
            
            raise B3APIError(f"Resposta inválida (não-JSON) para codigo_cvm={codigo_cvm}.") from e

    
    def _worker(self, ctx: PipelineContext) -> None:
        
        try:
        
            cias_cadastrais = ReaderSnapshotParquet().read()
        
        except FileNotFoundError as e:
            
            self.logger.error(f"Falha ao ler o snapshot cadastral: {e}"
                              f"Rodar o pipeline ``cvm_cias_abertas_informacao_cadastral``")
                
            return
        
            
        if cias_cadastrais.empty:
            
            self._write_checkpoint(
                ctx=ctx,
                stage=Stage.EXTRACT,
                step=Step.DOWNLOAD,
                filename=f"extractor_worker_a.failed.json",
                status=Status.FAILED,
                failure_point=FailurePoint.NO_CADASTRAL_INFO,
                severity=Severity.CRITICAL,
                source=getattr(self.settings, "url", self.pipeline),
                extra={"cias_cadastrais": "vazio"},
            )
                
            self.logger.warning("Nenhuma informação cadastral encontrada.")
            
            return 

        raw_json_path = ctx.prepare_raw_path(
            ctx.current_snapshot_path(self.pipeline),
            subdir_format="json"
        )
            
        cias_cadastrais = cias_cadastrais[["CD_CVM", "SIT"]].copy()

        MAX_RUNTIME_SECONDS = 4 * 60 * 60  # 4 horas
        start_time = monotonic()
            
        for _, row in cias_cadastrais.iterrows():
            
            if row.SIT != "ATIVO":
                continue
            
            filename = f"cd_cvm_{row.CD_CVM}.json"
            filepath = raw_json_path / filename
            
            if filepath.exists():
                continue
            
            # Checagem de teto de tempo total, antes de processar cada empresa
            elapsed = monotonic() - start_time
            if elapsed > MAX_RUNTIME_SECONDS:
                
                self._write_checkpoint(
                    ctx=ctx,
                    stage=Stage.EXTRACT,
                    step=Step.DOWNLOAD,
                    filename="extractor_worker_a.aborted.json",
                    status=Status.FAILED,
                    failure_point=FailurePoint.RUNTIME_EXCEEDED,
                    severity=Severity.CRITICAL,
                    source=getattr(self.settings, "url", self.pipeline),
                    extra={
                        "motivo": "tempo máximo de execução excedido",
                        "elapsed_seconds": round(elapsed, 1),
                        "cd_cvm_restante": row.CD_CVM,
                    },
                )
                
                self.logger.critical(
                    f"Tempo máximo de execução ({MAX_RUNTIME_SECONDS}s) excedido. "
                    f"Abortando antes de processar CVM {row.CD_CVM}."
                )
                
                break
            
            
            # --- Início do loop de tentativas para obter os dados da empresa ---
            
            
            attempt = 0
            max_attempts = 4
            resolved = False  # True se saiu do while já tratado (sucesso ou falha permanente)
            current_delay = jittered_delay(5, 15) # delay inicial entre tentativas
            
            while attempt < max_attempts:
                
                attempt += 1
                
                try:
                    
                    dados = self.get_company_by_cvm_code(row.CD_CVM)
                    
                    if not dados or not dados.get("code"):
                        
                        self._write_checkpoint(
                            ctx=ctx,
                            stage=Stage.EXTRACT,
                            step=Step.DOWNLOAD,
                            filename=f"extractor_worker_a.failed_{row.CD_CVM}.json",
                            status=Status.FAILED,
                            failure_point=FailurePoint.EMPTY_RESPONSE,
                            severity=Severity.ERROR,
                            source=getattr(self.settings, "url", self.pipeline),
                            extra={"cd_cvm": row.CD_CVM},
                        )
                        
                        self.logger.warning(f"CVM {row.CD_CVM} retornou dados vazios, marcando como falha e seguindo.")
                        
                        resolved = True
                        
                        sleep(jittered_delay(current_delay, current_delay + 5))
                        
                        break
                    
                    else:
                        
                        filepath.write_text(
                            json.dumps(dados, ensure_ascii=False, indent=2),
                            encoding="utf-8"
                        )
                        
                        self._write_checkpoint(
                            ctx=ctx,
                            stage=Stage.EXTRACT,
                            step=Step.DOWNLOAD,
                            filename=f"extractor_worker_a.success_{row.CD_CVM}.json",
                            status=Status.SUCCESSFUL,
                            failure_point=None,
                            severity=Severity.INFO,
                            source=getattr(self.settings, "url", self.pipeline),
                            extra={"cd_cvm": row.CD_CVM},
                        )
                        
                        resolved = True
                        
                        sleep(jittered_delay(current_delay, current_delay + 5)) # 700 × 15s = 10.500 segundos = 175 minutos, ou seja, 2h55min
                        
                        break
                    
                except CompanyNotFoundError:
                    
                    self._write_checkpoint(
                        ctx=ctx,
                        stage=Stage.EXTRACT,
                        step=Step.DOWNLOAD,
                        filename=f"extractor_worker_a.failed_{row.CD_CVM}.json",
                        status=Status.FAILED,
                        failure_point=FailurePoint.SEARCH_NO_RESULTS,
                        severity=Severity.ERROR,
                        source=getattr(self.settings, "url", self.pipeline),
                        extra={"cd_cvm": row.CD_CVM},
                    )
                    
                    self.logger.warning(f"CVM {row.CD_CVM} não encontrado, marcando como falha e seguindo.")
                    
                    resolved = True
                    
                    break
                
                except B3APIUnavailableError:
                    
                    self.logger.error(f"B3 API indisponível ao buscar CVM {row.CD_CVM}, tentando novamente.")
                    
                    sleep(jittered_delay(current_delay, current_delay + 5))
                    current_delay = min(60, current_delay * 2)  # aumenta o delay após erro de indisponibilidade da API
                    
                    continue 
                
                except B3APIRateLimitedError:
                    
                    self.logger.error(f"Rate limit atingido em CVM {row.CD_CVM}, tentando novamente.")
                    
                    sleep(jittered_delay(current_delay, current_delay + 5))
                    current_delay = min(60, current_delay * 2)  # aumenta o delay após atingir rate limit
                    
                    continue
            
            if not resolved:
                
                self._write_checkpoint(
                    ctx=ctx,
                    stage=Stage.EXTRACT,
                    step=Step.DOWNLOAD,
                    filename=f"extractor_worker_a.failed_{row.CD_CVM}.json",
                    status=Status.FAILED,
                    failure_point=FailurePoint.MAX_RETRIES_EXCEEDED,
                    severity=Severity.ERROR,
                    source=getattr(self.settings, "url", self.pipeline),
                    extra={
                        "cd_cvm": row.CD_CVM,
                        "motivo": "esgotou tentativas sem resolver"
                    },
                )
                
                self.logger.error(f"Falha ao buscar CVM {row.CD_CVM} após {max_attempts} tentativas.")
                
        
        
ExtractorWorkerA(pipeline="b3_enriquecimento_cadastral_ativos").main(PipelineContext())