
import pandas as pd
import streamlit as st


# Renderiza tabelas de monitoramento e ranking com formatação e cores configuráveis.
def render_asset_monitor_table_widget(
    data: dict | pd.DataFrame,
    percent_columns: list[str] | None = None,
    color_columns: dict[str, dict] | None = None,
    formatters: dict[str, str] | None = None,
    date_columns: list[str] | None = None,
    sort_by: str | None = "current_drawdown%",
    ascending: bool = True,
) -> None:
    """Exibe uma tabela Streamlit com formatação e gradientes configuráveis.

    Args:
        data: Dicionário de métricas indexado por ativo, como o retorno de
            ``AssetMonitoring.get_stats_by_ticker()``, ou um DataFrame pronto.
        percent_columns: Colunas exibidas como percentual. Quando ``None``,
            nenhuma coluna recebe formatação percentual.
        color_columns: Mapa de configurações de cor por coluna. Cada chave é
            uma coluna e o valor aceita ``cmap``, ``vmin`` e ``vmax`` usados
            por ``pandas.Styler.background_gradient``. Quando ``None``,
            nenhuma coluna recebe cor.
        formatters: Mapa ``coluna: formato`` adicional para ``Styler.format``.
            Por padrão preserva ``last_price`` como moeda brasileira.
        date_columns: Colunas a converter para data, sem horário. Por padrão
            converte ``date_last_price`` quando essa coluna existir.
        sort_by: Coluna usada para ordenar a tabela. O padrão preserva a
            ordenação por drawdown; passe ``None`` para manter a ordem recebida.
        ascending: Direção da ordenação quando ``sort_by`` for informada.
    """
    if isinstance(data, pd.DataFrame):
        df = data.copy()
    else:
        df = pd.DataFrame.from_dict(data, orient="index")
        df = df.reset_index().rename(columns={"index": "ativo"})

    percent_columns = percent_columns or []
    percent_columns = [column for column in percent_columns if column in df]

    if date_columns is None:
        date_columns = ["date_last_price"]
    for column in date_columns:
        if column in df:
            df[column] = pd.to_datetime(df[column]).dt.date

    if sort_by is not None and sort_by in df:
        df = df.sort_values(sort_by, ascending=ascending)

    default_formatters = {column: "{:.1%}" for column in percent_columns}
    if "last_price" in df:
        default_formatters["last_price"] = "R$ {:.2f}"
    if formatters:
        default_formatters.update(formatters)

    if color_columns is None:
        color_columns = {
            column: {"cmap": "RdYlGn", "vmin": -0.30, "vmax": 0.30}
            for column in percent_columns
        }

    styled = df.style.format(default_formatters)
    for column, options in color_columns.items():
        if column in df:
            styled = styled.background_gradient(subset=[column], **options)

    row_height = 35
    header_height = 38
    table_height = header_height + row_height * len(df)

    st.dataframe(styled, hide_index=True, width="stretch", height=table_height)