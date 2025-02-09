import pandas as pd
import argparse
from sklearn.preprocessing import LabelEncoder
import pprint
from typing import Tuple
import os
import re

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

def detect_top3(result_num: str):
    '''if in top3,  return 1
        or not,     return 0'''
    top3_flag = 0
    if int(result_num) <= 3:
        top3_flag = 1
    return top3_flag

def detect_sex(horse_info: str):
    '''sex: 
        セン馬  - 0 (牡馬を去勢した馬)
        牡馬    - 1 (オスの競走馬)
        牝馬    - 2 (メスの競走馬)
    '''
    sex = 0
    if("牡" in horse_info):
        sex = 1
    elif("牝" in horse_info):
        sex=2
    return sex

def detect_old(horse_info: str):
    '''return horse old'''
    pattern = re.search(r'\d+', horse_info)
    if pattern:
        return pattern.group()
    return None

def detect_month(race_date):
    '''return month'''
    pattern = r'^(\d{4})(\d{2})(\d{2})$'
    match = re.match(pattern, str(race_date))
    if match:
        yyyy, mm, dd = match.groups()
        return mm
    else:
        return None

def classify_raceTime(race_time: str):
    """
    receive HH:MM format strings, and classify them following below rule
      - 00:00 - 10:59 → 0 (Morning)
      - 11:00 - 13:59 → 1 (Afternooon)
      - 14:00 - 16:59 → 2 (Evening)
      - 17:00 - 23:59 → 3 (Night)
    """
    pattern = re.match(r'(\d{2}):(\d{2})', race_time)
    hour = int(pattern.group(1))
    # minute = int(m.group(2))
    if hour < 11:
        return 0
    elif hour < 14:
        return 1
    elif hour < 17:
        return 2
    else:
        return 3

def df_formatting(df: pd.DataFrame) -> pd.DataFrame:
    replace_dict_course = {" ": None, " ": None}
    replace_dict_jockey = {"▲": None, "△": None, "◇": None, "★": None, "☆": None}
    df["Course"] = df["Course"].str.translate(str.maketrans(replace_dict_course))
    df["Jockey"] = df["Jockey"].str.translate(str.maketrans(replace_dict_jockey))
    df["Horse_Weight"] = df["Horse_Weight"].str.replace("\(.*[0-9]{1,2}\)", "", regex=True)
    df['Time'] = df['Time'].apply(time_to_seconds)
    df['Top3'] = df['Result_Num'].apply(detect_top3)
    df['Horse_Sex'] = df['Horse_Info'].apply(detect_sex)
    df['Horse_Old'] = df['Horse_Info'].apply(detect_old)
    df['Race_Month'] = df['Race_Date'].apply(detect_month)
    df['Racetime_Class'] = df['Race_Time'].apply(classify_raceTime)
    return df

def drop_redundancy_col(df: pd.DataFrame, col_red: list) -> pd.DataFrame:
    '''drop given column data (col_red) from df'''
    for col_name in col_red:
        df = df.drop(columns=col_name)
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
                "Horse_Info", 
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
                # "Horse_Info", 
                "Jockey", 
                "Stable",
                "Course",
                "Weather",
                "Course_Status",
                "Race_Time",
                "Race_Id",
                "Race_Date"
                ]
    col_drop = ["Horse_Info",
                 "Passing-Order-at-Corner"]
    df_each_year = []
    df = pd.DataFrame()

    os.makedirs(convdir, exist_ok=True)
    ## load race result to df
    for year in range(year_start, year_end + 1, 1):
        csv_name = 'raceResults_{year}.csv'.format(year=year)
        df_temp = pd.read_csv(rawdir + csv_name, header=None, low_memory=False)
        ## set column names and df formatting
        df_temp.columns = col_name
        df_temp = df_formatting(df_temp)
        df_temp = drop_redundancy_col(df=df_temp, col_red=col_drop)
        df_each_year.append(df_temp)
        df_temp.to_csv(convdir + csv_name, index = False, header = True)
        # df = pd.concat([df, df_temp], axis=0)
    
    df_corrected = [df_each_year[0]] + [df.iloc[1:] for df in df_each_year[1:]]
    df = pd.concat(df_corrected, ignore_index=True)

    csv_name = "raceInfo_{year_start}_to_{year_end}_formatted.csv".\
                format(year_start=year_start, year_end=year_end)
    df.to_csv(convdir + csv_name, index = False, header = True)
    
    ## labelencoding 
    df, lebel_mapping, le_instances= encode_categorical(df, col_encode)
    # pprint.pprint(lebel_mapping)
    # print(le_instances['Weather'].classes_)
    dict_mapping2csv(lebel_mapping, labelmapdir)
    csv_name = "raceInfo_{year_start}_to_{year_end}_labelEncoded.csv".\
                format(year_start=year_start, year_end=year_end)
    df.to_csv(convdir + csv_name, index = False, header = True)
