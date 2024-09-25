#IMPORTANT:
#USE THE FIRST FUNCTION FOR LOCAL TESTING
#USE THE SECOND FUNCTION FOR AZURE WEB APP
# I have not yet figured out a way to access key vaults when testing locally - WORKING ON IT


def get_blob_storage_key():
    # Retrieves key1 from the text file in this directory.
    # Sets connection string, where AccountName is the name of the Storage Account, and AccountKey is a valid Access Key to that account.
    conn_string = "DefaultEndpointsProtocol=https;AccountName=cits3200testv1;AccountKey=;EndpointSuffix=core.windows.net"
    with open("keys.txt") as file:
        for line in file:
            if line.rstrip().startswith("key1:"):
                # Splits the key from after the first occurence of "key1:".
                key = line.rstrip().split("key1:", 1)[1]
                # Places the key in the correct position in the middle of connection string.
                return conn_string[:69] + key + conn_string[69:]
            
def get_db_password():
    return "meshtastic2024!"
'''
from azure.identity import DefaultAzureCredential
from azure.keyvault.secrets import SecretClient

def get_blob_storage_key():    

    VAULT_NAME = "cits32004keys"
    SECRET_NAME = "BlobStorageConnectionString"
    vault_url = f"https://{VAULT_NAME}.vault.azure.net/"
    conn_string = "DefaultEndpointsProtocol=https;AccountName=cits3200testv1;AccountKey=;EndpointSuffix=core.windows.net"

    # Create a SecretClient using DefaultAzureCredential
    credential = DefaultAzureCredential()
    client = SecretClient(vault_url=vault_url, credential=credential)

    # Retrieve the secret from the Key Vault
    retrieved_secret = client.get_secret(SECRET_NAME)
    key = retrieved_secret.value.rstrip()

    #Format correctly
    return conn_string[:69] + key + conn_string[69:]

def get_db_password():
    VAULT_NAME = "cits32004keys"
    SECRET_NAME = "historicalDatabasePassword"
    vault_url = f"https://{VAULT_NAME}.vault.azure.net/"

    # Create a SecretClient using DefaultAzureCredential
    credential = DefaultAzureCredential()
    client = SecretClient(vault_url=vault_url, credential=credential)

    # Retrieve the secret from the Key Vault
    retrieved_secret = client.get_secret(SECRET_NAME)
    password = retrieved_secret.value.rstrip()

    print("Password: ", password, ", should be meshtastic2024!")
    return password
'''