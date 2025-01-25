import os
import base64
import logging
from azure.storage.blob import BlobServiceClient
from azure.data.tables import TableServiceClient, TableEntity
from datetime import datetime, timezone
import azure.functions as func


# Initialize Blob Service Client
# Provide your Azure Blob Storage connection string here
blob_service_client = BlobServiceClient.from_connection_string(os.environ["AzureWebJobsStorage"])
# Or you can directly specify it like:
# blob_service_client = BlobServiceClient.from_connection_string("DefaultEndpointsProtocol=https;AccountName=mystorage12390;AccountKey=qgLgz4sxQNoL68vFiOErOugxPnenIUGZSsCoUrUS5spCn8t/cPWOUXz6cDW9PiP/b7gDqDw3f9MK+AStR/3s9A==;EndpointSuffix=core.windows.net")

# Initialize Table Service Client
# Provide your Azure Table Storage connection string here
table_service_client = TableServiceClient.from_connection_string(os.environ["AzureTableStorageConnectionString"])

# Or you can directly specify it like:
# table_service_client = TableServiceClient.from_connection_string("DefaultEndpointsProtocol=https;AccountName=mystorage12390;AccountKey=qgLgz4sxQNoL68vFiOErOugxPnenIUGZSsCoUrUS5spCn8t/cPWOUXz6cDW9PiP/b7gDqDw3f9MK+AStR/3s9A==;EndpointSuffix=core.windows.net")

# Define the Blob Container name (replace with your actual container name)
BLOB_CONTAINER_NAME = "$logs"  # e.g., "$logs" container

# Define the Table name (replace with your actual Table name)
TABLE_NAME = "mytable"  # e.g., "WADPerformanceCountersTable"

# Function triggered by Blob Storage event
def main(blob: func.InputStream):
    logging.info(f"Blob trigger function processed blob \n"
                 f"Name: {blob.name}\n"
                 f"Blob Size: {blob.length} bytes")

    # Read the content of the blob
    try:
        content = blob.read()  # Read the content of the blob
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
        table_client = table_service_client.get_table_client(TABLE_NAME)
        table_client.upsert_entity(log_entity)
        logging.info(f"Stored log from blob {blob.name} in Table Storage")

    except Exception as e:
        logging.error(f"Error storing log in Table Storage: {e}")
