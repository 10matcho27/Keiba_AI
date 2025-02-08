import pandas as pd
import argparse
from sklearn.preprocessing import LabelEncoder
import pprint
from typing import Tuple

def get_args():
    psr = argparse.ArgumentParser("test env")
    psr.add_argument('-y', '--year',  type=int,   required=True, help='the year you wanna load data')
    return psr.parse_args()

def get_integer_mapping(le) -> dict:
    ## Return a dict mapping labels to their integer values from an SKlearn LabelEncoder
    ## le = a fitted SKlearn LabelEncoder
    mapping = {}
    for cl in le.classes_:
        mapping.update({cl:le.transform([cl])[0]})
    return mapping

def encode_categorical(df: pd.DataFrame, cols: list) -> Tuple[pd.DataFrame, dict]:
    lebel_mapping = {}
    for col in cols:
        le = LabelEncoder()
        df[col] = pd.Series(le.fit_transform(df[col]))
        lebel_mapping[col] = get_integer_mapping(le)
    return df, lebel_mapping

if __name__ == '__main__':
    args = get_args()
    year = args.year

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
                "Horse_Weight(plus-or-minus)",
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
                "Course_Status"]
    
    df = pd.read_csv('./OUTPUT/raceResults_{year}.csv'.format(year=year), header=None, low_memory=False)
    df.columns = col_name
    print(df)
    df, lebel_mapping = encode_categorical(df, col_encode)
    print(df)
    pprint.pprint(lebel_mapping)