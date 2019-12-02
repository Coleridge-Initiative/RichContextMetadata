# RichContextMetadata
Extract or create metadata on publications and link to datasets. Results get exported to `RCPublications`.

## Generating Metadata
Clone https://github.com/NYU-CI/RCDatasets.

Metadata - primarily linkages between datasets and publications - will come from 
our partners and clients. We want to capture information on the dataset, and publication metadata, including linkages to the datasets that we are enumerating in `datasets.json`.

1. In this repo, in `/metadata`, create a subfolder for the drop you are working with, and give it a name that reflects what's in it e.g. `20190913_usda_excel` is named with the date USDA sent it, the data provider (usda) and the format. 
2. As you sift through the linkages additions to `datasets.json`, if you come across datasets that are in a publication but not listed yet. When adding an entry to `datasets.json` create a new branch from https://github.com/NYU-CI/RCDatasets. It may be helpful to name the branch with the same name as your subfolder in `/metadata`.

### Required Fields for Datasets

At a minimum, each record in the `datasets.json` file must have these
required fields:

  * `provider` -- name of the _data provider_
  * `title` -- name of the dataset
  * `id` -- a unique sequential identifier

For the names, use what the data provider shows on their web page and
try to be as consise as possible.

When adding records:

  - add to the bottom of the file
  - increment the `id` number manually
  - make sure not to introduce multiple names for the same provider

Other fields that may be included:

  * `alt_title` -- list of alternative titles or abbreviations, aka "mentions"
  * `url` -- URL for the main page describing the dataset
  * `doi` -- a unique persistent identifier assigned by the data provider
  * `alt_ids` -- other unique identifiers (alternative DOIs, etc.)
  * `description` -- a brief (tweet sized) text description of the dataset
  * `date` -- date of publication, which may help resolve conflicting identifiers

Example entry:
```
{
        "id": "dataset-058",
        "provider": "Bureau of Labor Statistics",
        "title": "Consumer Price Index",
        "alt_title": [
            "HEI"
        ],
        "url": "https://www.bls.gov/cpi/",
        "description": "The Consumer Price Index (CPI) is a measure of the average change over time in the prices paid by urban consumers for a market basket of consumer goods and services."
    }
```

3. Create a csv file in which you'll document the publication metadata (title, url, doi, etc).  Be sure to keep track of the linkages with the `dataset_id` that you just created. Ultimately you will export the publication metadata to a json file; name that according to the data drop as well. 

### Required Fields for Publications

At a minimum, each record in the `<your_unique_name>_publications.json` file must have these required fields:

  * `title` -- name of the _publication_
  * `url` -- URL for the main page describing the dataset
  * `related_dataset` -- `dataset_id` from `datasets.json`. 

Other fields that may be included:
  * `doi` -- a unique persistent identifier assigned by the data provider
  * `title` -- name of the dataset
  * `id` -- a unique sequential identifier


Example entry in `<your_unique_name>_publications.json`:
```
{
    "title": "Design Issues in USDA's Supplemental Nutrition Assistance Program: Looking Ahead by Looking Back",
    "url": "https://www.ers.usda.gov/webdocs/publications/86924/err-243.pdf?v=43124",
    "related_dataset": [
      {"dataset_id": "dataset-026"}
      ]
  }

```