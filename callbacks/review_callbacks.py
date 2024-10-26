from clients.spark_client import SparkClient
import const

def register_callbacks(app, spark_client: SparkClient):
  import dash
  import dash_bootstrap_components as dbc

  @dash.callback(
      dash.Output("unreviewed-data", "rowData"),
      dash.Output("unreviewed-header", "children"),
      dash.Output("reviewed-data", "rowData", allow_duplicate=True),
      dash.Output("reviewed-header", "children", allow_duplicate=True),
      dash.Output("error-notification", "is_open"),
      dash.Output("error-notification", "children"),
      dash.Input("source-table-input", "n_submit"),
      dash.State("source-table-input", "value"),
      prevent_initial_call=True,
      running=[
          (
              dash.Output("content-spinner", "spinner_style"),
              {"display": "block"},
              {"display": "none"},
          ),
          (
              dash.Output("tab-container", "style"),
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
            err = str(e)
            if ("session_id is no longer usable" in err):
              err = "Session expired. Please refresh the page."
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
              "schema_name": schema,
              "table_name": table,
              "column_name": row["column_name"],
              "pii_entity": row["pii_entity"],
              const.RESULT_TABLE_SCAN_ID_KEY: row[const.RESULT_TABLE_SCAN_ID_KEY],
          }
          for row in selected_rows
      ]
      try:
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
          err = str(e)
          if ("session_id is no longer usable" in err):
              err = "Session expired. Please refresh the page."
          return (
              [],
              "0 Classifications to review",
              [],
              "0 Classifications reviewed",
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
      dash.Output("apply-tags-button", "children"),
      dash.Output("apply-tags-button", "disabled"),
      dash.Output("reject-button", "children"),
      dash.Output("reject-button", "disabled"),
      dash.Input("unreviewed-data", "selectedRows"),
      prevent_initial_call=True,
  )


  @dash.callback(
      dash.Output("unreviewed-data", "rowData", allow_duplicate=True),
      dash.Output("unreviewed-header", "children", allow_duplicate=True),
      dash.Output("reviewed-data", "rowData", allow_duplicate=True),
      dash.Output("reviewed-header", "children", allow_duplicate=True),
      dash.Output("error-notification", "is_open", allow_duplicate=True),
      dash.Output("error-notification", "children", allow_duplicate=True),
      dash.Input("apply-tags-button", "n_clicks"),
      dash.State("unreviewed-data", "selectedRows"),
      dash.State("source-table-input", "value"),
      prevent_initial_call=True,
      running=[
          (dash.Output("apply-tags-button", "disabled"), True, False),
          (dash.Output("reject-button", "disabled"), True, False),
          (
              dash.Output("apply-tags-button", "children"),
              [dbc.Spinner(size="sm", spinner_class_name="me-2"), "Applying tags..."],
              ["Apply classification tags"],
          ),
      ],
  )
  def apply_tags(n_clicks, selected_rows, value):
      if n_clicks > 0 and len(selected_rows) > 0:
          return update_review_status_and_return(value, "apply_tag", selected_rows)


  @dash.callback(
      dash.Output("unreviewed-data", "rowData", allow_duplicate=True),
      dash.Output("unreviewed-header", "children", allow_duplicate=True),
      dash.Output("reviewed-data", "rowData", allow_duplicate=True),
      dash.Output("reviewed-header", "children", allow_duplicate=True),
      dash.Output("error-notification", "is_open", allow_duplicate=True),
      dash.Output("error-notification", "children", allow_duplicate=True),
      dash.Input("reject-button", "n_clicks"),
      dash.State("unreviewed-data", "selectedRows"),
      dash.State("source-table-input", "value"),
      prevent_initial_call=True,
      running=[
          (dash.Output("apply-tags-button", "disabled"), True, False),
          (dash.Output("reject-button", "disabled"), True, False),
          (
              dash.Output("reject-button", "children"),
              [dbc.Spinner(size="sm", spinner_class_name="me-2"), "Rejecting..."],
              ["Reject"],
          ),
      ],
  )
  def reject(n_clicks, selected_rows, value):
      if n_clicks > 0 and len(selected_rows) > 0:
          return update_review_status_and_return(value, "reject", selected_rows)
