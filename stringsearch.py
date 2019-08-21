import metadata_funs
import numpy as np
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

def gen_ds_names(dataset_names):
    """
    combine dataset name with dataset alias (if it exists)
    and output as dict with dataset_id (for input to return_string_search_dyads)
    """
    ds_names = []
    for d in dataset_names:
        name = metadata_funs.scrub_unicode(d['title'])
        dataset_id = d['dataset_id']
        try:
            alias = metadata_funs.scrub_unicode(d['alias'])
            ds_dict = {'dataset_name':list((name,alias)),'dataset_id':dataset_id}
        except:
            ds_dict = {'dataset_name':[name],'dataset_id':dataset_id}        
        ds_names.append(ds_dict)
    return ds_names


def return_string_search_dyads(dataset_string, api_client):
    """
    intake a dataset name
    , identify papers with that term in the full text
    , and return publication metadata
    """
    api_return = metadata_funs.run_exact_string_search(string = dataset_string, api_client = api_client)
    pub_metadata = []
    for i in api_return['publications']:
        time.sleep( 6 )
        pub_id = i['id']
        id_metadata = metadata_funs.run_pub_id_search(dimensions_id = pub_id, api_client = api_client)
        id_metadata.update({'dimensions_id':pub_id})
        pub_metadata.append(id_metadata)
    return pub_metadata


    
def gen_ss_dyad(dataset_name_dict,api_client):
    """
    intake a dataset dictionary that has a dataset_id and a list of names (name+alias)
    , and each is run through the string_search_dyads function to return publication metadata
    """

    dataset_names_list = dataset_name_dict['dataset_name']
    dataset_id = dataset_name_dict['dataset_id']
    dataset_names_list
    store_dyads = []
    for ds in dataset_names_list:
        pub_dataset_dyads  = return_string_search_dyads(dataset_string = ds, api_client = api_client)
        store_dyads.append(pub_dataset_dyads)
    store_dyads_flat = metadata_funs.flatten(store_dyads)
    for s in store_dyads_flat:
        s.update({'dataset_id':dataset_id,'linkage_source':'dataset_stringsearch'})
    return store_dyads_flat


def gen_dyad_list(ds_names):
    """
    intake a list of dataset dictionaries
    , where each dict has a dataset_id and a list of names (name+alias)
    , and run through gen_ss_dyad
    """
    big_list = []
    for d in ds_names:
        a = gen_ss_dyad(dataset_name_dict = d,api_client = api_client)
        big_list.append(a)
    return big_list


api_client = metadata_funs.create_api_client()
dataset_names = metadata_funs.read_datasets()

ds_names = gen_ds_names(dataset_names)
big_list = gen_dyad_list(ds_names = ds_names)
final_list = metadata_funs.flatten(big_list)
stringsearch_pubs_path = os.path.join(os.getcwd(),'metadata/{}stringsearch_pubs.json'.format(metadata_funs.get_hash(str(datetime.datetime.now()))))

json.dump(final_list, open(stringsearch_pubs_path, 'w'), indent=2)
