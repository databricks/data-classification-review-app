import dash
import dash_bootstrap_components as dbc
from clients.spark_client import SparkClient
from clients.databricks_client import DatabricksClient
from callbacks import review_callbacks
from pages import review


def create_app():
    app = dash.Dash(
        __name__,
        external_stylesheets=[dbc.themes.BOOTSTRAP],
        suppress_callback_exceptions=True,
    )

    app.title = "Data Classification"

    logger = app.logger

    spark_client = SparkClient(logger)

    databricks_client = DatabricksClient(logger)

    review_callbacks.register_callbacks(app, spark_client, databricks_client)

    app.layout = review.layout

    return app
