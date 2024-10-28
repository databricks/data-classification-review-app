import dash
import dash_bootstrap_components as dbc
from components import intervals, tabs, notification, actions

layout = dbc.Container(
    [
        intervals.initial_refresh_interval,
        intervals.long_refresh_interval,
        notification.error_notification,
        dbc.Stack(
            [
                dash.html.H2("Data classification"),
                dash.html.Div(
                    children=[
                        dbc.FormText(
                            "Full source table name (e.g. catalog.schema.table)",
                            class_name="mb-4",
                        ),
                        actions.search,
                    ]
                ),
                notification.content_spinner,
                dash.html.Div(
                    tabs.tabs,
                    id=tabs.tabs_id,
                    style={"visibility": "hidden"},
                ),
            ],
            gap=3,
        ),
    ],
    className="page-container",
    fluid=True,
)
