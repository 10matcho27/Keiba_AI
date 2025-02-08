import module.race_calendar
import module.get_race_info
import csv
import os
import pandas as pd
import argparse

URL = 'https://race.netkeiba.com/top/calendar.html?year={year}&month={mon}'

def get_args():
    psr = argparse.ArgumentParser("get race info of selected range year\n(e.g. race_ids, race_urls, race_dates)\n")
    psr.add_argument('-s', '--start_year',  type=int,   required=True, help='the year you wanna start collecting data from')
    psr.add_argument('-e', '--end_year',    type=int,   required=True, help='the year you wanna stop collecting data')
    return psr.parse_args()

if __name__ == '__main__':
    args = get_args()
    year_start  = int(args.start_year)
    year_end    = int(args.end_year)
    rawdir = "./OUTPUT/RAW/"
    
    for year in range(year_start, year_end + 1, 1):
        csv_name = "raceInfo_{year}.csv".format(year = year)
        try:
            os.remove(rawdir + csv_name)
        except:
            pass
        df = pd.DataFrame()
        for month in range(1, 12 + 1, 1):
            race_calendar = module.race_calendar.get_race_calendar(URL.format(year = year, mon = month))
            print(race_calendar)
            for race_date in race_calendar:
                df_tmp = pd.DataFrame()
                fieldname, race_info = module.get_race_info.get_race_info(race_date)
                for key in race_info.keys():
                    df_tmp[key] = race_info[key]
                df = pd.concat([df, df_tmp], axis = 0).reset_index(drop=True)
        df.to_csv(rawdir + csv_name, index = False)
        print(df)