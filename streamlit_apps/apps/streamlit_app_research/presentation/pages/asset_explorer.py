

# --- Imports ---


from streamlit_apps.apps.streamlit_app_research.application.services.asset_service import AssetService
from streamlit_apps.apps.streamlit_app_research.application.services.asset_fundamental_indicator_service import AssetFundamentalIndicatorService
from streamlit_apps.apps.streamlit_app_research.application.services.asset_price_service import AssetPriceService
from streamlit_apps.apps.streamlit_app_research.application.services.asset_demonstration_service import AssetDemonstrationService
from streamlit_apps.apps.streamlit_app_research.application.analytics.price_regression_analysis import PriceRegressionAnalysis
from streamlit_apps.apps.streamlit_app_research.application.analytics.return_volatility_analysis import ReturnVolatilityAnalysis

from streamlit_apps.apps.streamlit_app_research.presentation.components.moving_average_select_widget import render_moving_average_select_widget
from streamlit_apps.apps.streamlit_app_research.presentation.components.asset_select_widget import render_asset_select_widget
from streamlit_apps.apps.streamlit_app_research.presentation.components.charts.asset_price_line_chart import render_asset_price_line_chart
from streamlit_apps.apps.streamlit_app_research.presentation.components.charts.asset_returns_line_chart import render_asset_returns_line_chart
from streamlit_apps.apps.streamlit_app_research.presentation.components.charts.asset_returns_distribution_bar_chart import render_asset_returns_distribution_bar_chart
from streamlit_apps.apps.streamlit_app_research.presentation.components.styled_tabs_widget import styled_tabs
from streamlit_apps.apps.streamlit_app_research.presentation.components.charts.asset_price_regression_chart import (
    render_asset_price_regression_chart,
    render_asset_price_regression_distribution_chart,
)
from streamlit_apps.apps.streamlit_app_research.presentation.components.charts.asset_return_vs_volatility import (
    render_asset_return_vs_volatility_chart,
)
from streamlit_apps.apps.streamlit_app_research.presentation.components.charts.asset_balance_sheet_chart import (
    render_asset_balance_sheet_chart,
    ChartSeries,
)
from streamlit_apps.apps.streamlit_app_research.presentation.components.information_table_widget import render_information_table_widget

from streamlit_apps.apps.streamlit_app_research.shared.dto.asset_dto import AssetTradingCodeDTO, AssetDetailsDTO

import streamlit as st
from pandas import DataFrame


# --- Services ---


asset_service = AssetService()
asset_price_service = AssetPriceService()
asset_demonstration_service = AssetDemonstrationService()
asset_fundamental_indicator_service = AssetFundamentalIndicatorService()


# --- Page ---


st.title("Asset Explorer")

asset: AssetTradingCodeDTO = render_asset_select_widget(asset_service.list_trading_codes())

(
    preco, 
    retornos, 
    detalhes,
    balanco_patrimonial,
    demonstrativos_de_resultados
) = styled_tabs(
    [
        "Preço", 
        "Retornos", 
        "Detalhes",
        "Balanço Patrimonial",
        "Demonstrativos de Resultados"
    ]
)


with preco:

    try:
        
        price: DataFrame = asset_price_service.get_asset_price(
            tickers=asset.trading_code,
            period="10y"
            )
        
        render_asset_price_line_chart(price)
        
        st.dataframe(price[["Date", "Adj Close", "Volume"]].tail(5))
        
    except Exception as e:
        
        st.error(e.args[0])
    
    (
        regressao_de_preco, 
        indicator2, 
        indicator3
    ) = styled_tabs(
        [
            "Regressão de Preço", 
            "Indicador 2", 
            "Indicador 3"
        ]
    )
    
    with regressao_de_preco:

        analysis = PriceRegressionAnalysis(
            price=price,
            moving_average=render_moving_average_select_widget(key="asset_explorer_price_regression"),
        )

        render_asset_price_regression_chart(analysis)
        render_asset_price_regression_distribution_chart(analysis)


with retornos:
    
    daily_returns: DataFrame = asset_price_service.get_asset_returns(
        tickers=asset.trading_code,
        period="10y"
    )
    
    render_asset_returns_line_chart(daily_returns)
    
    st.dataframe(daily_returns[["Date", "daily_returns"]].tail(5))
    
    (
        distribuicao, 
        retorno_vs_volatilidade, 
        indicador3
    ) = styled_tabs(
        [
            "Distribuição", 
            "Retorno vs Volatilidade", 
            "Indicador 3"
        ]
    )
    
    with distribuicao:
        
        render_asset_returns_distribution_bar_chart(
            daily_returns=daily_returns,
            moving_average=render_moving_average_select_widget(key="asset_explorer_returns_distribution"),
        )
    
    with retorno_vs_volatilidade:

        analysis = ReturnVolatilityAnalysis(
            price=price,
            window=render_moving_average_select_widget(
                options = [20, 10, 5, 50, 100, 200],
                key="asset_explorer_return_vs_volatility"
            ),
        )

        render_asset_return_vs_volatility_chart(analysis)
        

with detalhes:

    col1, col2 = st.columns([1.2, 1])
    
    with col1:
        
        asset_details: AssetDetailsDTO | None = asset_service.get_details(trading_code=asset.trading_code)
        
        render_information_table_widget(
            data={
                "Código de Negociação": asset_details.trading_code if asset_details else "N/A",
                "Código CVM": asset_details.cvm_code if asset_details else "N/A",
                "Nome da Empresa": asset_details.company_name if asset_details else "N/A",
                "CNPJ": asset_details.cnpj if asset_details else "N/A",
                "Classificação da Indústria": asset_details.industry_classification if asset_details else "N/A",
                "Atividade": asset_details.activity if asset_details else "N/A"
            },
            title="Informações do Ativo"
        )
        
    with col2:
        
        render_information_table_widget(
            data={
                "Último Preço": "N/A",
                "Último Balanço Processado": "N/A",
                "Nro. Ações": "N/A"
            },
            title=""
        )
        
    col3, col4 = st.columns([1, 1])
    
    with col3:

        # pl = asset_fundamental_indicator_service.get_pl(cd_cvm=asset.cvm_code, preco=price)
        # pl_fmt = f"{pl['VL_CONTA_TRI'].dropna().iloc[-1]:,.2f}" if not pl.empty else "N/A"
        
        # dividend_yield = asset_fundamental_indicator_service.get_dividend_yield(cd_cvm=asset.cvm_code, preco=price)
        # dividend_yield_fmt = f"{dividend_yield['VL_CONTA_TRI'].dropna().iloc[-1]:,.2f}%" if not dividend_yield.empty else "N/A"
        
        render_information_table_widget(
            data={
                "P/L": "N/A",
                "Dividend Yield": "N/A"
            },
            title="Indicadores"
        )

    with col4:
        
        # try:
            
        #     valor_de_mercado: DataFrame = asset_fundamental_indicator_service.get_valor_de_mercado(cd_cvm=asset.cvm_code, preco=price)
        #     valor_de_mercado_fmt = f"R$ {valor_de_mercado['VL_CONTA_TRI'].dropna().iloc[-1]:,.0f} mil"
            
        # except Exception:
            
        #     valor_de_mercado_fmt = "N/A"
        
        render_information_table_widget(
            data={
                "Valor de Mercado": "N/A",
                "Indicador 4": "N/A"
            },
            title="Indicadores"
        )
    

with balanco_patrimonial:

    if asset.cvm_code is None:

        st.info("Não há dados de balanço disponíveis para este ativo.")

    else:
  
        try:

            ativo: DataFrame = asset_demonstration_service.get_ativo(cd_cvm=asset.cvm_code)
            divida_bruta_lp: DataFrame = asset_demonstration_service.get_divida_bruta_lp(cd_cvm=asset.cvm_code)
            divida_bruta_cp: DataFrame = asset_demonstration_service.get_divida_bruta_cp(cd_cvm=asset.cvm_code)
            caixa_e_equivalentes: DataFrame = asset_demonstration_service.get_caixa_e_equivalentes(cd_cvm=asset.cvm_code)
            patrimonio_liquido_total: DataFrame = asset_demonstration_service.get_patrimonio_liquido_total(cd_cvm=asset.cvm_code)
            divida_liquida: DataFrame = asset_demonstration_service.get_divida_liquida(cd_cvm=asset.cvm_code)
            patrimonio_liquido: DataFrame = asset_demonstration_service.get_patrimonio_liquido(cd_cvm=asset.cvm_code)

            render_asset_balance_sheet_chart(
                series=[ChartSeries(df=ativo, x="DT_REFER", y="VL_CONTA_TRI", name="Ativo Total")],
                title="Ativo Total",
                xlabel=None,
                ylabel="R$ (mil)",
            )

            render_asset_balance_sheet_chart(
                series=[
                    ChartSeries(df=divida_bruta_lp, x="DT_REFER", y="VL_CONTA_TRI", name="Dívida Bruta LP"),
                    ChartSeries(df=divida_bruta_cp, x="DT_REFER", y="VL_CONTA_TRI", name="Dívida Bruta CP"),
                    ChartSeries(df=divida_liquida, x="DT_REFER", y="VL_CONTA_TRI", name="Dívida Líquida"),
                ],
                title="Endividamento",
                xlabel=None,
                ylabel="R$ (mil)",
            )

            render_asset_balance_sheet_chart(
                series=[ChartSeries(df=patrimonio_liquido, x="DT_REFER", y="VL_CONTA_TRI", name="Patrimônio Líquido")],
                title="Patrimônio Líquido",
                xlabel=None,
                ylabel="R$ (mil)",
            )
            
            st.dataframe(ativo.tail(3))
            st.dataframe(divida_bruta_lp.tail(3))
            st.dataframe(divida_liquida.tail(3))

        except Exception as e:

            st.error(e.args[0])
    

with demonstrativos_de_resultados:
    
    if asset.cvm_code is None:

        st.info("Não há dados de demonstrativos de resultados disponíveis para este ativo.")
    
    else:
        
        receita_liquida: DataFrame = asset_demonstration_service.get_receita_liquida(cd_cvm=asset.cvm_code)
        lucro_liquido: DataFrame = asset_demonstration_service.get_lucro_liquido(cd_cvm=asset.cvm_code)
        
        
        render_asset_balance_sheet_chart(
            series=[ChartSeries(df=receita_liquida, x="DT_REFER", y="VL_CONTA_TRI", name="Receita Líquida")],
            title="Receita Líquida",
            xlabel=None,
            ylabel="R$ (mil)",
        )

        render_asset_balance_sheet_chart(
            series=[ChartSeries(df=lucro_liquido, x="DT_REFER", y="VL_CONTA_TRI", name="Lucro Líquido")],
            title="Lucro Líquido",
            xlabel=None,
            ylabel="R$ (mil)",
            chart_type="bar"
        )
        
        st.dataframe(receita_liquida.tail(3))  
        st.dataframe(lucro_liquido.tail(3))