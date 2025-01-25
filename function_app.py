# import azure.functions as func
# import logging

# app = func.FunctionApp()

# @app.blob_trigger(arg_name="blob", path ="logs/{name}",
#                                connection="AzureWebJobsStorage") 
# def blob_trigger(blob: func.InputStream):
#     logging.info(f"Python blob trigger function processed blob"
#                 f"Name: {blob.name}"
#                 f"Blob Size: {blob.length} bytes")


import azure.functions as func
import logging
import base64
from datetime import datetime, timezone
from azure.data.tables import TableServiceClient, TableEntity
import os

# Initialize the Table Service Client for Table Storage

# You can fetch the connection string from environment variables for better security
TABLE_STORAGE_CONNECTION_STRING = os.getenv("AzureTableStorageConnectionString")
TABLE_NAME = "mytable"  # Specify your table name

# Initialize the Function App and blob trigger
app = func.FunctionApp()

@app.blob_trigger(arg_name="blob", path="$logs/{name}", connection="AzureWebJobsStorage")
def blob_trigger(blob: func.InputStream):
    logging.info(f"Python blob trigger function processed blob\n"
                 f"Name: {blob.name}\n"
                 f"Blob Size: {blob.length} bytes")

    # Read the content of the blob
    try:
        content = blob.read()  # Read the blob content
        logging.info(f"Blob content (first 100 chars): {content[:100]}...")

        # Try to decode the content as UTF-8
        content_text = content.decode("utf-8")
    except UnicodeDecodeError:
        # If UTF-8 decoding fails, encode the content to base64
        content_text = base64.b64encode(content).decode("utf-8")
        logging.warning(f"Blob content is not valid UTF-8, storing as base64: {content[:100]}...")

    # Create an entity to store in Table Storage
    log_entity = TableEntity()
    log_entity["PartitionKey"] = "myvm"  # PartitionKey, could be based on VM or blob type
    log_entity["RowKey"] = str(datetime.now(timezone.utc))  # Use timestamp as RowKey for uniqueness
    log_entity["BlobName"] = blob.name  # Store blob name
    log_entity["Content"] = content_text  # Store the content as text or base64-encoded string

    # Insert or update the entity in Table Storage
    try:
        table_service_client = TableServiceClient.from_connection_string(TABLE_STORAGE_CONNECTION_STRING)
        table_client = table_service_client.get_table_client(TABLE_NAME)
        table_client.upsert_entity(log_entity)
        logging.info(f"Stored log from blob {blob.name} in Table Storage")

    except Exception as e:
        logging.error(f"Error storing log in Table Storage: {e}")

