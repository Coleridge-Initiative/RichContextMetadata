import gen_datasets
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
# importlib.reload(metadata_funs)



# def gen_stringsearch_pub_metadata(api_client,dataset_names_listing):
#     pub_dataset_list = []
#     for d in dataset_names_listing:
#         time.sleep( 6 )
#         dataset_name = d['dataset_name']
#         dataset_id = d['dataset_id']
#         pub_dataset_dyads  = metadata_funs.return_string_search_dyads(exact_match= True,dataset_string = dataset_name, api_client = api_client)
#         if pub_dataset_dyads:
#             pdd_list = []
#             for pdd in pub_dataset_dyads:
#                 related_dataset_id = [a['dataset_id'] for a in dataset_names_listing if a['dataset_name'] == dataset_name][0]
#                 pdd.update({'related_dataset':related_dataset_id})
#                 pdd_list.append(pdd)
#             pub_dataset_list.append(pdd_list)
#         elif not pub_dataset_dyads:
#             pass
#     pub_dataset_list_final = metadata_funs.flatten(pub_dataset_list)
#     return pub_dataset_list_final

def gen_stringsearch_pub_metadata(api_client,dataset_names_list):
    pub_dataset_list = []
    for d in dataset_names_list:
        time.sleep( 6 )
        dataset_name = d['dataset_name']
        dataset_id = d['dataset_id']
        pub_dataset_dyads  = metadata_funs.return_string_search_dyads(exact_match= True,dataset_string = dataset_name, api_client = api_client)
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
#     a_dataset_names_listing = [d for d in dataset_names_list if d['dataset_id'] in ['dataset-f442e418ac191ac60f7f','dataset-01bf466ee1063265fc2c']]
    stringsearch_pubs = gen_stringsearch_pub_metadata(api_client = api_client, dataset_names_listing=dataset_names_list)
    pub_dataset_list_final = metadata_funs.flatten(stringsearch_pubs)
    json.dump(pub_dataset_list_final, open('./stringsearch_pubs.json', 'w'), indent=2)
    return pub_dataset_list_final

if __name__ == "__main__":
    main()
