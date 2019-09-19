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
import dateutil.parser as dparser
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
#             ds_dict = {'dataset_name':list((name,alias)),'dataset_id':dataset_id}
            ds_dict = {'dataset_name':list(set(list((name,alias)))),'dataset_id':dataset_id}
        except:
            ds_dict = {'dataset_name':[name],'dataset_id':dataset_id}        
        ds_names.append(ds_dict)
    return ds_names


new_list = []
def filter_ids():
    search_path = '/Users/sophierand/RichContextMetadata/metadata/'
    pub_paths = [search_path+f for f in os.listdir(search_path) if f.endswith("stringsearch_pubs.json")]
    for p in pub_paths:
        file_date = dparser.parse(time.ctime(os.path.getctime(p)),fuzzy=True).date()
        with open(p) as json_file:
            ss_json = json.load(json_file)
        a = [{'ds_name':s['related_dataset_name'],'ds_id':s['related_dataset']
      ,'linkage_source':s['linkage_source'],'file_run':file_date
    ,'time_since_run':abs((file_date - datetime.datetime.now().date()).days)} for s in ss_json]
        b = [dict(t) for t in {tuple(d.items()) for d in a}]
        new_list.append(b)
    ss_pub_list_flat = metadata_funs.flatten(new_list)
    b_exclude = list(set([d['ds_id'] for d in ss_pub_list_flat if d['time_since_run'] <= 30]))
    return b_exclude

    

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
        id_metadata.update({'dimensions_id':pub_id,'related_dataset_name':dataset_string})
        pub_metadata.append(id_metadata)
    return pub_metadata


    
def gen_ss_dyad(dataset_name_dict,api_client):
    """
    intake a dataset dictionary that has a dataset_id and a list of names (name+alias)
    , and each is run through the string_search_dyads function to return publication metadata
    """

    dataset_names_list = dataset_name_dict['dataset_name']
    dataset_id = dataset_name_dict['dataset_id']
    store_dyads = []
    for ds in dataset_names_list:
        pub_dataset_dyads  = return_string_search_dyads(dataset_string = ds, api_client = api_client)
        store_dyads.append(pub_dataset_dyads)
    store_dyads_flat = metadata_funs.flatten(store_dyads)
    for s in store_dyads_flat:
        s.update({'related_dataset':dataset_id,'linkage_source':'dataset_stringsearch'})
    return store_dyads_flat


# def gen_dyad_list(ds_names):
#     """
#     intake a list of dataset dictionaries
#     , where each dict has a dataset_id and a list of names (name+alias)
#     , and run through gen_ss_dyad
#     """
#     big_list = []
#     for d in ds_names:
#         print('looking for ',d, ' now')
#         a = gen_ss_dyad(dataset_name_dict = d,api_client = api_client)
#         big_list.append(a)
#     return big_list

def gen_dyad_list(ds_names):
    """
    intake a list of dataset dictionaries
    , where each dict has a dataset_id and a list of names (name+alias)
    , and run through gen_ss_dyad
    """
    big_list = []
    try:
        for d in ds_names:
            print('looking for ',d, ' now')
            # a = 'i would do a string search with {}'.format(d)
            a = gen_ss_dyad(dataset_name_dict = d,api_client = api_client)
            big_list.append(a)
            time.sleep(1)
        return big_list
    except KeyboardInterrupt:
        return big_list


api_client = metadata_funs.create_api_client()
dataset_names = metadata_funs.read_datasets()
ds_names = gen_ds_names(dataset_names)
exclude_ids = filter_ids()
# ds_names_lim = [d for d  in ds_names if d['dataset_id'] in ['dataset-b48654a3feb4deaaa272','dataset-53fcd9fbd727f01baad3']]
ds_names_lim = [d for d  in ds_names if d['dataset_id'] not in exclude_ids]
# print('excluding these ids',exclude_ids)
# print('searching for these ids', ds_names_lim)
big_list = gen_dyad_list(ds_names = ds_names_lim)
# print(big_list)
final_list = metadata_funs.flatten(big_list)
stringsearch_pubs_path = os.path.join(os.getcwd(),'metadata/{}stringsearch_pubs.json'.format(metadata_funs.get_hash(str(datetime.datetime.now()))))

json.dump(final_list, open(stringsearch_pubs_path, 'w'), indent=2)
