


from streamlit_apps.apps.streamlit_app_research.infrastructure.repositories.asset_repository import AssetRepository
from streamlit_apps.apps.streamlit_app_research.shared.dto.asset_dto import AssetTradingCodeDTO, AssetDetailsDTO

import streamlit as st


MANUAL_TRADING_CODES: list[AssetTradingCodeDTO] = [
    AssetTradingCodeDTO(
        trading_code="^BVSP",
        cvm_code=None,
        company_name="Ibovespa",
    ),
]


class AssetService:


    def __init__(
        self
    ) -> None:
        
        self.asset_repository = AssetRepository()


    def list_trading_codes(self) -> list[AssetTradingCodeDTO]:
        
        assets: list[AssetTradingCodeDTO] = self.asset_repository.list_trading_codes()

        b3_assets = [
            AssetTradingCodeDTO(
                trading_code=f"{asset.trading_code}.SA",
                cvm_code=asset.cvm_code,
                company_name=asset.company_name,
            )
            for asset in assets
        ]

        return MANUAL_TRADING_CODES + b3_assets
    
    
    def get_details(self, trading_code: str) -> AssetDetailsDTO | None:
        
        codes = self.asset_repository.get_codes()
        companies = self.asset_repository.get_companies()

        asset = codes[codes["code"] == trading_code.replace(".SA", "")]
        if asset.empty:
            return None

        cvm_code = asset.iloc[0]["codeCVM"]
        company = companies[companies["codeCVM"] == cvm_code]
        company_name = company.iloc[0]["companyName"] if not company.empty else ""
        cnpj = company.iloc[0]["cnpj"] if not company.empty else ""
        industry_classification = company.iloc[0]["industryClassification"] if not company.empty else ""
        activity = company.iloc[0]["activity"] if not company.empty else ""
        

        return AssetDetailsDTO(
            trading_code=trading_code,
            cvm_code=str(cvm_code) if cvm_code is not None else None,
            company_name=company_name if company_name else None,
            cnpj=cnpj if cnpj else None,
            industry_classification=industry_classification if industry_classification else None,
            activity=activity if activity else None,
        )