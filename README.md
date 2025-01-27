# Azure Blob Trigger with Table Storage Logging

This project demonstrates an Azure Function that is triggered by a Blob Storage event, processes the blob content, and stores the relevant data in an Azure Table Storage. The function reads blob content, decodes it if possible, and stores the processed information in a table for logging or further analysis.

## Prerequisites

Before running this project, ensure you have the following:

- An **Azure account** and **Azure subscription**.
- **Azure Storage account** with Blob and Table services enabled.
- **Python 3.x** installed.
- **Azure Functions Core Tools** installed for local development and testing (optional).
- **Azure CLI** installed (optional for deployment).
- Set up the **AzureWebJobsStorage** and **AzureTableStorageConnectionString** environment variables with appropriate connection strings.

## Setup

1. Clone this repository to your local machine:

   git clone https://github.com/yourusername/azure-blob-function.git
   cd azure-blob-function
   
# Create a virtual environment and activate it:

python -m venv venv
source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
# Install the required dependencies:
pip install -r requirements.txt

# Set up environment variables for your Azure Storage connection strings:

AzureWebJobsStorage: The connection string for your Azure Blob Storage.
AzureTableStorageConnectionString: The connection string for your Azure Table Storage.
You can set these in your local environment or in a .env file.

# Function Workflow
The function works as follows:

1. The function is triggered by a new blob being uploaded to the specified Blob Storage container ($logs).
2. The content of the blob is read and processed:
   If the content is valid UTF-8, it's stored as plain text.
   If the content is not valid UTF-8, it's encoded in base64 and stored.
3. A log entry is created and inserted into an Azure Table Storage table (mytable), where:
   PartitionKey is set as "myvm".
   RowKey is set as the current timestamp.
   The blob name and content are also stored.
# Function Configuration
Blob Storage Container: $logs
Table Storage Table: mytable

# Dependencies
azure-storage-blob: To interact with Azure Blob Storage.
azure-data-tables: To interact with Azure Table Storage.
azure-functions: To define the Azure Function app.
# Key Functions
process_blob_content(blob): This function reads and processes the content of a blob. It attempts to decode the content as UTF-8. If decoding fails, it base64 encodes the content.

create_log_entity(blob, content_text): Creates an entity to be inserted into the Azure Table Storage with the blob's metadata and processed content.

blob_trigger(blob: func.InputStream): This is the function triggered by the blob upload. It processes the blob content and stores a corresponding log in Table Storage.

# Running the Function Locally
1. To test the function locally, use the Azure Functions Core Tools:
func start
2. Upload a blob to the $logs container in your Blob Storage account, and the function will automatically be triggered.

# Deployment to Azure
To deploy the function to Azure, follow these steps:
Ensure you have the Azure Functions extension installed in VS Code, or use the Azure CLI.
Run the following command to deploy your function:
func azure functionapp publish function_app

# Troubleshooting
Ensure the Blob Storage and Table Storage connection strings are correctly set.
Check the function logs for any errors related to blob processing or table storage insertion.
# License
