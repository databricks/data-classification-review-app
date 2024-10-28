import dash_bootstrap_components as dbc

apply_action_id = "apply-tags-button"
apply_action = dbc.Button(
    "Apply classification tags",
    id=apply_action_id,
    n_clicks=0,
    color="primary",
    className="me-2",
    style={"width": "100%"},
)

reject_action_id = "reject-button"
reject_action = dbc.Button(
    "Reject",
    id=reject_action_id,
    n_clicks=0,
    color="secondary",
    style={"width": "100%"},
)

search_id = "source-table-input"
search = dbc.Input(id=search_id, value="")
