from st_helpers.aggrid_html_cell_renderer import HtmlCellRenderer
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode, JsCode, StAggridTheme
import pandas as pd

def display_grid(feed_df: pd.DataFrame, feed_selection: str):
    CustomHtmlCellRenderer = JsCode(HtmlCellRenderer)
                    
    custom_theme = StAggridTheme(base="quartz").withParams(
        fontSize=16,
        rowBorder=False,
        backgroundColor="#273aa4c7",
        foregroundColor="#fff"
    ).withParts('iconSetAlpine')  

    gb = GridOptionsBuilder.from_dataframe(feed_df[["title"]])
    gb.configure_column(
        "title",
        header_name=f"Words in category: {feed_selection}",
        cellRenderer=CustomHtmlCellRenderer,
        autoHeight=True,
        wrapText=True
    )

    gb.configure_selection(
        selection_mode="single",
        suppressRowDeselection=True,
        suppressRowClickSelection=False,
        pre_selected_rows=[0]
    )
    
    gb.configure_grid_options(
        suppressHorizontalScroll=True
    )

    grid_options = gb.build()
    grid_options["masterDetail"] = False

    # Display grid
    grid_response = AgGrid(
        feed_df[["title"]],
        gridOptions=grid_options,
        height=600,
        update_mode=GridUpdateMode.SELECTION_CHANGED,
        allow_unsafe_jscode=True,
        enable_enterprise_modules=False,
        fit_columns_on_grid_load=True,
        theme=custom_theme
    )
    return grid_response