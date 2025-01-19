import re
import time
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

url_template        = 'https://race.netkeiba.com/top/race_list.html?kaisai_date={race_date}'
result_url_template = 'https://race.netkeiba.com/race/result.html?race_id={race_id}&rf=race_submenu'

def get_race_ids(race_date: str):
    url = url_template.format(race_date = race_date)
    print(url)
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
    try:
        ### try accessing to target url
        driver.get(url)
        ### wait for finishing search of target keyword "#RaceTopRace" 
        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '#RaceTopRace')))
        html    = driver.page_source
        soup    = BeautifulSoup(html, 'lxml')
        race_ids = []
        race_urls = []
        for a_tag in soup.select('.RaceList_DataItem > a:first-of-type'):
            race_id = re.search(r'race_id=(.+)&', a_tag.get('href')).group(1)
            race_ids.append(race_id)
            race_urls.append(result_url_template.format(race_id = race_id))
    # finally:
        driver.close()
        # driver.quit()
    except:
        print("some errors occurred, retry...")
        driver.close()
        driver.quit()
        time.sleep(1)
        race_ids, race_urls = get_race_ids(race_date)
    return race_ids, race_urls

if __name__ == '__main__':
    race_ids = get_race_ids('')
    print(race_ids)