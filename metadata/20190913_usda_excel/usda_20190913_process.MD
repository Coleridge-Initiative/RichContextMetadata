USDA sent us an excel spreadsheet `raw_data/FY2014-19 Datasets for ERS Publications.xlsx` with titles and datasets that were used in the publicatioins. The datasets were provided as bullet-pointed lists in an excel column cell, and were inconsistently named. So, we manually verified full dataset names and added them as entries to `datasets.json` from 
https://github.com/NYU-CI/RCDatasets

`cleaning_scripts/title_urls.ipynb` reads in the titles from the excel file, extracts their underlying urls, and exports them to `producing_metadata/usda_linkages.csv` which was then manually annotated with dataset_ids from `datasets.json`.

`producing_metadata/gen_linkages.ipynb` reads in `producing_metadata/usda_linkages.csv`, fetches dataset metadata from `datasets.json` using the `dataset_id`, and runs the titles through the Dimensions API to extract any publication metadata, if exists, in Dimensions. Publication metadata is then outputted to `results/<hashed_time_stamp>_usdapubs.json`

A script in `../publications` will read in this json and stitch with other publication metadata.