import module.get_race_result
import os
import pandas as pd
import csv

def search_race_info_csv():
    fullpaths = []
    for dirpath, dirnames, filenames in os.walk('./OUTPUT'):
        for filename in filenames:
            if(filename.endswith(".csv") and "raceInfo" in filename):
                # print(os.path.join(dirpath, filename))
                fullpaths.append(os.path.join(dirpath, filename))
    return fullpaths

def split_dateformat(date_str: str) -> tuple:
    year    = date_str[:4]
    month   = date_str[4:6]
    day     = date_str[6:8]
    return year, month, day

def init(collected_race_id_file):
    list = []
    try:
        with open(collected_race_id_file) as fr:
            reader = csv.reader(fr)
            list = [str(row)\
                    .translate(str.maketrans({"[": None, "]": None, "'": None})) for row in reader]
    except:
        pass
    
    return list

if __name__ == '__main__':
    collected_race_id_file = "./OUTPUT/collected_race_ids.csv"
    list_collected = init(collected_race_id_file)

    csv_files = search_race_info_csv()
    for csvfile in csv_files:
        first_row_flag = True
        with open(csvfile) as fr:
            while(True):
                line = fr.readline().replace("\n", "")
                if not line:
                    break
                # print(module.get_race_result.get_race_result(line))
                race_id, race_url, race_date = line.split(",")
                if(not first_row_flag) and not(race_id in list_collected):
                    # year, month, day = split_dateformat(race_date)
                    df = module.get_race_result\
                        .get_race_result(race_id = race_id, race_url = race_url, race_date = race_date)
                    print(df.sort_values("Horse_Info"))
                    # df = pd.concat([df, df_tmp], axis = 0)
                    df.sort_values("Horse_Info")                    \
                        .to_csv(csvfile.replace("Info", "Results"), \
                                header      =   False,              \
                                index       =   False,              \
                                errors      =   "ignore",           \
                                mode        =   'a',                \
                                )
                    with open(collected_race_id_file, mode = 'a') as fw:
                        fw.write(race_id + "\n")
                else:
                    first_row_flag = False
                