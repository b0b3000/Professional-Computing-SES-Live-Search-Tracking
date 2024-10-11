"""Functions that fetch the Azure storage account key and the Azure database password.

----- IMPORTANT -----
- Use the first two functions in this file when locally testing the web application.
- Use the next two functions in this file when hosting the web application on Azure.
"""

# First two functions for testing locally:

def get_blob_storage_key():
    """Fetches Azure storage account key from a text file in this directory.
    
    Fetches the key, then sets a connection string, where 'AccountName' is the name of the storage account, and 'AccountKey' 
    is a valid access key to that account.

    Returns:
        string (str): Connection string for the storage account.
    """

    conn_string = "DefaultEndpointsProtocol=https;AccountName=cits3200testv1;AccountKey=;EndpointSuffix=core.windows.net"#
    with open("keys.txt") as file:
        for line in file:
            if line.rstrip().startswith("key1:"):
                key = line.rstrip().split("key1:", 1)[1]
                return conn_string[:69] + key + conn_string[69:]


def get_db_password():
    """Returns a static Azure database password."""
    return "meshtastic2024!"

# Next two functions for hosting web application on Azure (use 'ctrl + /' to uncomment block):

# from azure.identity import DefaultAzureCredential
# from azure.keyvault.secrets import SecretClient


# def get_blob_storage_key():    
#     """Fetches the Azure storage connection string from a key vault.
    
#     Fetches the key from a key vault, then sets a connection string, where 'AccountName' is the name of the storage account, 
#     and 'AccountKey' is a valid access key to that account.

#     Returns:
#         string (str): Connection string for the storage account.
#     """

#     VAULT_NAME = "cits32004keys"
#     SECRET_NAME = "BlobStorageConnectionString"
#     vault_url = f"https://{VAULT_NAME}.vault.azure.net/"
#     conn_string = "DefaultEndpointsProtocol=https;AccountName=cits3200testv1;AccountKey=;EndpointSuffix=core.windows.net"

#     credential = DefaultAzureCredential()    # Creates a SecretClient using DefaultAzureCredential.
#     client = SecretClient(vault_url=vault_url, credential=credential)
    
#     retrieved_secret = client.get_secret(SECRET_NAME)    # Retrieves the secret from the Key Vault.
#     key = retrieved_secret.value.rstrip()
    
#     return conn_string[:69] + key + conn_string[69:]


# def get_db_password():
#     """Fetches the Azure database password from a key vault.
    
#     Returns:
#         string (str): Azure database password.
#     """

#     VAULT_NAME = "cits32004keys"
#     SECRET_NAME = "historicalDatabasePassword"
#     vault_url = f"https://{VAULT_NAME}.vault.azure.net/"
    
#     credential = DefaultAzureCredential()    # Creates a SecretClient using DefaultAzureCredential.
#     client = SecretClient(vault_url=vault_url, credential=credential)
    
#     retrieved_secret = client.get_secret(SECRET_NAME)    # Retrieve the secret from the Key Vault
#     password = retrieved_secret.value.rstrip()
    
#     return password
