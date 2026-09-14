

from streamlit_apps.apps.streamlit_app_research.infrastructure.repositories.cvm_formulario_por_cia_repository import CVMFormularioPorCiaRepository
from pipelines.domain.cvm_formulario_por_cia.demonstrations import AccountNotFoundError

from pandas import DataFrame
from typing import Literal
import streamlit as st


class AssetDemonstrationService:


    @st.cache_data(ttl=60*5, show_spinner="Loading demonstration data...")
    def get_demonstration(
        _self,
        cd_cvm: str,
        demonstration_code: Literal[
            'BPA_con', 'BPA_ind', 'BPP_con', 'BPP_ind', 'DFC_MD_con', 'DFC_MD_ind', 'DFC_MI_con',
            'DFC_MI_ind', 'DMPL_con', 'DMPL_ind', 'DRA_con', 'DRA_ind', 'DRE_con', 'DRE_ind', 'DVA_con', 'DVA_ind'
            ],
        prefix: Literal['itr', 'dfp', 'itr+dfp', 'dfp+itr'],
        ordem_exerc: str = "ÚLTIMO",
        cd_conta: str = "1",
    ) -> DataFrame:

        asset_demonstration_repository = CVMFormularioPorCiaRepository(
            cd_cvm=cd_cvm,
            demonstration_code=demonstration_code,
            prefix=prefix,
        )

        return (
            asset_demonstration_repository
            .get_formulario_por_cia(ordem_exerc=ordem_exerc, cd_conta=cd_conta)
            .df
            .reset_index(drop=True)
        )


    @st.cache_data(ttl=60*5, show_spinner="Loading demonstration data...")
    def get_demonstration_by_description(
        _self,
        cd_cvm: str,
        demonstration_code: Literal[
            'BPA_con', 'BPA_ind', 'BPP_con', 'BPP_ind', 'DFC_MD_con', 'DFC_MD_ind', 'DFC_MI_con',
            'DFC_MI_ind', 'DMPL_con', 'DMPL_ind', 'DRA_con', 'DRA_ind', 'DRE_con', 'DRE_ind', 'DVA_con', 'DVA_ind'
            ],
        prefix: Literal['itr', 'dfp', 'itr+dfp', 'dfp+itr'],
        ds_conta_contains: str,
        cd_conta_prefix: str | None = None,
        ordem_exerc: str = "ÚLTIMO",
    ) -> DataFrame:

        asset_demonstration_repository = CVMFormularioPorCiaRepository(
            cd_cvm=cd_cvm,
            demonstration_code=demonstration_code,
            prefix=prefix,
        )

        return (
            asset_demonstration_repository
            .get_formulario_por_cia_by_description(
                ds_conta_contains=ds_conta_contains,
                cd_conta_prefix=cd_conta_prefix,
                ordem_exerc=ordem_exerc,
            )
            .df
            .reset_index(drop=True)
        )


    @st.cache_data(ttl=60*5, show_spinner="Loading demonstration data...")
    def get_ativo(_self, cd_cvm: str) -> DataFrame:
        return _self.get_demonstration(
            cd_cvm=cd_cvm,
            demonstration_code="BPA_con",
            prefix="itr+dfp", ordem_exerc="ÚLTIMO",
            cd_conta="1",
        )
        
        
    @st.cache_data(ttl=60*5, show_spinner="Loading demonstration data...")
    def get_divida_bruta_lp(_self, cd_cvm: str) -> DataFrame:
        return _self.get_demonstration(
            cd_cvm=cd_cvm,
            demonstration_code="BPP_con",
            prefix="itr+dfp",
            ordem_exerc="ÚLTIMO",
            cd_conta="2.02.01",
        )


    @st.cache_data(ttl=60*5, show_spinner="Loading demonstration data...")
    def get_divida_bruta_cp(_self, cd_cvm: str) -> DataFrame:
        return _self.get_demonstration(
            cd_cvm=cd_cvm,
            demonstration_code="BPP_con",
            prefix="itr+dfp",
            ordem_exerc="ÚLTIMO",
            cd_conta="2.01.04",
        )


    @st.cache_data(ttl=60*5, show_spinner="Loading demonstration data...")
    def get_caixa_e_equivalentes(_self, cd_cvm: str) -> DataFrame:
        return _self.get_demonstration(
            cd_cvm=cd_cvm,
            demonstration_code="BPA_con",
            prefix="itr+dfp",
            ordem_exerc="ÚLTIMO",
            cd_conta="1.01.01",
        )


    @st.cache_data(ttl=60*5, show_spinner="Loading demonstration data...")
    def get_patrimonio_liquido_total(_self, cd_cvm: str) -> DataFrame:
        return _self.get_demonstration(
            cd_cvm=cd_cvm,
            demonstration_code="BPP_con",
            prefix="itr+dfp",
            ordem_exerc="ÚLTIMO",
            cd_conta="2.03",
        )
        
        
    @st.cache_data(ttl=60*5, show_spinner="Loading demonstration data...")
    def get_participacao_nao_controladores(_self, cd_cvm: str) -> DataFrame:
        return _self.get_demonstration(
            cd_cvm=cd_cvm,
            demonstration_code="BPP_con",
            prefix="itr+dfp",
            ordem_exerc="ÚLTIMO",
            cd_conta="2.03.09",
        )
        
        
    @st.cache_data(ttl=60*5, show_spinner="Loading demonstration data...")
    def get_divida_liquida(_self, cd_cvm: str) -> DataFrame:
        return (
            _self.get_divida_bruta_lp(cd_cvm=cd_cvm)[["DT_REFER", "VL_CONTA_TRI"]]
            .merge(_self.get_divida_bruta_cp(cd_cvm=cd_cvm)[["DT_REFER", "VL_CONTA_TRI"]], on="DT_REFER", suffixes=("_lp", "_cp"))
            .merge(
                _self.get_caixa_e_equivalentes(cd_cvm=cd_cvm)[["DT_REFER", "VL_CONTA_TRI"]].rename(columns={"VL_CONTA_TRI": "VL_CONTA_TRI_caixa"}),
                on="DT_REFER",
            )
            .assign(VL_CONTA_TRI=lambda df: df["VL_CONTA_TRI_lp"] + df["VL_CONTA_TRI_cp"] - df["VL_CONTA_TRI_caixa"])
        )


    # --- Balanço: contas complementares para liquidez ---


    @st.cache_data(ttl=60*5, show_spinner="Loading demonstration data...")
    def get_ativo_circulante(_self, cd_cvm: str) -> DataFrame:
        return _self.get_demonstration(
            cd_cvm=cd_cvm,
            demonstration_code="BPA_con",
            prefix="itr+dfp",
            ordem_exerc="ÚLTIMO",
            cd_conta="1.01",
        )


    @st.cache_data(ttl=60*5, show_spinner="Loading demonstration data...")
    def get_passivo_circulante(_self, cd_cvm: str) -> DataFrame:
        return _self.get_demonstration(
            cd_cvm=cd_cvm,
            demonstration_code="BPP_con",
            prefix="itr+dfp",
            ordem_exerc="ÚLTIMO",
            cd_conta="2.01",
        )


    # --- DRE: uma conta por método, valor já isolado por trimestre ---


    @st.cache_data(ttl=60*5, show_spinner="Loading demonstration data...")
    def get_receita_liquida(_self, cd_cvm: str) -> DataFrame:
        return _self.get_demonstration(
            cd_cvm=cd_cvm,
            demonstration_code="DRE_con",
            prefix="itr+dfp",
            ordem_exerc="ÚLTIMO",
            cd_conta="3.01",
        )


    @st.cache_data(ttl=60*5, show_spinner="Loading demonstration data...")
    def get_lucro_bruto(_self, cd_cvm: str) -> DataFrame:
        return _self.get_demonstration(
            cd_cvm=cd_cvm,
            demonstration_code="DRE_con",
            prefix="itr+dfp",
            ordem_exerc="ÚLTIMO",
            cd_conta="3.03",
        )


    @st.cache_data(ttl=60*5, show_spinner="Loading demonstration data...")
    def get_ebit(_self, cd_cvm: str) -> DataFrame:
        # 3.05 = "Resultado Antes do Resultado Financeiro e dos Tributos" (aproximação padrão do EBIT).
        # Em bancos/seguradoras a DRE tem estrutura própria; validar antes de usar fora do setor não financeiro.
        return _self.get_demonstration(
            cd_cvm=cd_cvm,
            demonstration_code="DRE_con",
            prefix="itr+dfp",
            ordem_exerc="ÚLTIMO",
            cd_conta="3.05",
        )


    @st.cache_data(ttl=60*5, show_spinner="Loading demonstration data...")
    def get_resultado_antes_tributos(_self, cd_cvm: str) -> DataFrame:
        # Base (junto com get_imposto_renda_csll) para a taxa efetiva de IR usada no ROIC.
        return _self.get_demonstration(
            cd_cvm=cd_cvm,
            demonstration_code="DRE_con",
            prefix="itr+dfp",
            ordem_exerc="ÚLTIMO",
            cd_conta="3.07",
        )


    @st.cache_data(ttl=60*5, show_spinner="Loading demonstration data...")
    def get_imposto_renda_csll(_self, cd_cvm: str) -> DataFrame:
        return _self.get_demonstration(
            cd_cvm=cd_cvm,
            demonstration_code="DRE_con",
            prefix="itr+dfp",
            ordem_exerc="ÚLTIMO",
            cd_conta="3.08",
        )


    @st.cache_data(ttl=60*5, show_spinner="Loading demonstration data...")
    def get_lucro_liquido(_self, cd_cvm: str) -> DataFrame:
        return _self.get_demonstration(
            cd_cvm=cd_cvm,
            demonstration_code="DRE_con",
            prefix="itr+dfp",
            ordem_exerc="ÚLTIMO",
            cd_conta="3.11",
        )


    # --- DFC: fluxo de caixa operacional e depreciação/amortização ---


    @st.cache_data(ttl=60*5, show_spinner="Loading demonstration data...")
    def get_fluxo_caixa_operacional(_self, cd_cvm: str) -> DataFrame:
        return _self.get_demonstration(
            cd_cvm=cd_cvm,
            demonstration_code="DFC_MI_con",
            prefix="itr+dfp",
            ordem_exerc="ÚLTIMO",
            cd_conta="6.01",
        )


    @st.cache_data(ttl=60*5, show_spinner="Loading demonstration data...")
    def get_depreciacao_amortizacao(_self, cd_cvm: str) -> DataFrame:
        # O CD_CONTA da linha de D&A dentro de 6.01 muda de posição entre períodos/empresas
        # (ex.: 6.01.01.04/.05/.06 na mesma companhia), por isso a busca é pela descrição.
        try:
            return _self.get_demonstration_by_description(
                cd_cvm=cd_cvm,
                demonstration_code="DFC_MI_con",
                prefix="itr+dfp",
                ordem_exerc="ÚLTIMO",
                ds_conta_contains="deprecia",
                cd_conta_prefix="6.01",
            )
        except AccountNotFoundError:
            st.warning(f"Depreciação/Amortização não encontrada para cd_cvm={cd_cvm}; EBITDA usará apenas o EBIT.")
            return DataFrame(columns=["DT_REFER", "VL_CONTA_TRI"])


    # --- Indicadores derivados ---


    def _to_ltm(self, df: DataFrame, value_column: str = "VL_CONTA_TRI") -> DataFrame:
        """Converte uma série trimestral isolada em série 'últimos 12 meses' (soma móvel de 4 trimestres)."""
        df = df.sort_values("DT_REFER").copy()
        df[value_column] = df[value_column].rolling(window=4, min_periods=4).sum()
        return df.dropna(subset=[value_column]).reset_index(drop=True)


    # LTM de contas de fluxo, reaproveitadas por indicadores que dependem de dado de mercado
    # (P/L, PSR, EV/EBIT em FundamentalIndicatorService).


    @st.cache_data(ttl=60*5, show_spinner="Loading demonstration data...")
    def get_receita_liquida_ltm(_self, cd_cvm: str) -> DataFrame:
        return _self._to_ltm(_self.get_receita_liquida(cd_cvm=cd_cvm)[["DT_REFER", "VL_CONTA_TRI"]])


    @st.cache_data(ttl=60*5, show_spinner="Loading demonstration data...")
    def get_ebit_ltm(_self, cd_cvm: str) -> DataFrame:
        return _self._to_ltm(_self.get_ebit(cd_cvm=cd_cvm)[["DT_REFER", "VL_CONTA_TRI"]])


    @st.cache_data(ttl=60*5, show_spinner="Loading demonstration data...")
    def get_lucro_liquido_ltm(_self, cd_cvm: str) -> DataFrame:
        return _self._to_ltm(_self.get_lucro_liquido(cd_cvm=cd_cvm)[["DT_REFER", "VL_CONTA_TRI"]])


    @st.cache_data(ttl=60*5, show_spinner="Loading demonstration data...")
    def get_ebitda(_self, cd_cvm: str) -> DataFrame:
        ebit = _self.get_ebit(cd_cvm=cd_cvm)[["DT_REFER", "VL_CONTA_TRI"]]
        depreciacao = _self.get_depreciacao_amortizacao(cd_cvm=cd_cvm)[["DT_REFER", "VL_CONTA_TRI"]]

        ebitda_trimestral = (
            ebit
            .merge(depreciacao, on="DT_REFER", how="left", suffixes=("", "_dep"))
            .assign(
                VL_CONTA_TRI_dep=lambda df: df["VL_CONTA_TRI_dep"].fillna(0),
                VL_CONTA_TRI=lambda df: df["VL_CONTA_TRI"] + df["VL_CONTA_TRI_dep"],
            )
            [["DT_REFER", "VL_CONTA_TRI"]]
        )

        # EBITDA em base LTM (últimos 12 meses), convenção usual de mercado (ex.: Fundamentus).
        return _self._to_ltm(ebitda_trimestral)


    @st.cache_data(ttl=60*5, show_spinner="Loading demonstration data...")
    def get_margem_bruta(_self, cd_cvm: str) -> DataFrame:
        lucro_bruto_ltm = _self._to_ltm(_self.get_lucro_bruto(cd_cvm=cd_cvm)[["DT_REFER", "VL_CONTA_TRI"]])
        receita_liquida_ltm = _self.get_receita_liquida_ltm(cd_cvm=cd_cvm)

        return (
            lucro_bruto_ltm
            .merge(receita_liquida_ltm, on="DT_REFER", suffixes=("_lucro_bruto", "_receita_liquida"))
            .assign(VL_CONTA_TRI=lambda df: df["VL_CONTA_TRI_lucro_bruto"] / df["VL_CONTA_TRI_receita_liquida"])
            [["DT_REFER", "VL_CONTA_TRI"]]
        )


    @st.cache_data(ttl=60*5, show_spinner="Loading demonstration data...")
    def get_margem_ebit(_self, cd_cvm: str) -> DataFrame:
        ebit_ltm = _self.get_ebit_ltm(cd_cvm=cd_cvm)
        receita_liquida_ltm = _self.get_receita_liquida_ltm(cd_cvm=cd_cvm)

        return (
            ebit_ltm
            .merge(receita_liquida_ltm, on="DT_REFER", suffixes=("_ebit", "_receita_liquida"))
            .assign(VL_CONTA_TRI=lambda df: df["VL_CONTA_TRI_ebit"] / df["VL_CONTA_TRI_receita_liquida"])
            [["DT_REFER", "VL_CONTA_TRI"]]
        )


    @st.cache_data(ttl=60*5, show_spinner="Loading demonstration data...")
    def get_margem_liquida(_self, cd_cvm: str) -> DataFrame:
        lucro_liquido_ltm = _self.get_lucro_liquido_ltm(cd_cvm=cd_cvm)
        receita_liquida_ltm = _self.get_receita_liquida_ltm(cd_cvm=cd_cvm)

        return (
            lucro_liquido_ltm
            .merge(receita_liquida_ltm, on="DT_REFER", suffixes=("_lucro_liquido", "_receita_liquida"))
            .assign(VL_CONTA_TRI=lambda df: df["VL_CONTA_TRI_lucro_liquido"] / df["VL_CONTA_TRI_receita_liquida"])
            [["DT_REFER", "VL_CONTA_TRI"]]
        )


    @st.cache_data(ttl=60*5, show_spinner="Loading demonstration data...")
    def get_roe(_self, cd_cvm: str) -> DataFrame:
        lucro_liquido_ltm = _self.get_lucro_liquido_ltm(cd_cvm=cd_cvm)
        patrimonio_liquido = _self.get_patrimonio_liquido_total(cd_cvm=cd_cvm)[["DT_REFER", "VL_CONTA_TRI"]]

        return (
            lucro_liquido_ltm
            .merge(patrimonio_liquido, on="DT_REFER", suffixes=("_lucro_liquido", "_pl"))
            .assign(VL_CONTA_TRI=lambda df: df["VL_CONTA_TRI_lucro_liquido"] / df["VL_CONTA_TRI_pl"])
            [["DT_REFER", "VL_CONTA_TRI"]]
        )


    @st.cache_data(ttl=60*5, show_spinner="Loading demonstration data...")
    def get_roic(_self, cd_cvm: str) -> DataFrame:
        ebit_ltm = _self.get_ebit_ltm(cd_cvm=cd_cvm)
        ebt_ltm = _self._to_ltm(_self.get_resultado_antes_tributos(cd_cvm=cd_cvm)[["DT_REFER", "VL_CONTA_TRI"]])
        ir_ltm = _self._to_ltm(_self.get_imposto_renda_csll(cd_cvm=cd_cvm)[["DT_REFER", "VL_CONTA_TRI"]])
        divida_liquida = _self.get_divida_liquida(cd_cvm=cd_cvm)[["DT_REFER", "VL_CONTA_TRI"]]
        patrimonio_liquido = _self.get_patrimonio_liquido_total(cd_cvm=cd_cvm)[["DT_REFER", "VL_CONTA_TRI"]]

        return (
            ebit_ltm
            .merge(ebt_ltm, on="DT_REFER", suffixes=("_ebit", "_ebt"))
            .merge(ir_ltm.rename(columns={"VL_CONTA_TRI": "VL_CONTA_TRI_ir"}), on="DT_REFER")
            .merge(divida_liquida.rename(columns={"VL_CONTA_TRI": "VL_CONTA_TRI_divida_liquida"}), on="DT_REFER")
            .merge(patrimonio_liquido.rename(columns={"VL_CONTA_TRI": "VL_CONTA_TRI_pl"}), on="DT_REFER")
            .assign(
                # IR/CSLL costuma vir com sinal negativo (despesa); taxa positiva = alíquota efetiva usual.
                taxa_ir=lambda df: -df["VL_CONTA_TRI_ir"] / df["VL_CONTA_TRI_ebt"],
                VL_CONTA_TRI=lambda df: (
                    df["VL_CONTA_TRI_ebit"] * (1 - df["taxa_ir"])
                    / (df["VL_CONTA_TRI_divida_liquida"] + df["VL_CONTA_TRI_pl"])
                ),
            )
            [["DT_REFER", "VL_CONTA_TRI"]]
        )


    @st.cache_data(ttl=60*5, show_spinner="Loading demonstration data...")
    def get_liquidez_corrente(_self, cd_cvm: str) -> DataFrame:
        ativo_circulante = _self.get_ativo_circulante(cd_cvm=cd_cvm)[["DT_REFER", "VL_CONTA_TRI"]]
        passivo_circulante = _self.get_passivo_circulante(cd_cvm=cd_cvm)[["DT_REFER", "VL_CONTA_TRI"]]

        return (
            ativo_circulante
            .merge(passivo_circulante, on="DT_REFER", suffixes=("_ativo", "_passivo"))
            .assign(VL_CONTA_TRI=lambda df: df["VL_CONTA_TRI_ativo"] / df["VL_CONTA_TRI_passivo"])
            [["DT_REFER", "VL_CONTA_TRI"]]
        )


    @st.cache_data(ttl=60*5, show_spinner="Loading demonstration data...")
    def get_divida_liquida_sobre_patrimonio_liquido(_self, cd_cvm: str) -> DataFrame:
        divida_liquida = _self.get_divida_liquida(cd_cvm=cd_cvm)[["DT_REFER", "VL_CONTA_TRI"]]
        patrimonio_liquido = _self.get_patrimonio_liquido_total(cd_cvm=cd_cvm)[["DT_REFER", "VL_CONTA_TRI"]]

        return (
            divida_liquida
            .merge(patrimonio_liquido, on="DT_REFER", suffixes=("_divida_liquida", "_pl"))
            .assign(VL_CONTA_TRI=lambda df: df["VL_CONTA_TRI_divida_liquida"] / df["VL_CONTA_TRI_pl"])
            [["DT_REFER", "VL_CONTA_TRI"]]
        )


    @st.cache_data(ttl=60*5, show_spinner="Loading demonstration data...")
    def get_divida_liquida_sobre_ebitda(_self, cd_cvm: str) -> DataFrame:
        divida_liquida = _self.get_divida_liquida(cd_cvm=cd_cvm)[["DT_REFER", "VL_CONTA_TRI"]]
        ebitda = _self.get_ebitda(cd_cvm=cd_cvm)[["DT_REFER", "VL_CONTA_TRI"]]

        return (
            divida_liquida
            .merge(ebitda, on="DT_REFER", suffixes=("_divida_liquida", "_ebitda"))
            .assign(VL_CONTA_TRI=lambda df: df["VL_CONTA_TRI_divida_liquida"] / df["VL_CONTA_TRI_ebitda"])
            [["DT_REFER", "VL_CONTA_TRI"]]
        )
        

    @st.cache_data(ttl=60*5, show_spinner="Loading demonstration data...")
    def get_patrimonio_liquido(_self, cd_cvm: str) -> DataFrame:
        
        patrimonio_liquido_total: DataFrame = _self.get_patrimonio_liquido_total(cd_cvm=cd_cvm)
    
        try:

            participacao_nao_controladores: DataFrame = _self.get_participacao_nao_controladores(cd_cvm=cd_cvm)

        except Exception:

            participacao_nao_controladores = None

        if participacao_nao_controladores is not None and not participacao_nao_controladores.empty:

            patrimonio_liquido = (
                patrimonio_liquido_total[["DT_REFER", "VL_CONTA_TRI"]]
                .merge(
                    participacao_nao_controladores[["DT_REFER", "VL_CONTA_TRI"]],
                    on="DT_REFER",
                    how="left",
                    suffixes=("", "_nao_controladores"),
                )
                .assign(
                    VL_CONTA_TRI_nao_controladores=lambda df: df["VL_CONTA_TRI_nao_controladores"].fillna(0),
                    VL_CONTA_TRI=lambda df: df["VL_CONTA_TRI"] - df["VL_CONTA_TRI_nao_controladores"],
                )
            )

        else:

            patrimonio_liquido = patrimonio_liquido_total

        return patrimonio_liquido
        