import module.get_race_result
import os
import time

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
                    module.get_race_result.get_race_result(race_id = race_id, race_url = race_url, race_date = race_date)
                else:
                    first_row_flag = False
                