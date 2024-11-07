from clients.spark_client import SparkClient

def register_callbacks(app, spark_client: SparkClient):
  from collections import defaultdict
  import const
  import dash
  import dash_bootstrap_components as dbc
  from components import intervals, grid, tabs, notification, actions
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


  def update_review_status_and_return(value, status, selected_rows):
      _, schema, table = value.split(".")
      updates_list = [
          {
              const.RESULT_TABLE_SCHEMA_NAME_KEY: schema,
              const.RESULT_TABLE_TABLE_NAME_KEY: table,
              const.SUMMARY_COLUMN_NAME_KEY: row[const.SUMMARY_COLUMN_NAME_KEY],
              const.SUMMARY_PII_ENTITY_KEY: row[const.SUMMARY_PII_ENTITY_KEY],
              const.RESULT_TABLE_SCAN_ID_KEY: row[const.RESULT_TABLE_SCAN_ID_KEY],
          }
          for row in selected_rows
      ]
      try:
          if (status == "applied_tag"):
            updates_dict = defaultdict(list)
            for row in selected_rows:
                updates_dict[row[const.SUMMARY_COLUMN_NAME_KEY]].append(row[const.SUMMARY_PII_ENTITY_KEY])
            # TODO: Replace this with a service call once the service endpoint is ready
            spark_client.apply_tags(value, updates_dict)

          spark_client.update_review_status(value, updates_list, status)
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
              dash.no_update,
              dash.no_update,
              dash.no_update,
              dash.no_update,
              True,
              dash.html.P(err, className="error-toast-content"),
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
      dash.Output(notification.error_notificaton_id, "children", allow_duplicate=True),
      dash.Input(actions.apply_action_id, "n_clicks"),
      dash.State(grid.unreviewed_grid_id, "selectedRows"),
      dash.State(actions.search_id, "value"),
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
  def apply_tags(n_clicks, selected_rows, value):
      if n_clicks > 0 and len(selected_rows) > 0:
          return update_review_status_and_return(value, "applied_tag", selected_rows)


  @dash.callback(
      dash.Output(grid.unreviewed_grid_id, "rowData", allow_duplicate=True),
      dash.Output(tabs.to_review_tab_header_id, "children", allow_duplicate=True),
      dash.Output(grid.reviewed_grid_id, "rowData", allow_duplicate=True),
      dash.Output(tabs.reviewed_tab_header_id, "children", allow_duplicate=True),
      dash.Output(notification.error_notificaton_id, "is_open", allow_duplicate=True),
      dash.Output(notification.error_notificaton_id, "children", allow_duplicate=True),
      dash.Input(actions.reject_action_id, "n_clicks"),
      dash.State(grid.unreviewed_grid_id, "selectedRows"),
      dash.State(actions.search_id, "value"),
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
  def reject(n_clicks, selected_rows, value):
      if n_clicks > 0 and len(selected_rows) > 0:
          return update_review_status_and_return(value, "rejected", selected_rows)
