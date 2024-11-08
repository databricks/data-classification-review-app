from clients.spark_client import SparkClient
from clients.databricks_client import DatabricksClient


def register_callbacks(
    app, spark_client: SparkClient, databricks_client: DatabricksClient
):
    from collections import defaultdict
    import const
    import dash
    import dash_bootstrap_components as dbc
    from components import intervals, grid, tabs, notification, actions, store
    from utils import error_utils

    @dash.callback(
        dash.Input(intervals.initial_refresh_interval_id, "n_intervals"),
    )
    def refresh_cluster_initial(n_intervals):
        try:
            spark_client.refresh_cluster("initial-" + str(n_intervals))
        except Exception as e:
            app.logger.info(str(e))

    @dash.callback(
        dash.Input(intervals.long_refresh_interval_id, "n_intervals"),
    )
    def refresh_cluster_long(n_intervals):
        try:
            spark_client.refresh_cluster("long-" + str(n_intervals))
        except Exception as e:
            app.logger.info(str(e))

    @dash.callback(
        dash.Output(grid.unreviewed_grid_id, "rowData"),
        dash.Output(tabs.to_review_tab_header_id, "children"),
        dash.Output(grid.reviewed_grid_id, "rowData", allow_duplicate=True),
        dash.Output(tabs.reviewed_tab_header_id, "children", allow_duplicate=True),
        dash.Output(notification.error_notificaton_id, "is_open"),
        dash.Output(notification.error_notificaton_id, "children"),
        dash.Input(actions.search_id, "n_submit"),
        dash.State(actions.search_id, "value"),
        prevent_initial_call=True,
        running=[
            (
                dash.Output(notification.content_spinner_id, "spinner_style"),
                {"display": "block"},
                {"display": "none"},
            ),
            (
                dash.Output(tabs.tabs_id, "style"),
                {"visibility": "hidden"},
                {"visibility": "visible"},
            ),
        ],
    )
    def input_submit(n_submit, value):
        if value:
            try:
                updated_data = spark_client.get_datasets(value)
                unreviewed_data = updated_data[0].to_dict("records")
                reviewed_data = updated_data[1].to_dict("records")
                return (
                    unreviewed_data,
                    f"{str(len(unreviewed_data))} Classifications to review",
                    reviewed_data,
                    f"{str(len(reviewed_data))} Classifications reviewed",
                    False,
                    "",
                )
            except Exception as e:
                err = error_utils.reformat_error(e)
                return (
                    [],
                    "0 Classifications to review",
                    [],
                    "0 Classifications reviewed",
                    True,
                    dash.html.P(err, className="error-toast-content"),
                )

    def update_review_status_and_return(value, status, selected_rows, token_data):
        token_data = token_data or {}
        _, schema, table = value.split(".")
        try:
            update_review_status_list = []
            apply_review_results_list = []
            for row in selected_rows:
                update_review_status_list.append(
                    {
                        const.RESULT_TABLE_SCHEMA_NAME_KEY: schema,
                        const.RESULT_TABLE_TABLE_NAME_KEY: table,
                        const.SUMMARY_COLUMN_NAME_KEY: row[
                            const.SUMMARY_COLUMN_NAME_KEY
                        ],
                        const.SUMMARY_PII_ENTITY_KEY: row[const.SUMMARY_PII_ENTITY_KEY],
                        const.RESULT_TABLE_SCAN_ID_KEY: row[
                            const.RESULT_TABLE_SCAN_ID_KEY
                        ],
                    }
                )
                apply_review_results_list.append(
                    {
                        "column_name": row[const.SUMMARY_COLUMN_NAME_KEY],
                        "data_class": const.SENSITIVE_DATA_CLASS_MAP.get(
                            row[const.SUMMARY_PII_ENTITY_KEY], 0
                        ),
                    }
                )

            if status == "applied_tag":
                accepted_classifications = apply_review_results_list
                rejected_classifications = None
            else:
                accepted_classifications = None
                rejected_classifications = apply_review_results_list

            _, latest_token, latest_token_expiration = (
                databricks_client.apply_review_results(
                    value,
                    accepted_classifications,
                    rejected_classifications,
                    token_data.get("token"),
                    token_data.get("token_expiration"),
                )
            )

            spark_client.update_review_status(value, update_review_status_list, status)
            updated_data = spark_client.get_datasets(value)
            unreviewed_data = updated_data[0].to_dict("records")
            reviewed_data = updated_data[1].to_dict("records")
            return (
                unreviewed_data,
                f"{str(len(unreviewed_data))} Classifications to review",
                reviewed_data,
                f"{str(len(reviewed_data))} Classifications reviewed",
                False,
                "",
                {"token": latest_token, "token_expiration": latest_token_expiration},
            )
        except Exception as e:
            err = error_utils.reformat_error(e)
            return (
                dash.no_update,
                dash.no_update,
                dash.no_update,
                dash.no_update,
                True,
                dash.html.P(err, className="error-toast-content"),
                dash.no_update,
            )

    dash.clientside_callback(
        """
      function(selectedRows) {
          if (!!selectedRows && selectedRows.length > 0) {
              return [`Apply classification tags (${selectedRows.length})`, false,`Reject (${selectedRows.length})`, false]
          }
          return ["Apply classification tags", true, "Reject", true]
      }
      """,
        dash.Output(actions.apply_action_id, "children"),
        dash.Output(actions.apply_action_id, "disabled"),
        dash.Output(actions.reject_action_id, "children"),
        dash.Output(actions.reject_action_id, "disabled"),
        dash.Input(grid.unreviewed_grid_id, "selectedRows"),
        prevent_initial_call=True,
    )

    @dash.callback(
        dash.Output(grid.unreviewed_grid_id, "rowData", allow_duplicate=True),
        dash.Output(tabs.to_review_tab_header_id, "children", allow_duplicate=True),
        dash.Output(grid.reviewed_grid_id, "rowData", allow_duplicate=True),
        dash.Output(tabs.reviewed_tab_header_id, "children", allow_duplicate=True),
        dash.Output(notification.error_notificaton_id, "is_open", allow_duplicate=True),
        dash.Output(
            notification.error_notificaton_id, "children", allow_duplicate=True
        ),
        dash.Output(store.token_store_id, "data", allow_duplicate=True),
        dash.Input(actions.apply_action_id, "n_clicks"),
        dash.State(grid.unreviewed_grid_id, "selectedRows"),
        dash.State(actions.search_id, "value"),
        dash.State(store.token_store_id, "data"),
        prevent_initial_call=True,
        running=[
            (dash.Output(actions.apply_action_id, "disabled"), True, False),
            (dash.Output(actions.reject_action_id, "disabled"), True, False),
            (
                dash.Output(actions.apply_action_id, "children"),
                [dbc.Spinner(size="sm", spinner_class_name="me-2"), "Applying tags..."],
                ["Apply classification tags"],
            ),
        ],
    )
    def apply_tags(n_clicks, selected_rows, value, data):
        if n_clicks > 0 and len(selected_rows) > 0:
            return update_review_status_and_return(
                value, "applied_tag", selected_rows, data
            )

    @dash.callback(
        dash.Output(grid.unreviewed_grid_id, "rowData", allow_duplicate=True),
        dash.Output(tabs.to_review_tab_header_id, "children", allow_duplicate=True),
        dash.Output(grid.reviewed_grid_id, "rowData", allow_duplicate=True),
        dash.Output(tabs.reviewed_tab_header_id, "children", allow_duplicate=True),
        dash.Output(notification.error_notificaton_id, "is_open", allow_duplicate=True),
        dash.Output(
            notification.error_notificaton_id, "children", allow_duplicate=True
        ),
        dash.Output(store.token_store_id, "data", allow_duplicate=True),
        dash.Input(actions.reject_action_id, "n_clicks"),
        dash.State(grid.unreviewed_grid_id, "selectedRows"),
        dash.State(actions.search_id, "value"),
        dash.State(store.token_store_id, "data"),
        prevent_initial_call=True,
        running=[
            (dash.Output(actions.apply_action_id, "disabled"), True, False),
            (dash.Output(actions.reject_action_id, "disabled"), True, False),
            (
                dash.Output(actions.reject_action_id, "children"),
                [dbc.Spinner(size="sm", spinner_class_name="me-2"), "Rejecting..."],
                ["Reject"],
            ),
        ],
    )
    def reject(n_clicks, selected_rows, value, data):
        if n_clicks > 0 and len(selected_rows) > 0:
            return update_review_status_and_return(
                value, "rejected", selected_rows, data
            )
