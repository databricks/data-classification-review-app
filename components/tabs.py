import dash
import dash_bootstrap_components as dbc
from components import grid, actions

reviewed_tab_id = "reviewed-tab"
reviewed_tab_header_id = "reviewed-header"
reviewed_tab_content = dbc.Stack(
    [
        dash.html.H4(
            f"0 Classifications reviewed", className="mt-3", id=reviewed_tab_header_id
        ),
        dbc.Row(
            dbc.Col(
                grid.reviewed_grid,
                width=12,
            )
        ),
    ],
    gap=3,
)

to_review_tab_id = "to-review-tab"
to_review_tab_header_id = "unreviewed-header"
to_review_tab_content = dbc.Stack(
    [
        dash.html.H4(
            f"0 Classifications to review", className="mt-3", id=to_review_tab_header_id
        ),
        dbc.Row(
            dbc.Col(
                grid.unreviewed_grid,
                width=12,
            )
        ),
        dbc.Row(
            [
                dbc.Col(
                    actions.apply_action,
                    width="4",
                ),
                dbc.Col(
                    actions.reject_action,
                    width="4",
                ),
            ],
        ),
    ],
    gap=3,
)

tabs_id = "tab-container"
tabs = (
    dbc.Tabs(
        [
            dbc.Tab(
                to_review_tab_content,
                tab_id=to_review_tab_id,
                label="To review",
            ),
            dbc.Tab(
                reviewed_tab_content,
                label="Reviewed",
                tab_id=reviewed_tab_id,
            ),
        ],
        active_tab=to_review_tab_id,
    ),
)
