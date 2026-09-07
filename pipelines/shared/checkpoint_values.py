"""Valores padronizados para checkpoints.

Define os vocabulários fechados de status, failure_point, reason e
severity, evitando strings soltas e garantindo validação em runtime
(Enum rejeita valores fora do conjunto definido).
"""


from enum import Enum


SCHEMA_VERSION = "v3"


class Stage(str, Enum):
    """Estágios do pipeline.

    Opções: `EXTRACT`, `TRANSFORM`, `TO_INTERIM`, `TO_PROCESSED`, `LOAD`, `QUALITY`, `PUBLISH`, `RETENTION`,
    `COMPARE`, `VALIDATION`, `INTEGRATION`.
    """

    EXTRACT = "extract"
    TRANSFORM = "transform"
    TO_INTERIM = "to_interim"
    TO_PROCESSED = "to_processed"
    LOAD = "load"
    QUALITY = "quality"
    PUBLISH = "publish"
    RETENTION = "retention"
    COMPARE = "compare"
    VALIDATION = "validation"
    INTEGRATION = "integration"


class Step(str, Enum):
    """Etapas de execução dentro de um estágio.

    Opções: `DOWNLOAD`, `PARSE`, `TRANSFORM`, `UPLOAD`, `VALIDATE`, `PUBLISH`, `CLEANUP`, `UNZIP`, `CONCATENATE`,
    `DB_CREATE`, `READER`, `CHECKER`, `JOINER_WORKERS`.
    """

    DOWNLOAD = "download"
    PARSE = "parse"
    TRANSFORM = "transform"
    UPLOAD = "upload"
    VALIDATE = "validate"
    PUBLISH = "publish"
    CLEANUP = "cleanup"
    CLEANUP_DATA = "cleanup_data"
    CLEANUP_HISTORICAL_DATA = "cleanup_historical_data"
    CLEANUP_LOGS = "cleanup_logs"
    CLEANUP_SNAPSHOTS = "cleanup_snapshots"
    UNZIP = "unzip"
    CONCATENATE = "concatenate"
    DB_CREATE = "db_create"
    READER = "reader"
    CHECKER = "checker"
    JOINER_WORKERS = "joiner_workers"
    
    

class Status(str, Enum):
    """Status de execução de um checkpoint.

    Opções: `SUCCESSFUL`, `FAILED`, `NO_FILE_DETECTED`, `DRIVER_ERROR`, `PENDING`,
    `RUNNING`, `PARTIAL_SUCCESS`, `SKIPPED`, `RETRYING`, `TIMEOUT`, `CANCELLED`,
    `WARNING`.
    """

    SUCCESSFUL = "successful"
    FAILED = "failed"
    NO_FILE_DETECTED = "no_file_detected"
    DRIVER_ERROR = "driver_error"
    PENDING = "pending"
    RUNNING = "running"
    PARTIAL_SUCCESS = "partial_success"
    SKIPPED = "skipped"
    RETRYING = "retrying"
    TIMEOUT = "timeout"
    CANCELLED = "cancelled"
    WARNING = "warning"


class FailurePoint(str, Enum):
    """Ponto de falha registrado no checkpoint.

    Opções: `DRIVER_CREATION`, `FILE_DETECTION`, `VALIDATION`, `EXCEPTION`,
    `DOWNLOAD_BUTTON_NOT_FOUND`, `TRANSFORM_EXCEPTION`, `NETWORK_ERROR`,
    `AUTH_ERROR`, `SCHEMA_ERROR`, `PARSE_ERROR`, `IO_ERROR`, `TIMEOUT_ERROR`,
    `DEPENDENCY_ERROR`, `UNEXPECTED_ERROR`, `UNZIP`, `SEARCH_NO_RESULTS`, 
    `NO_CADASTRAL_INFO`, `EMPTY_RESPONSE`, `PROCESSING_ERROR`.
    """

    DRIVER_CREATION = "driver_creation"
    FILE_DETECTION = "file_detection"
    VALIDATION = "validation"
    EXCEPTION = "exception"
    DOWNLOAD_BUTTON_NOT_FOUND = "download_button_not_found"
    TRANSFORM_EXCEPTION = "transform_exception"
    NETWORK_ERROR = "network_error"
    AUTH_ERROR = "auth_error"
    SCHEMA_ERROR = "schema_error"
    PARSE_ERROR = "parse_error"
    IO_ERROR = "io_error"
    TIMEOUT_ERROR = "timeout_error"
    DEPENDENCY_ERROR = "dependency_error"
    UNEXPECTED_ERROR = "unexpected_error"
    UNZIP = "unzip"
    SEARCH_NO_RESULTS = "search_no_results"
    NO_CADASTRAL_INFO = "no_cadastral_info"
    EMPTY_RESPONSE = "empty_response"
    MAX_RETRIES_EXCEEDED = "max_retries_exceeded"
    RUNTIME_EXCEEDED = "runtime_exceeded"  
    PROCESSING_ERROR = "processing_error"
    

class ReasonCode(str, Enum):
    """Código de motivo associado a um status.

    Opções: `ALREADY_PROCESSED`, `NO_NEW_DATA`, `SOURCE_UNAVAILABLE`,
    `RATE_LIMITED`, `CHECKPOINT_CORRUPTED`.
    """

    ALREADY_PROCESSED = "already_processed"
    NO_NEW_DATA = "no_new_data"
    SOURCE_UNAVAILABLE = "source_unavailable"
    RATE_LIMITED = "rate_limited"
    CHECKPOINT_CORRUPTED = "checkpoint_corrupted"
    

class Severity(str, Enum):
    """Severidade do evento registrado.

    Opções: `INFO`, `WARNING`, `ERROR`, `CRITICAL`.
    """

    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"
