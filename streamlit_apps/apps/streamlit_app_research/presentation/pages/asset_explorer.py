

# --- Libraries ---


from streamlit_apps.apps.streamlit_app_research.application.services import (
    AssetRegistryService, 
    AssetRegistryDTO,
    AssetPriceService,
    AssetDemonstrationService
    )

from streamlit_apps.apps.streamlit_app_research.application.analytics import (
    PriceRegressionAnalysis,
    ReturnVolatilityAnalysis
)

from streamlit_apps.apps.streamlit_app_research.presentation.components.charts import (
    render_asset_price_line_chart,
    render_asset_price_regression_chart,
    render_asset_price_regression_distribution_chart,
    render_asset_returns_line_chart,
    render_asset_balance_sheet_chart,
    ChartSeries,
    render_asset_returns_distribution_bar_chart,
    render_asset_return_vs_volatility_chart
)


from streamlit_apps.apps.streamlit_app_research.presentation.components import (
    styled_tabs,
    render_moving_average_select_widget,
    render_information_table_widget
)


import streamlit as st
from pandas import DataFrame


# --- Service Initialization ---


asset_registry_service: list[AssetRegistryDTO] = AssetRegistryService().add_company_names().add_cvm_cias_cad().to_dto_list()
asset_price_service = AssetPriceService()
asset_demonstration_service = AssetDemonstrationService()


# --- Asset Explorer ---


selected_asset = st.selectbox(
    f"Selected Asset — Qty: {len(asset_registry_service)}",
    options=[asset for asset in asset_registry_service],
    format_func=lambda asset: f"{asset.ticker}  —  {asset.company_name[0] if asset.company_name else ''}", 
    key="selected_asset",
)

preco, retornos, detalhes, balanco_patrimonial, demonstrativos_resultados = styled_tabs([
    "Preço", "Retornos", "Detalhes", "Balanço Patrimonial", "Demonstrativos de Resultados"
])


# --- Price Section ---


with preco:
    
    st.write(f"Preço do ativo {selected_asset.ticker}")
    
    try:
    
        price: DataFrame = asset_price_service.get_asset_price(tickers=selected_asset.ticker, period="10y")
        
        render_asset_price_line_chart(price)
        st.dataframe(price[["Date", "Adj Close", "Volume"]].tail(3))
    
    except Exception as e:
        
        st.error(f"Erro ao obter o preço do ativo: {e}")
    
    regressao_de_preco, indicator2, indicator3 = styled_tabs([
        "Regressão de Preço", "Indicador 2", "Indicador 3"
    ])
    
    with regressao_de_preco:
        
        analysis = PriceRegressionAnalysis(price, moving_average=render_moving_average_select_widget("PriceRegressionAnalysis"))
        
        render_asset_price_regression_chart(analysis)
        render_asset_price_regression_distribution_chart(analysis)
    

# --- Returns Section ---


with retornos:
    
    st.write(f"Retornos do ativo {selected_asset.ticker}")

    try:
        
        daily_returns: DataFrame = asset_price_service.get_asset_returns(tickers=selected_asset.ticker, period="10y")
        
        render_asset_returns_line_chart(daily_returns)
        st.dataframe(daily_returns[["Date", "daily_returns"]].tail(3))
        
    except Exception as e:
        
        st.error(f"Erro ao obter os retornos do ativo: {e}")
        
    distribuicao, retorno_vs_volatilidade, indicador3 = styled_tabs([
        "Distribuição", "Retorno vs Volatilidade", "Indicador 3"])
    
    with distribuicao:

        render_asset_returns_distribution_bar_chart(daily_returns)

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
    
    st.write(f"Detalhes do ativo {selected_asset.ticker}")

    col1, col2 = st.columns([1.2, 1])
    
    with col1:
        
        render_information_table_widget(
            data={
                "Código de Negociação": selected_asset.ticker if selected_asset.ticker else "N/A",
                "Código CVM": selected_asset.cd_cvm if selected_asset.cd_cvm else "N/A",
                "Nome da Empresa": selected_asset.company_name if selected_asset.company_name else "N/A",
                "CNPJ": selected_asset.cnpj_cia if selected_asset.cnpj_cia else "N/A",
                "Website": selected_asset.website if selected_asset.website else "N/A",
                "Classificação da Indústria": selected_asset.industry_classification if selected_asset.industry_classification else "N/A",
                "Atividade": selected_asset.activity if selected_asset.activity else "N/A"
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
    
    
# --- Balance Sheet Section ---


with balanco_patrimonial:
    
    st.write(f"Balanço Patrimonial do ativo {selected_asset.ticker}")
    
    try:

        ativo: DataFrame = asset_demonstration_service.get_ativo(cd_cvm=selected_asset.cd_cvm)
        divida_bruta_lp: DataFrame = asset_demonstration_service.get_divida_bruta_lp(cd_cvm=selected_asset.cd_cvm)
        divida_bruta_cp: DataFrame = asset_demonstration_service.get_divida_bruta_cp(cd_cvm=selected_asset.cd_cvm)
        caixa_e_equivalentes: DataFrame = asset_demonstration_service.get_caixa_e_equivalentes(cd_cvm=selected_asset.cd_cvm)
        patrimonio_liquido_total: DataFrame = asset_demonstration_service.get_patrimonio_liquido_total(cd_cvm=selected_asset.cd_cvm)
        divida_liquida: DataFrame = asset_demonstration_service.get_divida_liquida(cd_cvm=selected_asset.cd_cvm)
        patrimonio_liquido: DataFrame = asset_demonstration_service.get_patrimonio_liquido(cd_cvm=selected_asset.cd_cvm)

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


# --- Income Statement Section ---


with demonstrativos_resultados:
    
    st.write(f"Demonstrativos de Resultados do ativo {selected_asset.ticker}")

    receita_liquida: DataFrame = asset_demonstration_service.get_receita_liquida(cd_cvm=selected_asset.cd_cvm)
    lucro_liquido: DataFrame = asset_demonstration_service.get_lucro_liquido(cd_cvm=selected_asset.cd_cvm)
    
    
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