import re
import time
import bs4
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

import pandas as pd
import numpy as np

def get_race_result(race_url: str):
    # service = Service()
    options = webdriver.ChromeOptions()
    options.add_argument("--headless=new")
    options.add_argument("--disable-popup-blocking")
    options.add_argument('--ignore-ssl-errors')
    options.add_argument("--no-sandbox")
    options.add_argument("--ignore-certificate-errors") 
    options.add_experimental_option('excludeSwitches', ['enable-logging'])
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_argument("--disable-dev-shm-usage")
    options.page_load_strategy = 'eager'
    prefs = {
        'profile.managed_default_content_settings.images': 2,  # 画像を無効化
        # 'profile.managed_default_content_settings.javascript': 2  # JavaScriptを無効化（必要な場合は除く）
    }
    options.add_experimental_option('prefs', prefs)
    # service.creation_flags = 0x08000000 ## makes "DevTools listening ~~~" unvisible in headless mode
    # driver  = webdriver.Chrome(options = options)
    # driver  = webdriver.Chrome(options = options, service=service)
    driver = webdriver.Chrome(options = options, service=ChromeService(ChromeDriverManager().install()))
    driver.set_page_load_timeout(15)
    wait    = WebDriverWait(driver, 10)
    ### try accessing to target url
    driver.get(race_url)
    ### wait for finishing search of target keyword "#tab_ResultSelect_1_con" 
    wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '#tab_ResultSelect_1_con')))
    html    = driver.page_source
    soup    = BeautifulSoup(html, 'lxml')
    
    table_raw = soup.find('table', {'id': 'All_Result_Table'})
    race_result = {}
    ### extract table info
    for body in table_raw.find('tbody'):
        pattern_Odds = r"Odds (BgYellow|BgOrange|BgBlue02|Txt_C)"
        pattern_time = r"\d{1,2}:\d{2}\.\d"
        for row in body:
            if(type(row) == bs4.element.Tag):
                col_name = ' '.join(row.get('class'))
                val = row.get_text(strip=True)
                ### column name formatting
                if("Num Waku" in col_name):
                    col_name = "Num Waku"
                if(re.match(pattern_Odds, col_name)):
                    col_name = "Odds_Txt_C"
                if(("Time" in col_name) and not re.match(pattern_time, val)):
                    continue
                col_name = col_name.replace(" ", "_")
                ### insert data into dict
                if(col_name not in race_result):
                    race_result[col_name] = [val]
                else:
                    race_result[col_name].append(val)
    df = pd.DataFrame.from_dict(race_result)
    print(df)
    driver.close()

    return df

if __name__ == '__main__':
    race_ids = get_race_result('https://race.netkeiba.com/race/result.html?race_id=202404040407&rf=race_submenu')
    # print(race_ids)