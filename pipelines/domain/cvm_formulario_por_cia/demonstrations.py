

from __future__ import annotations

from pipelines.readers.pipelines.cvm_formulario_por_cia.reader_parquet import ReaderSnapshotParquet as form_por_cia

from typing import Literal
from pandas import DataFrame, concat
import unicodedata


class AccountNotFoundError(ValueError):
    """Levantado quando nenhuma conta contábil corresponde aos filtros aplicados."""


def normalize_account_text(text: str) -> str:
    """Remove acentos e caixa, para comparar descrições de conta (DS_CONTA) de forma tolerante."""
    return unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode("ascii").casefold()


class DemonstrationValueAggregator:

    # Linhas de ITR com INTERVALO_EXERC até esse limite são "somente trimestre";
    # acima disso, são leituras acumuladas desde o início do exercício (YTD).
    QUARTER_ONLY_MAX_DAYS = 95


    @classmethod
    def _collapse_duplicate_accounts(cls, df: DataFrame) -> DataFrame:
        """Soma linhas de contas diferentes que caem no mesmo período/origem (ex.: busca por descrição casando mais de uma conta)."""

        group_cols = ["DT_REFER", "INTERVALO_EXERC", "ORIGEM_FORMULARIO"]

        return df.groupby(group_cols, as_index=False)["VL_CONTA"].sum()


    @classmethod
    def _keep_ytd_rows(cls, df: DataFrame) -> DataFrame:
        """
        Para DRE/DRA, a CVM reporta duas linhas por trimestre não inicial com o mesmo DT_REFER:
        uma somente do trimestre e outra acumulada no exercício (YTD), distinguidas por
        INTERVALO_EXERC. Mantém apenas a linha YTD, base da decumulação abaixo.
        """

        is_itr = df["ORIGEM_FORMULARIO"] == "ITR"
        has_duplicate = is_itr & df.duplicated(subset=["DT_REFER"], keep=False)
        quarter_only_duplicate = has_duplicate & (df["INTERVALO_EXERC"] <= cls.QUARTER_ONLY_MAX_DAYS)

        return df[~quarter_only_duplicate].copy()


    @classmethod
    def calc_flow_statement(cls, df: DataFrame) -> DataFrame:
        """
        DRE/DRA/DFC são reportadas pela CVM acumuladas desde o início do exercício (YTD) em cada
        ITR, e no total anual no DFP. Decumula para o valor isolado do trimestre por diferença
        dentro de cada ano (trimestre = YTD atual - YTD anterior; o primeiro do ano fica como está).
        """

        df = cls._collapse_duplicate_accounts(df)
        df = cls._keep_ytd_rows(df)

        df["ANO"] = df["DT_REFER"].dt.year
        df = df.sort_values("DT_REFER")

        df["VL_CONTA_TRI"] = df.groupby("ANO")["VL_CONTA"].diff()
        df["VL_CONTA_TRI"] = df["VL_CONTA_TRI"].fillna(df["VL_CONTA"])

        return df.drop(columns=["ANO"]).reset_index(drop=True)


    @classmethod
    def calculate_aggregated_values(cls, df: DataFrame, demonstration_code: str) -> DataFrame:

        if any(kind in demonstration_code for kind in ("DRE", "DRA", "DFC")):
            return cls.calc_flow_statement(df)

        result = df.copy()
        result["VL_CONTA_TRI"] = result["VL_CONTA"]
        return result
    

class Demonstration:
    
    
    def __init__(
        self,
        cd_cvm: str,
        demonstration_code: Literal[
            'BPA_con', 'BPA_ind', 'BPP_con', 'BPP_ind', 'DFC_MD_con', 'DFC_MD_ind', 'DFC_MI_con', 'DFC_MI_ind', 'DMPL_con', 
            'DMPL_ind', 'DRA_con', 'DRA_ind', 'DRE_con', 'DRE_ind', 'DVA_con', 'DVA_ind'
        ],
        prefix: Literal["itr", "dfp", "itr+dfp", "dfp+itr"],
    ) -> None:
        
        self.cd_cvm = cd_cvm
        self.demonstration_code = demonstration_code
        self.prefix = prefix
        
        self.df: DataFrame | None = None
    
    
    def read(self) -> Demonstration:
        
        self.cia_itr_df = form_por_cia(
            cd_cvm=self.cd_cvm,
            demonstration_code=self.demonstration_code,
            prefix="itr"
        ).read()
        
        if self.prefix == "itr":
            
            self.df = self.cia_itr_df
            
            return self
        
        self.cia_dfp_df = form_por_cia(
            cd_cvm=self.cd_cvm,
            demonstration_code=self.demonstration_code,
            prefix="dfp"
        ).read()
        
        if self.prefix == "dfp":
            
            self.df = self.cia_dfp_df
            
            return self
        
        if self.prefix == "itr+dfp" or self.prefix == "dfp+itr":
            
            return self


    def concatenate(self) -> Demonstration:
    
        if self.prefix == "itr+dfp" or self.prefix == "dfp+itr":
            
            self.df = concat([self.cia_itr_df, self.cia_dfp_df], ignore_index=True).sort_values("DT_REFER").reset_index(drop=True)
            
            return self
    
    
    def filter_by_ordem_exerc(self, ordem_exerc: str = "ÚLTIMO") -> Demonstration:
        
        self.df = self.df[self.df["ORDEM_EXERC"] == ordem_exerc].copy()
        
        return self
    

    def filter_by_account(self, cd_conta: str | None = None, ds_conta: str | None = None, fallback: bool = True) -> Demonstration:
        
        if cd_conta is None and ds_conta is None:
            raise ValueError("É necessário fornecer pelo menos um dos parâmetros 'cd_conta' ou 'ds_conta'.")
        
        if cd_conta:
            
            df = self.df[self.df['CD_CONTA'] == cd_conta].copy()
            
        if ds_conta:
            
            df = self.df[self.df['DS_CONTA'] == ds_conta].copy()
        
        if df.empty:
            
            if fallback:
                
                available_accounts = (
                    self.df[["CD_CONTA", "DS_CONTA"]]
                    .drop_duplicates()
                    .sort_values(["CD_CONTA", "DS_CONTA"])
                )
                
                print(available_accounts)
            
            raise AccountNotFoundError(
                f"Nenhuma conta encontrada para cd_conta={cd_conta!r}, ds_conta={ds_conta!r}."
            )
        
        self.df = df
        
        return self


    def filter_by_account_contains(self, ds_conta_contains: str, cd_conta_prefix: str | None = None) -> Demonstration:
        """
        Filtra contas cuja descrição (DS_CONTA) contenha o texto informado, ignorando acentos e
        caixa. Útil quando o CD_CONTA varia entre períodos/empresas, como ocorre com a linha de
        Depreciação/Amortização dentro do fluxo de caixa operacional.
        """

        target = normalize_account_text(ds_conta_contains)
        mask = self.df["DS_CONTA"].map(normalize_account_text).str.contains(target, na=False)

        if cd_conta_prefix:
            mask &= self.df["CD_CONTA"].str.startswith(cd_conta_prefix)

        df = self.df[mask].copy()

        if df.empty:
            raise AccountNotFoundError(
                f"Nenhuma conta contendo {ds_conta_contains!r}"
                + (f" com prefixo {cd_conta_prefix!r}" if cd_conta_prefix else "")
                + " foi encontrada."
            )

        self.df = df

        return self


    def filter_by_intervalo_exerc(self, intervalo_exerc: int = 95) -> Demonstration:
        
        if "INTERVALO_EXERC" not in self.df.columns:
            raise ValueError("Coluna 'INTERVALO_EXERC' não encontrada no DataFrame.")

        self.df = self.df[self.df["INTERVALO_EXERC"] == intervalo_exerc].copy()

        return self
    
    
    def calculate_aggregated_values(self) -> Demonstration:
        
        self.df = DemonstrationValueAggregator.calculate_aggregated_values(
            self.df,
            self.demonstration_code
        )
        
        return self
        

if __name__ == "__main__":
    
    demo = Demonstration(cd_cvm="4170", demonstration_code='BPA_con', prefix="itr+dfp")
    
    df = (demo
          .read()
          .concatenate()
          .filter_by_ordem_exerc(ordem_exerc="ÚLTIMO")
          .filter_by_account(cd_conta="1")
          .calculate_aggregated_values()
          )
    
    print(df.df)