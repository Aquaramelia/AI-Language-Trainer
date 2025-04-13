from st_helpers.aggrid_html_cell_renderer import HtmlCellRenderer
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode, JsCode, StAggridTheme


def display_grid(category_df, category_selection):
    CustomHtmlCellRenderer = JsCode(HtmlCellRenderer)
                    
    custom_theme = StAggridTheme(base="quartz").withParams(
        fontSize=16,
        rowBorder=False,
        backgroundColor="#273aa4c7",
        foregroundColor="#fff"
    ).withParts('iconSetAlpine')  

    gb = GridOptionsBuilder.from_dataframe(category_df[["word_md"]])
    gb.configure_column(
        "word_md",
        header_name=f"Words in category: {category_selection}",
        cellRenderer=CustomHtmlCellRenderer
    )

    gb.configure_selection(
        selection_mode="single",
        suppressRowDeselection=True,
        suppressRowClickSelection=False,
        pre_selected_rows=[0]
    )

    grid_options = gb.build()
    grid_options["masterDetail"] = False

    # Display grid
    grid_response = AgGrid(
        category_df[["word_md"]],
        gridOptions=grid_options,
        height=600,
        update_mode=GridUpdateMode.SELECTION_CHANGED,
        allow_unsafe_jscode=True,
        enable_enterprise_modules=False,
        fit_columns_on_grid_load=True,
        theme=custom_theme
    )
    return grid_response