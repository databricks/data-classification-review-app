import dash
import dash_ag_grid as dag
import dash_bootstrap_components as dbc
import const

_common_column_defs = [
    {
        "field": const.SUMMARY_PII_ENTITY_KEY,
        "flex": 1,
        "headerName": "Classification tag",
        "cellRenderer": "TagRenderer",
    },
    {
        "field": const.SUMMARY_MATCH_SCORE_KEY,
        "flex": 0.5,
        "headerName": "Match",
        "sort": "desc",
        "cellRenderer": "MatchScoreRenderer",
    },
    {
        "field": const.SUMMARY_SAMPLES_KEY,
        "cellRenderer": "ExpandableListRenderer",
        "wrapText": True,
        "autoHeight": True,
        "flex": 2,
        "headerName": "Samples",
    },
]

reviewed_grid_id = "reviewed-data"

reviewed_grid = dag.AgGrid(
    id=reviewed_grid_id,
    rowData=[],
    columnDefs=[
        {
            "field": const.SUMMARY_COLUMN_NAME_KEY,
            "flex": 1,
            "headerName": "Column",
            "filter": True,
        },
        *_common_column_defs,
        {
            "field": const.RESULT_TABLE_REVIEW_STATUS_KEY,
            "flex": 1,
            "headerName": "Review Status",
            "cellRenderer": "RenameRenderer",
            "filter": True,
        },
    ],
    rowStyle={"backgroundColor": "white"},
    className="ag-theme-alpine",
    getRowId=f"params.data.{const.SUMMARY_COLUMN_NAME_KEY} + params.data.{const.SUMMARY_PII_ENTITY_KEY}",
    style={"height": "32rem", "width": "100%"},
)

unreviewed_grid_id = "unreviewed-data"

unreviewed_grid = dag.AgGrid(
    id=unreviewed_grid_id,
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
            "field": const.RESULT_TABLE_SCAN_ID_KEY,
            "hide": True,
        },
        *_common_column_defs,
    ],
    dashGridOptions={
        "rowSelection": "multiple",
        "rowMultiSelectWithClick": True,
        "isRowSelectable": {
            "function": f"!!params.data.{const.SUMMARY_PII_ENTITY_KEY}"
        },
    },
    rowStyle={"backgroundColor": "white"},
    className="ag-theme-alpine",
    getRowId=f"params.data.{const.SUMMARY_COLUMN_NAME_KEY} + params.data.{const.SUMMARY_PII_ENTITY_KEY}",
    style={"height": "32rem", "width": "100%"},
)
