#### Populating `false_positives.csv`

Identify publication linkages that were erroneously linked to datasets. 
Most linkages for validation were pulled by doing a full text string search 
with the dataset name through the Dimensions API. Results were placed in subfolders of `RichContextMetadata/metadata` and then validated by the Rich Context team. Some were false positives - e.g. the dataset may have been referenced but was not actually used in the paper. We want to capture the false positives, and if possible the reasons for the match - e.g. punctuation issue, dataset was mentioned as a reference in another paper or as background, etc.

#### Populating `empty_search_results.csv`

Some search strings did not return any results - those spreadsheets are empty. We want to record the string that led to the empty result and the `dataset-id` from `RCDatasets/datasets.json` associated with the dataset.


