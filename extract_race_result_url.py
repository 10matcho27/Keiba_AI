import module.race_calendar
import module.get_race_id
import time
import os

URL = 'https://race.netkeiba.com/top/calendar.html?year={year}&month={mon}'

if __name__ == '__main__':
    URL_LIST = []
    year_start  = 2020
    year_end    = 2025
    try:
        os.remove("./OUTPUT/race_result_urls.csv")
    except:
        pass
    for year in range(year_start, year_end + 1, 1):
        for month in range(1, 12 + 1, 1):
            race_calendar = module.race_calendar.get_race_calendar(URL.format(year = year, mon = month))
            print(race_calendar)
            for race_date in race_calendar:
                time.sleep(0.5)
                race_ids, race_urls = module.get_race_id.get_race_ids(race_date)
                URL_LIST = URL_LIST + race_urls
            # for url in URL_LIST:
            #     print(url)
            with open("./OUTPUT/race_result_urls.csv", mode='a') as fw:
                for line in URL_LIST:
                    fw.write(line + "\n")
            URL_LIST = []