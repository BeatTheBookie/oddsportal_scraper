
# general
import boto3
import requests
from io import StringIO
import io
import pandas as pd
from datetime import date, time
import datetime
import time
import json
import re
import html
from scrapy.http import HtmlResponse
from w3lib.html import remove_tags
import requests
import html
from requests_html import HTMLSession

# beatiful soap
import requests
from bs4 import BeautifulSoup
import pandas as pd
import json


# selium browser
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC




#
# function for general browser configuration
#

def init_browser(proxy = None):
    
    # Headless Chrome
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument("--no-sandbox")

    # User-Agent-Header setzen
    # chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.102 Safari/537.36")
    chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:115.0) Gecko/20100101 Firefox/115.0")

    # use proxy
    if proxy:
        chrome_options.add_argument(f"--proxy-server={proxy}")

    service = Service(ChromeDriverManager().install())
    browser = webdriver.Chrome(service=service, options=chrome_options)

    return browser






#
# get 1x2 odds for next football
# matches
#

def oddsportal_football_next_matches_1x2_odds(country = 'germany', division = 'bundesliga', proxy = None):

    # 
    # open default page of oddsportal and get all matches url
    # for 1x2 odds, the average odds are already included
    #

    # open url
    browser = init_browser(proxy)

    v_url = f"https://www.oddsportal.com/football/{country}/{division}/"

    browser.get(v_url)

    with open("oddsportal_debug_{country}.html", "w", encoding="utf-8") as f:
        f.write(browser.page_source)

    browser.save_screenshot("oddsportal_debug_{country}.png")   

    #collect data
    match_elements = browser.find_elements(By.CSS_SELECTOR, "div.border-b.border-l.border-r")

    match_data = []

    for match in match_elements:
        try:
            teams = match.find_elements(By.CSS_SELECTOR, "p.participant-name")
            odds = match.find_elements(By.CSS_SELECTOR, "div[data-testid='add-to-coupon-button'] p")

            if len(teams) == 2 and len(odds) == 3:
                match_data.append({
                    "country": country,
                    "division": division,
                    "team_home": teams[0].text.strip(),
                    "team_away": teams[1].text.strip(),
                    "avg_odds_home_win": odds[0].text.strip(),
                    "avg_odds_draw": odds[1].text.strip(),
                    "avg_odds_away_win": odds[2].text.strip()
                })
        except Exception as e:
            print(f"⚠️ Fehler bei Spiel-Element: {e}")
            continue
    
    # create data frame
    df_next_matches = pd.DataFrame(match_data)
    
    # close browser
    browser.quit()


    return df_next_matches



