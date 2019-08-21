import pandas as pd
import metadata_funs
import getpass
import pandas
import json
import datetime
import time
import os
import pandas as pd
import metadata_funs
import importlib
importlib.reload(metadata_funs)



def return_string_search_dyads(exact_match: bool, dataset_string: str, api_client):
    if exact_match == True:
        api_return = metadata_funs.run_exact_string_search(string = dataset_string, api_client = api_client)
    if exact_match == False:
        api_return = run_string_search(string = dataset_string, api_client = api_client)
    pub_metadata = []
    for i in api_return['publications']:
        time.sleep( 6 )
        try:
            pub_id = i['id']
            id_metadata = run_pub_id_search(dimensions_id = pub_id, api_client = api_client)
            try:
                doi_id = id_metadata['doi']
            except:
                doi_id = None
#             id_metadata.update({'dataset_name':dataset_string})
            pub_metadata.append(id_metadata)
        except Exception as e:               
            print("Could not fetch metadata for publication: {}".format(doi_id))
    return pub_metadata

def gen_stringsearch_pub_metadata(api_client,dataset_names_list):
    pub_dataset_list = []
    for d in dataset_names_list:
        time.sleep( 6 )
        dataset_name = d['dataset_name']
        dataset_id = d['dataset_id']
        pub_dataset_dyads  = return_string_search_dyads(exact_match= True,dataset_string = dataset_name, api_client = api_client)
        if pub_dataset_dyads:
            pdd_list = []
            for pdd in pub_dataset_dyads:
                related_dataset_id = [a['dataset_id'] for a in dataset_names_list if a['dataset_name'] == dataset_name][0]
                pdd.update({'related_dataset':related_dataset_id})
                pdd_list.append(pdd)
            pub_dataset_list.append(pdd_list)
        elif not pub_dataset_dyads:
            pass
    return pub_dataset_list

def main(api_client):
    dataset_names = metadata_funs.read_datasets()
    dataset_names_list =[{'dataset_name':d['title'],'dataset_id':d['dataset_id']} for d in dataset_names]
#     dataset_names_list = [d for d in dataset_names_list if d['dataset_id'] in ['dataset-f442e418ac191ac60f7f','dataset-01bf466ee1063265fc2c']]
    stringsearch_pubs_path = os.path.join(os.getcwd(),'metadata/{}stringsearch_pubs.json'.format(metadata_funs.get_hash(str(datetime.datetime.now()))))
    stringsearch_pubs = gen_stringsearch_pub_metadata(api_client = api_client, dataset_names_list=dataset_names_list)
    pub_dataset_list_final = metadata_funs.flatten(stringsearch_pubs)
    json.dump(pub_dataset_list_final, open(stringsearch_pubs_path, 'w'), indent=2)
    return pub_dataset_list_final
