import os
import pandas as pd
import unicodedata
import datetime
import metadata_funs
import dateutil
import json

# def assign_id(dataset_entry,fields_to_hash):
#     hash_vals = [(v) for k,v in dataset_entry.items() if k in fields_to_hash]
#     dataset_entry['dataset_id'] = "dataset-" + metadata_funs.get_hash(hash_vals)
#     dataset_entry['dataset_id_metadata'] = {'dataset_id':dataset_entry['dataset_id']
#                                             ,'hashed_columns':fields_to_hash
# #                                             ,'date_created':datetime.datetime.now()}
#                                             ,'date_created':convert_date(datetime.datetime.now())}
# #                                                 ,'date_created':str(dateutil.parser.parse(str(datetime.datetime.now())).date())}
#     return dataset_entry

# def convert_date(a_date):
#     new_date = str(dateutil.parser.parse(str(a_date)).date())
#     return new_date
    
# def read_adrf_dataset_md():
#     linkage_path = os.path.join(os.getcwd(),'metadata/manually_curated_metadata/adrf_metadata.csv')
#     adrf_md_df = pd.read_csv(linkage_path)
#     return adrf_md_df


# def read_manual_ds_names():
#     manual_dataset_json_path =  os.path.join(os.getcwd(),'metadata/manually_curated_metadata/curated_dataset_names_alias.json')
#     with open(manual_dataset_json_path) as json_file:
#         manual_dataset_json = json.load(json_file)
#     return manual_dataset_json

# def read_ds_names(adrf_md):
#     titles = adrf_md.title.unique().tolist()
#     alias =  adrf_md.alias.unique().tolist()
#     adrf_ds_names = list(set(titles+alias))
#     return adrf_ds_names

# def update_archive_dict(dataset_entry):
#     hist_dict = {'dataset_id':dataset_entry['dataset_id'],'date_archived':datetime.datetime.now()}
#     hist_dict.update(dataset_entry['dataset_id_metadata'])
#     return hist_dict
def assign_id(dataset_entry,fields_to_hash):
    hash_vals = [(v) for k,v in dataset_entry.items() if k in fields_to_hash]
    dataset_entry['dataset_id'] = "dataset-" + metadata_funs.get_hash(hash_vals)
    dataset_entry['dataset_id_metadata'] = {'dataset_id':dataset_entry['dataset_id']
                                            ,'hashed_columns':fields_to_hash
                                            ,'date_created':convert_date(datetime.datetime.now())}
    return dataset_entry

def convert_date(a_date):
    new_date = str(dateutil.parser.parse(str(a_date)).date())
    return new_date


def get_last_id(dataset_entry):
    most_recent_date = max([convert_date(t['date_archived']) for t in dataset_entry['dataset_id_history']])
    most_recent_id = [t['dataset_id'] for t in dataset_entry['dataset_id_history'] if t['date_archived'] == most_recent_date][0]
    return most_recent_id

def read_adrf_dataset_md():
    linkage_path = os.path.join(os.getcwd(),'metadata/manually_curated_metadata/adrf_metadata.csv')
    adrf_md_df = pd.read_csv(linkage_path)
    return adrf_md_df


def read_manual_ds_names():
    manual_dataset_json_path =  os.path.join(os.getcwd(),'metadata/manually_curated_metadata/curated_dataset_names_alias.json')
    with open(manual_dataset_json_path) as json_file:
        manual_dataset_json = json.load(json_file)
    return manual_dataset_json

def read_ds_names(adrf_md):
    titles = adrf_md.title.unique().tolist()
    alias =  adrf_md.alias.unique().tolist()
    adrf_ds_names = list(set(titles+alias))
    return adrf_ds_names

def update_archive_dict(dataset_entry):
    
    hist_dict = {'dataset_id':dataset_entry['dataset_id'],'date_archived':convert_date(datetime.datetime.now())}

    hist_dict.update(dataset_entry['dataset_id_metadata'])
    return hist_dict




def main():
    adrf_ds_df = read_adrf_dataset_md()
    adrf_ds_names = read_ds_names(adrf_ds_df)
    man_ds_names = read_manual_ds_names()

    addl_ds_names = [i for i in man_ds_names if i['title'] not in adrf_ds_names]
    adrf_dd_dict = adrf_ds_df.to_dict('records')


    final_ds_dict = adrf_dd_dict + addl_ds_names

    dd_dict = final_ds_dict
    for i in dd_dict:
        i['title'] = unicodedata.normalize('NFC',i['title'])
        fields_to_hash = ['title']
        i = assign_id(dataset_entry = i,fields_to_hash = fields_to_hash)
        hist_dict = update_archive_dict(i)
        try:
            i['dataset_id_history']
            i['dataset_id_history'].append(hist_dict)
        except:
            hist_dict_list = []
            hist_dict_list.append(hist_dict)
            i['dataset_id_history'] = hist_dict_list
        last_id = get_last_id(i)
        if last_id == i['dataset_id']:
            in_use = True
        elif last_id != i['dataset_id']:
            in_use = False
        this_hist_dict = [h for h in hist_dict_list if h['dataset_id'] == i['dataset_id']][0]
        this_hist_dict.update({'in_use':in_use})
        try:
            if isinstance(i['temporal_coverage_end'], datetime.date):
                i['temporal_coverage_end'] = convert_date(i['temporal_coverage_end'])
    #             i['temporal_coverage_end'] = str(dateutil.parser.parse(str(i['temporal_coverage_end'])).date())
            if isinstance(i['temporal_coverage_start'], datetime.date):
                i['temporal_coverage_end'] = convert_date(i['temporal_coverage_start'])
    #             i['temporal_coverage_start'] = str(dateutil.parser.parse(str(i['temporal_coverage_start'])).date())
        except:
            pass

    return dd_dict


#     for i in dd_dict:
#         i['title'] = unicodedata.normalize('NFC',i['title'])
#         fields_to_hash = ['title']
#         i = assign_id(dataset_entry = i,fields_to_hash = fields_to_hash)
#         hist_dict = update_archive_dict(i)
# #         hist_list.append(hist_dict)
# #         dataset_entry['dataset_id_history'] = hist_list
#         try:
#             i['dataset_id_history']
#             i['dataset_id_history'].append(hist_dict)
#         except:
#             hist_dict_list = []
#             hist_dict_list.append(hist_dict)
#             i['dataset_id_history'] = hist_dict_list
#         try:
#             if isinstance(i['temporal_coverage_end'], datetime.date):
#                 i['temporal_coverage_end'] = str(dateutil.parser.parse(str(i['temporal_coverage_end'])).date())
#             if isinstance(i['temporal_coverage_start'], datetime.date):
#                 i['temporal_coverage_start'] = str(dateutil.parser.parse(str(i['temporal_coverage_start'])).date())
#         except:
#             pass
#     return dd_dict

dd_dict = main()    
dd_dict_lim = [{k: v for k, v in d.items() if k in ['title','dataset_id','alias','dataset_id_metadata','dataset_id_history','data_steward']} for d in dd_dict]

json.dump(dd_dict, open('new_metadata/datasets.json', 'w'), indent=2)
json.dump(dd_dict_lim, open('new_metadata/datasets_lim.json', 'w'), indent=2)
