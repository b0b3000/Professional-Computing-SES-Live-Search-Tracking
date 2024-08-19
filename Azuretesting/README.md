## Azure Storage Documentation

### How to Run
- You do not need to create an Azure account for this (hopefully)
- Just download Azure Storage Explorer: https://azure.microsoft.com/en-au/products/storage/storage-explorer
- Using Azure Storage Explorer:
    - Click the connection symbol on the sidebar
    - Select "Storage account or service"
    - Select "Connection string (Key or SAS)"
    - Under "Display name", write "cits3200testv1"
    - For the "Connection string", use this:
    ```
    BlobEndpoint=https://cits3200testv1.blob.core.windows.net/;QueueEndpoint=https://cits3200testv1.queue.core.windows.net/;FileEndpoint=https://cits3200testv1.file.core.windows.net/;TableEndpoint=https://cits3200testv1.table.core.windows.net/;SharedAccessSignature=sv=2022-11-02&ss=bfqt&srt=sco&sp=rwdlacupiytfx&se=2024-12-30T17:14:56Z&st=2024-08-19T09:14:56Z&spr=https,http&sig=lGJZq7yRcnHGFqGR2V7mzTtIfAfKS6CkwvEupdnj0HA%3D
    ```
    - Then click "Next", then click "Connect"
    - The Storage Account should now show up in the sidebar, and you can navigate down to certain containers and blobs

- Running "retrieve_from_container.py" will read all containers and blobs in storage, create a TimestampedGeoJson object from each of them, then save it onto the Folium map under "footprint.html"
- Open "footprint.html" in a browser

### An explanation of some of the Azure storage concepts:
- A Storage Account is a space on an Azure account that stores Containers
- A Container is essentially a directory that stores Blobs
- A Blob is a single file in a container
