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

        (see Discord)

    - Then click "Next", then click "Connect"
    - The Storage Account should now show up in the sidebar, and you can navigate down to certain containers and blobs

- Running "retrieve_from_container.py" will read all containers and blobs in storage, create a TimestampedGeoJson object from each of them, then save it onto the Folium map under "footprint.html"
- Open "footprint.html" in a browser

### An explanation of some of the Azure storage concepts:
- A Storage Account is a space on an Azure account that stores Containers
- A Container is essentially a directory that stores Blobs
- A Blob is a single file in a container
