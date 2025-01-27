import os
import base64
import logging
from azure.storage.blob import BlobServiceClient
from azure.data.tables import TableServiceClient, TableEntity
from datetime import datetime, timezone
import azure.functions as func

# Initialize Blob Service Client
blob_service_client = BlobServiceClient.from_connection_string(os.getenv("AzureWebJobsStorage"))
# Initialize Table Service Client
table_service_client = TableServiceClient.from_connection_string(os.getenv("AzureTableStorageConnectionString"))

# Constants for Table and Blob Container
BLOB_CONTAINER_NAME = "$logs"
TABLE_NAME = "mytable"

# Helper function to handle blob content and decode it
def process_blob_content(blob):
    content = blob.read()
    logging.info(f"Blob content (first 100 chars): {content[:100]}...")

    # Try to decode the content as UTF-8
    try:
        return content.decode("utf-8")
    except UnicodeDecodeError:
        # If UTF-8 decoding fails, base64 encode it
        base64_content = base64.b64encode(content).decode("utf-8")
        logging.warning(f"Blob content is not valid UTF-8, storing as base64.")
        return base64_content
    except Exception as e:
        # Catch any other unexpected errors and log them
        logging.error(f"Error processing blob content: {e}")
        return None  # Return None if there’s an error (you can handle this later)

# Helper function to create a Table Entity
def create_log_entity(blob, content_text):
    log_entity = TableEntity()
    log_entity["PartitionKey"] = "myvm"  # PartitionKey, could be based on VM or blob type
    log_entity["RowKey"] = str(datetime.now(timezone.utc))  # Use timestamp as RowKey for uniqueness
    log_entity["BlobName"] = blob.name  # Store blob name
    log_entity["Content"] = content_text  # Store the content as text or base64-encoded string
    return log_entity

# Azure Functions app
app = func.FunctionApp()

# Function triggered by Blob Storage event
@app.blob_trigger(arg_name="blob", path="$logs/{name}", connection="AzureWebJobsStorage")
def blob_trigger(blob: func.InputStream):
    logging.info(f"Blob trigger function processed blob \n"
                 f"Name: {blob.name}\n"
                 f"Blob Size: {blob.length} bytes")

    # Process blob content
    content_text = process_blob_content(blob)

    # Create log entity to store in Table Storage
    log_entity = create_log_entity(blob, content_text)

    # Insert or update the entity in Table Storage
    try:
        table_client = table_service_client.get_table_client(TABLE_NAME)
        table_client.upsert_entity(log_entity)
        logging.info(f"Stored log from blob {blob.name} in Table Storage")
    except Exception as e:
        logging.error(f"Error storing log in Table Storage: {e}")