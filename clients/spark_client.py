import pandas as pd
from delta.tables import DeltaTable
from pyspark.sql import functions
import time
from databricks.connect import DatabricksSession
import const

class SparkClient:
    def __init__(self, logger):
        self._logger = logger
    
    @property
    def _spark(self):
        self._logger.info("Creating Databricks session")
        return DatabricksSession.builder.serverless(True).getOrCreate()
    
    def get_datasets(self, source_table_name: str) -> tuple[pd.DataFrame, pd.DataFrame]:
        """
        Returns two DataFrames for a given source table: 
        1. To Review Dataset (with review_status == NULL)
        2. Reviewed Dataset (with review_status not NULL)
        """
        start_time = time.time()

        catalog, schema, table = source_table_name.split(".")
  
        # Get the full result table DF
        table_name = self._get_result_table_name(source_table_name)
        df = self._spark.read.format("delta").table(table_name)

        # Filter data where schema_name and table_name equals the source_table_name
        df_filtered = df.filter(
            (functions.col(const.RESULT_TABLE_SCHEMA_NAME_KEY) == schema) & (functions.col(const.RESULT_TABLE_TABLE_NAME_KEY) == table)
        )
        
        # We should have one row per (schema, table, column name, pii entity)
        grouping_columns = [const.RESULT_TABLE_SCHEMA_NAME_KEY, const.RESULT_TABLE_TABLE_NAME_KEY, const.SUMMARY_COLUMN_NAME_KEY, const.SUMMARY_PII_ENTITY_KEY]
        
        # Create a helper column for sorting
        df_processed = df_filtered.withColumn(
            'review_status_not_null',
            functions.when(functions.col(const.RESULT_TABLE_REVIEW_STATUS_KEY).isNotNull(), 1).otherwise(0)
        )
        
        # Create a struct of the fields we need to retain
        df_processed = df_processed.withColumn(
            'data_struct',
            functions.struct(
                functions.col('review_status_not_null'),
                functions.col(const.RESULT_TABLE_REVIEW_STATUS_KEY),
                functions.col(const.SUMMARY_RATIONALES_KEY),
                functions.col(const.SUMMARY_SAMPLES_KEY)
            )
        )
        
        # Use max_by to get the row with the highest priority per group
        # Priority is defined by review_status_not_null and timestamp
        df_deduped = df_processed.groupBy(*grouping_columns).agg(
            functions.max_by('data_struct', functions.struct(functions.col('review_status_not_null'), functions.col(const.RESULT_TABLE_TIMESTAMP_KEY))).alias('max_struct')
        )
        
        # Extract the fields from the struct
        df_deduped = df_deduped.select(
            *grouping_columns,
            functions.col(f'max_struct.{const.RESULT_TABLE_REVIEW_STATUS_KEY}').alias(const.RESULT_TABLE_REVIEW_STATUS_KEY),
            functions.col(f'max_struct.{const.SUMMARY_RATIONALES_KEY}').alias(const.SUMMARY_RATIONALES_KEY),
            functions.col(f'max_struct.{const.SUMMARY_SAMPLES_KEY}').alias(const.SUMMARY_SAMPLES_KEY)
        )
        
        # Split into two DataFrames based on review_status being null
        df_to_review = df_deduped.filter(functions.col(const.RESULT_TABLE_REVIEW_STATUS_KEY).isNull()).toPandas()
        df_reviewed = df_deduped.filter(functions.col(const.RESULT_TABLE_REVIEW_STATUS_KEY).isNotNull()).toPandas()

        elapsed_time = time.time() - start_time
        self._logger.info(f"Get datasets took {elapsed_time:.2f} seconds")

        return df_to_review, df_reviewed

    def update_review_status(self, source_table_name, updates_list, review_status):
        """
        Updates the result table for a given source table with the provided updates list
        
        :param source_table_name: The source table name
        :param updates_list: List of dictionaries defining the updates. Format should be:
            [{
                'schema_name': schema,
                'table_name': table,
                'column_name': column,
                'pii_entity': email,
                'scan_id': scan_id
            }]
        :param review_status: The review status to set
        """
        start_time = time.time()

        table_name = self._get_result_table_name(source_table_name)
        # Read the main DataFrame
        delta_table = DeltaTable.forName(self._spark, table_name)

        # Prepare the updates DataFrame
        updates_df = self._spark.createDataFrame(updates_list)
        updates_df = updates_df.withColumn(const.RESULT_TABLE_REVIEW_STATUS_KEY, functions.lit(review_status))

        # Define merge condition
        merge_condition = f"""
        target.{const.RESULT_TABLE_SCAN_ID_KEY} = source.{const.RESULT_TABLE_SCAN_ID_KEY} AND
        target.{const.RESULT_TABLE_SCHEMA_NAME_KEY} = source.{const.RESULT_TABLE_SCHEMA_NAME_KEY} AND
        target.{const.RESULT_TABLE_TABLE_NAME_KEY} = source.{const.RESULT_TABLE_TABLE_NAME_KEY} AND
        target.{const.SUMMARY_COLUMN_NAME_KEY} = source.{const.SUMMARY_COLUMN_NAME_KEY} AND
        target.{const.SUMMARY_PII_ENTITY_KEY} = source.{const.SUMMARY_PII_ENTITY_KEY}
        """

        # Perform the merge
        delta_table.alias('target').merge(
            updates_df.alias('source'),
            merge_condition
        ).whenMatchedUpdate(
            set={const.RESULT_TABLE_REVIEW_STATUS_KEY: f"source.{const.RESULT_TABLE_REVIEW_STATUS_KEY}"}
        ).execute()

        end_time = time.time()
        elapsed_time = end_time - start_time
        self._logger.info(f"Update review status took {elapsed_time} seconds")

    def _get_result_table_name(self, source_table_name: str) -> str:
        catalog, _, _ = source_table_name.split(".")
        return f"{catalog}.{const.RESULT_SCHEMA_NAME}.{const.RESULT_TABLE_NAME}"