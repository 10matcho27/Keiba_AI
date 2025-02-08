import pandas as pd
import argparse
from sklearn.preprocessing import LabelEncoder
import pprint
from typing import Tuple
import os

def get_args():
    psr = argparse.ArgumentParser("get race info of selected range year\n(e.g. race_ids, race_urls, race_dates)\n")
    psr.add_argument('-s', '--start_year',  type=int,   required=True, help='the year you wanna start collecting data from')
    psr.add_argument('-e', '--end_year',    type=int,   required=True, help='the year you wanna stop collecting data')
    return psr.parse_args()

def get_integer_mapping(le) -> dict:
    ## Return a dict mapping labels to their integer values from an SKlearn LabelEncoder
    ## le = a fitted SKlearn LabelEncoder
    mapping = {}
    for iter, label in enumerate(le.classes_):
    # le.classes_ is 1-dimentional list, which has LABEL and indexs are corresponding it's LABEL_ID
        mapping.update({label:iter})
    return mapping

def encode_categorical(df: pd.DataFrame, cols: list) -> Tuple[pd.DataFrame, dict, dict]:
    lebel_mapping = {}
    le_instances = {}
    for col in cols:
        le = LabelEncoder()
        df[col] = pd.Series(le.fit_transform(df[col]))  ## encoded df
        lebel_mapping[col] = get_integer_mapping(le)    ## mapping of label encoding
        le_instances.update({col:le})                   ## instances of labelencoder
    return df, lebel_mapping, le_instances

def dict_mapping2csv(d: dict, outdir: str):
    outdir = './OUTPUT/LABEL_MAPPING/'
    os.makedirs(outdir, exist_ok=True)
    for encoded_col, each_dict in d.items():
        writeline = []
        for key, value in each_dict.items():
            # print(key + "," +str(value))
            writeline.append(str(key) + "," + str(value) + "\n")
        with open(outdir + encoded_col + '.csv', mode='w') as fw:
            fw.writelines(writeline)

def time_to_seconds(time_str):
    minutes, seconds = time_str.split(':')
    return int(minutes) * 60 + float(seconds)

def df_formatting(df: pd.DataFrame) -> pd.DataFrame:
    replace_dict_course = {" ": None, " ": None}
    replace_dict_jockey = {"▲": None, "△": None, "◇": None, "★": None, "☆": None}
    df["Course"] = df["Course"].str.translate(str.maketrans(replace_dict_course))
    df["Jockey"] = df["Jockey"].str.translate(str.maketrans(replace_dict_jockey))
    df["Horse_Weight"] = df["Horse_Weight"].str.replace("\(.*[0-9]{1,2}\)", "", regex=True)
    df['Time'] = df['Time'].apply(time_to_seconds)
    return df

if __name__ == '__main__':
    args = get_args()
    year_start  = int(args.start_year)
    year_end    = int(args.end_year)
    rawdir = "./OUTPUT/RAW/"
    convdir = "./OUTPUT/CONVERTED/"
    labelmapdir = "./OUTPUT/LABEL_MAPPING/"
    
    col_name = ["Result_Num", 
                "Waku", 
                "Num", 
                "Horse_Name", 
                "Horse_Old", 
                "Weight_for_Age", 
                "Jockey", 
                "Time", 
                "Popularity", 
                "Odds", 
                "Passing-Order-at-Corner",
                "Stable",
                "Horse_Weight",
                "Race_Id",
                "Race_Date",
                "Race_Time",
                "Course",
                "Weather",
                "Course_Status"]
    col_encode = ["Horse_Name", 
                "Horse_Old", 
                "Jockey", 
                "Stable",
                "Course",
                "Weather",
                "Course_Status",
                "Race_Time",
                "Race_Id",
                "Race_Date"]
    df_each_year = {}
    df = pd.DataFrame()

    os.makedirs(convdir, exist_ok=True)
    ## load race result to df
    for year in range(year_start, year_end + 1, 1):
        csv_name = 'raceResults_{year}.csv'.format(year=year)
        df_temp = pd.read_csv(rawdir + csv_name, header=None, low_memory=False)
        df_each_year.update({year:df_temp})
        df = pd.concat([df, df_temp], axis=0)
    ## set column names and df formatting
    df.columns = col_name
    df = df_formatting(df)
    csv_name = "raceInfo_{year_start}_to_{year_end}_formatted.csv".\
                format(year_start=year_start, year_end=year_end)
    df.to_csv(convdir + csv_name, index = False, header = True)
    
    for year, df in df_each_year.items():
        csv_name = 'raceResults_{year}.csv'.format(year=year)
        df.columns = col_name
        df = df_formatting(df)
        df.to_csv(convdir + csv_name, index = False, header = col_name)
    
    ## labelencoding 
    df, lebel_mapping, le_instances= encode_categorical(df, col_encode)
    # pprint.pprint(lebel_mapping)
    # print(le_instances['Weather'].classes_)
    dict_mapping2csv(lebel_mapping, labelmapdir)
    csv_name = "raceInfo_{year_start}_to_{year_end}_labelEncoded.csv".\
                format(year_start=year_start, year_end=year_end)
    df.to_csv(convdir + csv_name, index = False, header = True)
