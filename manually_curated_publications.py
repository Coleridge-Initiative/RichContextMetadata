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



def read_curated_linkages():
    manual_linkages = os.path.join(os.getcwd(),'dataset_metadata/curated_linkages.csv')
    manual_df = pd.read_csv(manual_linkages)
    manual_df_doi = manual_df.loc[manual_df.doi.notnull()]
    manual_df_doi_dict = manual_df_doi.to_dict('records')
    return manual_df_doi_dict



def fetch_curated_metadata(manual_df_doi_dict,dataset_names,api_client):
    manual_pub_dataset_list = []
    for i in manual_df_doi_dict:
        time.sleep( 6 )
        doi_id = i['doi']
        dataset_name = i['dataset_name']
        try:
            dataset_id = [d for d in dataset_names if d['dataset_name'] == dataset_name][0]['dataset_id']
            pub_metadata = metadata_funs.run_doi_search(doi_id,api_client)
            if pub_metadata:
                pub_metadata.update({'related_dataset': dataset_id})
                manual_pub_dataset_list.append(pub_metadata)
            elif pub_metadata == None:
                pass
        except:
            pass
    return manual_pub_dataset_list


def main():
    dataset_names = metadata_funs.read_datasets()
    user = input()
    password = getpass.getpass()
    api_client = metadata_funs.connect_ds_api(username=user,password=password)
    manual_df_doi_dict =  read_curated_linkages()
    manual_pub_dataset_list = fetch_curated_metadata(manual_df_doi_dict,dataset_names,api_client)
    json.dump(manual_pub_dataset_list, open('./manually_curated_pubs.json', 'w'), indent=2)
    return manual_pub_dataset_list
