import dash
import dash_ag_grid as dag
import dash_bootstrap_components as dbc
import const

_reviewed_tab_content = dbc.Stack(
    [
        dash.html.H4(f"0 Classifications reviewed", className="mt-3", id="reviewed-header"),
        dbc.Row(
            dbc.Col(
                dag.AgGrid(
                    id="reviewed-data",
                    rowData=[],
                    columnDefs=[
                        {
                            "field": const.SUMMARY_COLUMN_NAME_KEY,
                            "flex": 1,
                            "headerName": "Column",
                            "filter": True,
                        },
                        {
                            "field": const.SUMMARY_PII_ENTITY_KEY,
                            "flex": 1,
                            "headerName": "Classification tag",
                            "cellRenderer": "TagRenderer"
                        },
                        {
                            "field": const.SUMMARY_RATIONALES_KEY,
                            "flex": 1,
                            "headerName": "Rationale",
                            "cellRenderer": "RenameRenderer"
                        },
                        {
                            "field": const.SUMMARY_SAMPLES_KEY,
                            "cellRenderer": "ExpandableListRenderer",
                            "wrapText": True,
                            "autoHeight": True,
                            "flex": 2,
                            "headerName": "Samples",
                        },
                        {
                            "field": const.RESULT_TABLE_REVIEW_STATUS_KEY,
                            "flex": 1,
                            "headerName": "Review Status",
                            "cellRenderer": "RenameRenderer"
                        },
                    ],
                    rowStyle={
                        'backgroundColor': 'white'
                    },
                    className="ag-theme-alpine",
                    getRowId=f"params.data.{const.SUMMARY_COLUMN_NAME_KEY} + params.data.{const.SUMMARY_PII_ENTITY_KEY}",
                    style={"height": "32rem", "width": "100%"},
                ),
                width=12,
            )
        ),
    ],
    gap=3,
)

_to_review_tab_content = dbc.Stack(
    [
        dash.html.H4(
            f"0 Classifications to review", className="mt-3", id="unreviewed-header"
        ),
        dbc.Row(
            dbc.Col(
                dag.AgGrid(
                    id="unreviewed-data",
                    rowData=[],
                    columnDefs=[
                        {
                            "field": const.SUMMARY_COLUMN_NAME_KEY,
                            "headerCheckboxSelection": True,
                            "checkboxSelection": True,
                            "flex": 1,
                            "headerName": "Column",
                            "filter": True,
                        },
                        {
                            "field": const.SUMMARY_PII_ENTITY_KEY,
                            "flex": 1,
                            "headerName": "Classification tag",
                            "cellRenderer": "TagRenderer"
                        },
                        {
                            "field": const.SUMMARY_RATIONALES_KEY,
                            "flex": 1,
                            "headerName": "Rationale",
                            "cellRenderer": "RenameRenderer"
                        },
                        {
                            "field": const.SUMMARY_SAMPLES_KEY,
                            "cellRenderer": "ExpandableListRenderer",
                            "wrapText": True,
                            "autoHeight": True,
                            "flex": 2,
                            "headerName": "Samples",
                        },
                    ],
                    dashGridOptions={
                        "rowSelection": "multiple",
                        "rowMultiSelectWithClick": True,
                        "isRowSelectable": {"function": f"!!params.data.{const.SUMMARY_PII_ENTITY_KEY}"},
                    },
                    rowStyle={
                        'backgroundColor': 'white'
                    },
                    className="ag-theme-alpine",
                    getRowId=f"params.data.{const.SUMMARY_COLUMN_NAME_KEY} + params.data.{const.SUMMARY_PII_ENTITY_KEY}",
                    style={"height": "32rem", "width": "100%"},
                ),
                width=12,
            )
        ),
        dbc.Row(
            [
                dbc.Col(
                    dbc.Button(
                        "Apply classification tags",
                        id="apply-tags-button",
                        n_clicks=0,
                        color="primary",
                        className="me-2",
                        style={"width": "100%"},
                    ),
                    width="4",
                ),
                dbc.Col(
                    dbc.Button(
                        "Reject",
                        id="reject-button",
                        n_clicks=0,
                        color="secondary",
                        style={"width": "100%"},
                    ),
                    width="4",
                ),
            ],
        ),
    ],
    gap=3,
)

layout = dbc.Container(
    [
        dbc.Toast(
            "",
            header="Error",
            id="error-notification",
            class_name="error-toast",
            icon="danger",
            dismissable=True,
            is_open=False,
        ),
        dbc.Stack(
            [
                dash.html.H2("Data classification"),
                dash.html.Div(
                    children=[
                        dbc.FormText(
                            "Full source table name (e.g. catalog.schema.table)",
                            class_name="mb-4",
                        ),
                        dbc.Input(id="source-table-input", value=""),
                    ]
                ),
                dbc.Spinner(
                    id="content-spinner",
                    color="primary",
                    spinner_class_name="center-item",
                    spinner_style={"display": "none"},
                ),
                dash.html.Div(
                    dbc.Tabs(
                        [
                            dbc.Tab(
                                _to_review_tab_content,
                                tab_id="to-review-tab",
                                label="To review",
                            ),
                            dbc.Tab(
                                _reviewed_tab_content,
                                label="Reviewed",
                                tab_id="reviewed-tab",
                            ),
                        ],
                        active_tab="to-review-tab",
                    ),
                    id="tab-container",
                    style={"visibility": "hidden"},
                ),
            ],
            gap=3,
        ),
    ],
    className="page-container",
    fluid=True,
)
