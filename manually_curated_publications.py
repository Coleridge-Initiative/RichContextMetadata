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
    print('enter your dimensions api username')
    user = input()
    print('enter your dimensions api password')
    pw = getpass.getpass()
    api_client = metadata_funs.connect_ds_api(username = user, password = pw)
#     now = datetime.datetime.now()
    dataset_names_list = metadata_funs.read_datasets()
    dataset_names =[{'dataset_name':d['title'],'dataset_id':d['dataset_id']} for d in dataset_names_list]
    manual_df_doi_dict =  read_curated_linkages()
    manual_pub_dataset_list = fetch_curated_metadata(manual_df_doi_dict,dataset_names,api_client)
    manual_pubs_path = os.path.join(os.getcwd(),'metadata/{}manually_curated_pubs.json'.format(metadata_funs.get_hash(str(datetime.datetime.now()))))
    json.dump(manual_pub_dataset_list, open(manual_pubs_path, 'w'), indent=2)
#         json.dump(manual_pub_dataset_list, open('./metadata/manually_curated_pubs.json', 'w'), indent=2)
    return manual_pub_dataset_list


