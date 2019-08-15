# RichContextMetadata
Extracting metadata on publications, datasets and persons, and drawing relationships between these three entity types.

## Generating Metadata

### Datasets
`gen_datasets.py` pulls dataset names from multiple sources, and outputs metadata to `datasets.json`

### Publications
`gen_publications.py` generates publication metadata (including linkages to datasets). It generates publication metadata from
1. linkages from manually curated data (`gen_manual_pubs`) and outputs to `/metadata/<hash>manually_curated_pubs`
2.  linkages from string search data (Dimensions API) (run `gen_ss_pubs`) and outputs to `/metadata/<hash>stringsearch_pub`

To generate these publication metadata, run the following:
`import gen_publications`
`api_client = gen_publications.gen_api_client()`
`gen_publications.gen_manual_pubs(api_client = api_client)`
`gen_publications.gen_ss_pubs(api_client = api_client)`

The combine the outputs, run
`gen_publication_linkages.py`.

This code collates the publication-dataset linkages and metadata from the manually and string-searched generated metadata, and assigns
a unique `pub_id`, which is hashed from `title`,`doi` and `journal`.


### Subfolders
`/views` contains code and data outputs for views needed for the ADRF Data Explorere.
`/metadata` contains metadata generated from this workflow, as well as the raw, manually curated datasets needed to fetch metadata.
