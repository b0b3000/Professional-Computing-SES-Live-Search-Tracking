def get_key():
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