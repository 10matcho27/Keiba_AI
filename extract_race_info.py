import module.race_calendar
import module.get_race_info
import csv
import os
import pandas as pd

URL = 'https://race.netkeiba.com/top/calendar.html?year={year}&month={mon}'

if __name__ == '__main__':
    # URL_LIST = []
    year_start  = 2020
    year_end    = 2025
    try:
        os.remove("./OUTPUT/race_result_info.csv")
    except:
        pass
    for year in range(year_start, year_end + 1, 1):
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
        df.to_csv("./OUTPUT/raceInfo_{year}.csv".format(year = year), index = False)
        print(df)