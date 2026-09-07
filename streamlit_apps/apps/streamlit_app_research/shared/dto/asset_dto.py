

from dataclasses import dataclass


@dataclass(frozen=True)
class AssetTradingCodeDTO:
    trading_code: str
    cvm_code: str | None
    company_name: list[str]
    

@dataclass(frozen=True)
class AssetDetailsDTO:
    
    trading_code: str | None
    cvm_code: str | None
    company_name: str | None
    cnpj: str | None
    industry_classification: str | None
    activity: str | None