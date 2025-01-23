import module.get_race_result
import os
import time
import pandas as pd


def search_race_info_csv():
    fullpaths = []
    for dirpath, dirnames, filenames in os.walk('./OUTPUT'):
        for filename in filenames:
            if(filename.endswith(".csv") and "raceInfo" in filename):
                # print(os.path.join(dirpath, filename))
                fullpaths.append(os.path.join(dirpath, filename))
    return fullpaths

if __name__ == '__main__':
    csv_files = search_race_info_csv()
    for csvfile in csv_files:
        df = pd.DataFrame()
        first_row_flag = True
        with open(csvfile) as fr:
            while(True):
                line = fr.readline().replace("\n", "")
                if not line:
                    break
                # print(module.get_race_result.get_race_result(line))
                if(not first_row_flag):
                    race_id, race_url, race_date = line.split(",")
                    # print(race_id, race_url, race_date)
                    df_tmp = module.get_race_result.get_race_result(race_id = race_id, race_url = race_url, race_date = race_date)
                    df = pd.concat([df, df_tmp], axis = 0)
                    print(df.sort_values("Horse_Info"))
                else:
                    first_row_flag = False
        df.sort_values("Horse_Info")\
            .to_csv(csvfile.replace("Info", "Results"), \
                    index       =   False, \
                    errors      =   "ignore")
            
                