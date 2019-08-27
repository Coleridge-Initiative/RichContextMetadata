import getpass
import pandas
import datetime
import time
import os
import pandas as pd
import metadata_funs
import json
import importlib
importlib.reload(metadata_funs)
import datetime

def read_curated_linkages():
    manual_linkages = os.path.join(os.getcwd(),'metadata/manually_curated_metadata/curated_linkages.csv')
    manual_df = pd.read_csv(manual_linkages)
    manual_df_doi = manual_df.loc[manual_df.doi.notnull()]
    return manual_df_doi


def fetch_curated_metadata(manual_df_doi_dataset,dataset_names,api_client):
    manual_pub_dataset_list = []
    for idx,row in manual_df_doi_dataset.iterrows():
        time.sleep( 6 )
        doi_id = row.doi
        dataset_name = row.dataset_name
        dataset_id = [d for d in dataset_names if d['title'] == dataset_name][0]['dataset_id']
        pub_metadata = metadata_funs.run_doi_search(doi_id,api_client)
        if pub_metadata:
            pub_metadata.update({'related_dataset': dataset_id,'related_dataset_name': dataset_name,'dimensions_id': pub_metadata['id'],'linkage_source': "manually_curated"})
            manual_pub_dataset_list.append(pub_metadata)
        elif pub_metadata == None:
            pass
    return manual_pub_dataset_list


api_client = metadata_funs.create_api_client()
dataset_names = metadata_funs.read_datasets()
dataset_names_df = pd.DataFrame(dataset_names)
manual_df_doi = read_curated_linkages()
manual_df_doi_dataset = manual_df_doi.merge(dataset_names_df,left_on = 'dataset_name',right_on = 'title')

manual_pub_dataset_list = fetch_curated_metadata(manual_df_doi_dataset = manual_df_doi_dataset, dataset_names = dataset_names,api_client = api_client)

manual_pubs_path = os.path.join(os.getcwd(),'metadata/{}manually_curated_pubs.json'.format(metadata_funs.get_hash(str(datetime.datetime.now()))))


json.dump(manual_pub_dataset_list, open(manual_pubs_path, 'w'), indent=2)
