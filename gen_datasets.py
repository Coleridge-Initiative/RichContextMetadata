import unicodedata
import datetime
import os
import json
from os import listdir
import pandas as pd
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
    return lim_excel_df_sheets      
    

def gen_data_dictionary(lim_excel_df_sheets):
    common_fields = list(set(lim_excel_df_sheets[6].columns.values) & set(lim_excel_df_sheets[5].columns.values))
    new_df_list = []
    for i in range(len(lim_excel_df_sheets)):
        a = lim_excel_df_sheets[i][common_fields]
        new_df_list.append(a)
    df = pd.concat(new_df_list).drop_duplicates()
    df = df.reset_index()
    df['dataset_id'] = ["dataset-{}".format(metadata_funs.get_hash(df['title'][_])) for _ in range(len(df.index))]
#     df['uuid'] = [str(uuid.uuid4()) for _ in range(len(df.title))]
    return df


lim_excel_df_sheets  = read_data_dictionary()
dd_df = gen_data_dictionary(lim_excel_df_sheets)


dd_dict = dd_df.to_dict('records')

pattern = re.compile('([^\sa-zA-Z]|_)+')
for i in dd_dict:
    i['title'] = pattern.sub('',i['title']).strip()
    i['title'] = unicodedata.normalize('NFC',i['title'])
    if isinstance(i['temporal_coverage_end'], datetime.date):
        i['temporal_coverage_end'] = str(dateutil.parser.parse(str(i['temporal_coverage_end'])).date())
    if isinstance(i['temporal_coverage_start'], datetime.date):
        i['temporal_coverage_start'] = str(dateutil.parser.parse(str(i['temporal_coverage_start'])).date())


json.dump(dd_dict, open('./datasets.json', 'w'), indent=2)