
import unicodedata
import datetime
import os
import json
from os import listdir
import pandas as pd
pd.set_option('display.width', 10000)
import dateutil.parser
import metadata_funs
import xlrd
import datetime
from os.path import isfile, join
import ntpath
import uuid
import re



def read_data_dictionary():
    ex_data_path = os.path.join(os.getcwd(),'metadata/manually_curated_metadata/ADRF Dataset Metadata.xlsx')
    xls = pd.ExcelFile(ex_data_path)
    sheet_to_df_map = pd.read_excel(ex_data_path, sheet_name=None)
    uniform_sheets = ['course1-datasets','course2-datasets' ,'kcmo-datasets', 'in_data_2019-datasets'
    , 'mo_data_2019-datasets', 'usda-datasets','bundesbank-rc']
    lim_excel_df_sheets  = []
    for i,v in enumerate(sheet_to_df_map):
        if v in uniform_sheets:
            lim_excel_df_sheets.append(sheet_to_df_map[v])
    common_fields = list(set(lim_excel_df_sheets[6].columns.values) & set(lim_excel_df_sheets[5].columns.values))
    new_df_list = []
    for i in range(len(lim_excel_df_sheets)):
        a = lim_excel_df_sheets[i][common_fields]
        new_df_list.append(a)
    df = pd.concat(new_df_list).drop_duplicates()
    pattern = re.compile('([^\sa-zA-Z]|_)+')
    df['title'] = df['title'].apply(lambda x: pattern.sub('',x).strip())
    df['title'] = df['title'].apply(lambda x: re.sub(' +', ' ',x))
    return df  


# In[3]:


def read_curated_linkages():
    linkage_path = os.path.join(os.getcwd(),'metadata/manually_curated_metadata/curated_linkages.csv')
    csv = pd.read_csv(linkage_path)
    curated_dataset_names = csv.dataset_name.unique().tolist()
    return curated_dataset_names



def read_manual_ds_names():
    manual_dataset_json_path =  os.path.join(os.getcwd(),'metadata/manually_curated_metadata/curated_dataset_names.json')
    with open(manual_dataset_json_path) as json_file:
        manual_dataset_json = json.load(json_file)
    return manual_dataset_json


def combine_manual_data():
    manual_dataset_names_list = read_manual_ds_names()
    manual_dataset_names = [d['dataset_name'] for d in manual_dataset_names_list]
    curated_dataset_names = read_curated_linkages()
    dataset_names_list = list(set(manual_dataset_names + curated_dataset_names))
    return dataset_names_list


def concat_dataset_dfs(dataset_names_list,dataset_df):
    addl_datasets = [c for c in dataset_names_list if c not in dataset_df.title.unique().tolist()]
    tmp = pd.DataFrame({'description': '','data_steward_org': '',  'temporal_coverage_end': '',  'source_archive': '',
  'dataset_documentation': '',  'data_classification': '',  'external_id': '',  'keywords': '',  'access_actions_required': '',
  'temporal_coverage_start': '',  'dataset_version': '',
  'access_requirements': '',  'dataset_header_desc': '',  'dataset_citation': '',  'title': '',  'category': '',
  'geographical_coverage': '','data_steward': '',  'reference_url': '',  'source_url': '',  'related_articles': '',
  'adrf_id': '',  'geographical_unit': '',  'data_usage_policy': '',  'data_provider': '','filenames': '','title':addl_datasets})
    data_df_full = pd.concat([dataset_df, tmp])
    return data_df_full



dataset_names_list = combine_manual_data()
dataset_df  = read_data_dictionary()
data_df_full = concat_dataset_dfs(dataset_names_list = dataset_names_list,dataset_df = dataset_df)
data_df_full['dataset_id'] = data_df_full.title.apply(lambda x: "dataset-{}".format(metadata_funs.get_hash(x)))

data_df_full = data_df_full.drop_duplicates()
dd_dict = data_df_full.to_dict('records')


for i in dd_dict:
    i['title'] = unicodedata.normalize('NFC',i['title'])
    if isinstance(i['temporal_coverage_end'], datetime.date):
        i['temporal_coverage_end'] = str(dateutil.parser.parse(str(i['temporal_coverage_end'])).date())
    if isinstance(i['temporal_coverage_start'], datetime.date):
        i['temporal_coverage_start'] = str(dateutil.parser.parse(str(i['temporal_coverage_start'])).date())


json.dump(dd_dict, open('datasets.json', 'w'), indent=2)

