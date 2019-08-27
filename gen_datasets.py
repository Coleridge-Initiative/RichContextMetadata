import os
import pandas as pd
import unicodedata
import datetime
import metadata_funs
import json



def read_adrf_dataset_md():
    linkage_path = os.path.join(os.getcwd(),'metadata/manually_curated_metadata/adrf_metadata.csv')
    adrf_md_df = pd.read_csv(linkage_path)
    return adrf_md_df


def read_manual_ds_names():
    manual_dataset_json_path =  os.path.join(os.getcwd(),'metadata/manually_curated_metadata/curated_dataset_names.json')
    with open(manual_dataset_json_path) as json_file:
        manual_dataset_json = json.load(json_file)
    return manual_dataset_json

def read_ds_names(adrf_md):
    titles = adrf_md.title.unique().tolist()
    alias =  adrf_md.alias.unique().tolist()
    adrf_ds_names = list(set(titles+alias))
    return adrf_ds_names


adrf_ds_df = read_adrf_dataset_md()
adrf_ds_names = read_ds_names(adrf_ds_df)
man_ds_names = read_manual_ds_names()

addl_ds_names = [i for i in man_ds_names if i['title'] not in adrf_ds_names]
adrf_dd_dict = adrf_ds_df.to_dict('records')


final_ds_dict = adrf_dd_dict + addl_ds_names

dd_dict = final_ds_dict

for i in dd_dict:
    i['title'] = unicodedata.normalize('NFC',i['title'])
    i['dataset_id'] = metadata_funs.get_hash(i['title'],prefix = 'dataset-')
    try:
        if isinstance(i['temporal_coverage_end'], datetime.date):
            i['temporal_coverage_end'] = str(dateutil.parser.parse(str(i['temporal_coverage_end'])).date())
        if isinstance(i['temporal_coverage_start'], datetime.date):
            i['temporal_coverage_start'] = str(dateutil.parser.parse(str(i['temporal_coverage_start'])).date())
    except:
        pass

    
dd_dict_lim = [{k: v for k, v in d.items() if k in ['title','dataset_id','alias']} for d in dd_dict]

json.dump(dd_dict, open('datasets.json', 'w'), indent=2)
json.dump(dd_dict_lim, open('datasets_lim.json', 'w'), indent=2)
