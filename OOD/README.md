# RichContextMetadata
Extracting metadata on publications, datasets and persons, and drawing relationships between these three entity types.

`pip install -r requirements.txt`
## Generating Metadata

### Accessing the Dimensions API
`import metadata_funs`
`api_client = metadata_funs.create_api_client()`

### Datasets
Dataset names are pulled from multiple sources - a set of hand-curated lists of dataset names and variations on the names.

`python gen_datasets.py`

This pulls dataset names from multiple sources, and outputs metadata to `datasets.json`


### Publications
Publication metadata is generated from multiple sources.
1. We take dataset names and aliases and search them through full-text documents, fetching publication ids and then retrieving the metadata associated with the publication ids, using the Dimensions API. Outputs to `/metadata/<hash>stringsearch_pub`.

`python stringsearch.py`

 2. Using manually curated linkages between datasets and publications, we take the publication DOIs and run them through the Dimensions API. Outputs to `/metadata/<hash>manually_curated_pubs`.

 `python manually_curated_publications.py`

Publications are collected and given unique identifiers (a hash of `article title` and `journal name`) by
`python gen_publication_linkages.py`


### Subfolders
`/views` contains code and data outputs for views needed for the ADRF Data Explorere.
`/metadata` contains metadata generated from this workflow, as well as the raw, manually curated datasets needed to fetch metadata.
