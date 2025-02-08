import re
from bs4 import BeautifulSoup
import requests

URL = 'https://race.netkeiba.com/top/calendar.html?year={year}&month={mon}'

def get_race_calendar(url: str) -> list[str]:
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:133.0) Gecko/20100101 Firefox/133.0'
    }
    r = requests.get(url, headers=headers)
    r.raise_for_status()
    soup = BeautifulSoup(r.content, 'lxml')
    race_calendar = []
    for a_tag in soup.select('.Calendar_Table .Week > td > a'):
        # print(a_tag)
        race_date = re.search(r'kaisai_date=(.+)', a_tag.get('href')).group(1)
        race_calendar.append(race_date)
    return race_calendar

if __name__ == '__main__':
    year_start  = 1999
    year_end    = 2000
    for year in range(year_start, year_end + 1, 1):
        for month in range(1, 12 + 1, 1):
            race_calendar = get_race_calendar(URL.format(year = year, mon = month))
            print(race_calendar)