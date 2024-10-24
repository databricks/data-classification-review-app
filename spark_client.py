import pandas as pd
from delta.tables import DeltaTable
from pyspark.sql import functions
import time
from databricks.connect import DatabricksSession

class SparkClient:
    def __init__(self, logger):
        self._logger = logger
    
    @property
    def _spark(self):
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
            (functions.col('schema_name') == schema) & (functions.col('table_name') == table)
        )
        
        # We should have one row per (schema, table, column name, pii entity)
        grouping_columns = ['schema_name', 'table_name', 'column_name', 'pii_entity']
        
        # Create a helper column for sorting
        df_processed = df_filtered.withColumn(
            'review_status_not_null',
            functions.when(functions.col('review_status').isNotNull(), 1).otherwise(0)
        )
        
        # Create a struct of the fields we need to retain
        df_processed = df_processed.withColumn(
            'data_struct',
            functions.struct(
                functions.col('review_status_not_null'),
                functions.col('scan_id'),
                functions.col('review_status'),
                functions.col('rationales'),
                functions.col('samples')
            )
        )
        
        # Use max_by to get the row with the highest priority per group
        # Priority is defined by review_status_not_null and timestamp
        df_deduped = df_processed.groupBy(*grouping_columns).agg(
            functions.max_by('data_struct', functions.struct(functions.col('review_status_not_null'), functions.col('timestamp'))).alias('max_struct')
        )
        
        # Extract the fields from the struct
        df_deduped = df_deduped.select(
            *grouping_columns,
            functions.col('max_struct.scan_id').alias('scan_id'),
            functions.col('max_struct.review_status').alias('review_status'),
            functions.col('max_struct.rationales')alias('rationales'),
            functions.col('max_struct.samples').alias('samples')
        )
        
        # Split into two DataFrames based on review_status being null
        df_to_review = df_deduped.filter(functions.col('review_status').isNull())
        df_reviewed = df_deduped.filter(functions.col('review_status').isNotNull())

        elapsed_time = time.time() - start_time
        self._logger.info(f"Get datasets took {elapsed_time:.2f} seconds")

        return df_to_review.toPandas(), df_reviewed.toPandas()

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
            }]
        :param review_status: The review status to set
        """
        start_time = time.time()

        table_name = self._get_result_table_name(source_table_name)
        # Read the main DataFrame
        delta_table = DeltaTable.forName(self._spark, table_name)

        # Prepare the updates DataFrame
        updates_df = self._spark.createDataFrame(updates_list)
        updates_df = updates_df.withColumn('review_status', functions.lit(review_status))

        # Define merge condition
        merge_condition = """
        target.schema_name = source.schema_name AND
        target.table_name = source.table_name AND
        target.column_name = source.column_name AND
        target.pii_entity = source.pii_entity
        """

        # Perform the merge
        delta_table.alias('target').merge(
            updates_df.alias('source'),
            merge_condition
        ).whenMatchedUpdate(
            set={"review_status": "source.review_status"}
        ).execute()

        end_time = time.time()
        elapsed_time = end_time - start_time
        self._logger.info(f"Update review status took {elapsed_time} seconds")

    def _get_result_table_name(self, source_table_name: str) -> str:
        catalog, _, _ = source_table_name.split(".")
        return f"{catalog}._data_classification._result"