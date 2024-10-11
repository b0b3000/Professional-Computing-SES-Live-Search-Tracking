"""
Python program for retrieving keys/passwords from Azure key vault.
Also has utility function for retrieving from manually created local key txt files.

Use the first 2 functions for local testing, as you wont be able to access Azure keyvault if not a running instance of the web app
Otherwise, leave that section commented out

Written by Bob Beashel

"""

KEY_FILEPATH = "keys.txt"
from azure.identity import DefaultAzureCredential
from azure.keyvault.secrets import SecretClient
VAULT_NAME = "cits32004keys"
ACCOUNT_NAME = "cits3200testv1"



def get_blob_storage_key():

    # Retrieves key1 from the text file in this directory.
    # Sets connection string, where AccountName is the name of the Storage Account, and AccountKey is a valid Access Key to that account.
    conn_string = f"DefaultEndpointsProtocol=https;AccountName={ACCOUNT_NAME};AccountKey=;EndpointSuffix=core.windows.net"
    with open(KEY_FILEPATH) as file:
        for line in file:
            if line.rstrip().startswith("key1:"):
                # Splits the key from after the first occurence of "key1:".
                key = line.rstrip().split("key1:", 1)[1]
                # Places the key in the correct position in the middle of connection string.
                return conn_string[:69] + key + conn_string[69:]


def get_db_password():
    with open(KEY_FILEPATH) as file:
        for line in file:
            if line.rstrip().startswith("password:"):
                # Splits the key from after the first occurence of "password:".
                password = line.rstrip().split("password:", 1)[1]
                # Places the key in the correct position in the middle of connection string.
                return password
  
"""

def get_blob_storage_key():    

    secret_name = "BlobStorageConnectionString"
    vault_url = f"https://{VAULT_NAME}.vault.azure.net/"
    conn_string = f"DefaultEndpointsProtocol=https;AccountName={ACCOUNT_NAME};AccountKey=;EndpointSuffix=core.windows.net"
    
    # Create a SecretClient using DefaultAzureCredential.
    credential = DefaultAzureCredential()
    client = SecretClient(vault_url=vault_url, credential=credential)
    
    # Retrieve the secret from the Key Vault
    retrieved_secret = client.get_secret(secret_name)
    key = retrieved_secret.value.rstrip()
    
    #Format correctly
    return conn_string[:69] + key + conn_string[69:]


def get_db_password():
    secret_name = "historicalDatabasePassword"
    vault_url = f"https://{VAULT_NAME}.vault.azure.net/"
    
    # Create a SecretClient using DefaultAzureCredential
    credential = DefaultAzureCredential()
    client = SecretClient(vault_url=vault_url, credential=credential)
    
    # Retrieve the secret from the Key Vault
    retrieved_secret = client.get_secret(secret_name)
    password = retrieved_secret.value.rstrip()
    
    return password
"""