import dash_bootstrap_components as dbc

error_notificaton_id = "error-notification"
error_notification = dbc.Toast(
    "",
    header="Error",
    id=error_notificaton_id,
    class_name="error-toast",
    icon="danger",
    dismissable=True,
    is_open=False,
)

content_spinner_id = "content-spinner"
content_spinner = dbc.Spinner(
    id=content_spinner_id,
    color="primary",
    spinner_class_name="center-item",
    spinner_style={"display": "none"},
)
