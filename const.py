# These constants are used to reference the results table.
# They MUST be the same as the constants defined in data-classification client

RESULT_SCHEMA_NAME = "_data_classification"
RESULT_TABLE_NAME = "_result"

RESULT_TABLE_TIMESTAMP_KEY = "timestamp"
RESULT_TABLE_SCAN_ID_KEY = "scan_id"
RESULT_TABLE_SCHEMA_NAME_KEY = "schema_name"
RESULT_TABLE_TABLE_NAME_KEY = "table_name"
RESULT_TABLE_REVIEW_STATUS_KEY = "review_status"
SUMMARY_COLUMN_NAME_KEY = "column_name"
SUMMARY_PII_ENTITY_KEY = "pii_entity"
SUMMARY_SAMPLES_KEY = "samples"
SUMMARY_RATIONALES_KEY = "rationales"

# This must be the same as `SensitiveDataClass` defined in data classification service proto
SENSITIVE_DATA_CLASS_MAP = {
    "sensitive_data_class_unspecified": 0,
    "credit_card": 1,
    "crypto": 2,
    "email_address": 3,
    "iban_code": 4,
    "ip_address": 5,
    "location": 6,
    "person": 7,
    "phone_number": 8,
    "medical_license": 9,
    "us_bank_number": 10,
    "us_driver_license": 11,
    "us_itin": 12,
    "us_passport": 13,
    "us_ssn": 14,
}
