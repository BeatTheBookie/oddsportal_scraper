
import time
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import numpy as np
import pandas as pd
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager





#
# function for general browser configuration
#

def init_browser():
    
    # Add the "--headless" option to ChromeOptions
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument('--window-size=1024,768')

    browser = webdriver.Chrome(executable_path=ChromeDriverManager().install(), chrome_options=chrome_options)

    return browser



#
# function to provide the list of
# match urls for next matches
#

def oddsportal_football_next_matches_list(country = 'germany', division = 'bundesliga'):

    #variables
    next_match_list=[]

    #create url for current fixtures
    v_url = 'https://www.oddsportal.com/football/{}/{}/'.format(country,division)

    print('Scraping next matches from ',v_url)    

    try:
        browser.quit() # close all widows
    except:
        pass

    print('...downloading webdriver (if not yet happened)')
    browser = init_browser()
    browser.get(v_url)

    print('...waiting 4 seconds')
    time.sleep(4)

    #get links to single matches
    print('...getting links of single matches')
    v_match_items = browser.find_elements(By.CLASS_NAME,"mobile-next-matches")

    for match_item in v_match_items:

        #get url of match
        match_url = match_item.get_attribute('href')
            
        next_match_list.append([match_url])

    browser.quit()

    return next_match_list



#
# function to provide the list of
# match urls for historic matches of the given season
#

def oddsportal_football_hist_matches_list(country = 'germany', division = 'bundesliga', season = '2022-2023'):

    #variables
    his_match_list=[]

    #check if current season or past season
    #as the url is different

    current_year = datetime.now().year
    season_years = season.split('-')

    if (season_years[0] == str(current_year) or season_years[1] == str(current_year)):
        print(f"{season} is the current season.")

        #create url for historic fixtures
        v_base_url = 'https://www.oddsportal.com/football/{}/{}/results/'.format(country,division)
        print('...scraping historic match list from:',v_base_url)
    else:
        print(f"{season} is not the current season.")

        #create url for historic fixtures
        v_base_url = 'https://www.oddsportal.com/football/{}/{}-{}/results/'.format(country,division,season)
        print('...scraping historic match list from:',v_base_url)

    #determin the number of pages for the given
    #country, league and season in the base-url
    print('...determine number of pages')

    try:
        browser.quit() # close all widows
    except:
        pass
    
    #call 1x2 website
    browser = init_browser()
    browser.get(v_base_url)

    print('...waiting 4 seconds')
    time.sleep(4)

    i_num_pages = 2
    loop = True

    # each page starting at 2 has a follwing xpath //*[@id="pagination"]/a[1]
    # counting starts at page 2, page 1 has another xpath
    while (loop == True):
        v_xpath = '//*[@id="pagination"]/a[{}]'.format(str(i_num_pages - 1))
        #print(v_xpath)
        try:
            page_element = browser.find_element(By.XPATH,v_xpath)
            print(page_element,v_xpath)
        except:
            print("...no more pages found")
            break

        i_num_pages = i_num_pages + 1
    
    print('...determined {} number of pages'.format(i_num_pages-1))

    
    # 
    #loop over number of pages and extract match list
    #    
    for v_page in range(1,i_num_pages):
        
        i_num_matches = 0

        v_url = v_base_url + '#/page/{}/'.format(v_page)

        print('...scraping historic matches from ',v_url)   

        try:
            browser.quit() # close all widows
        except:
            pass

        # start browser and get match list
        browser = init_browser()
        browser.get(v_url)

        print('...waiting 4 seconds and after that scrolling 10 times to load data')
        time.sleep(4)

        # Scroll 3 time to get all matches
        for i in range(10):

            #print('scrolling and wating 1s')

            # Scroll down to the bottom of the page
            browser.execute_script("window.scrollTo(0, document.body.scrollHeight);")

            # Wait for the page to load
            time.sleep(1)            


        #get table with all matches    
        v_match_table = browser.find_element(By.XPATH, '//*[@id="app"]/div/div[1]/div/main/div[2]/div[5]')

        v_match_items = v_match_table.find_elements(By.CLASS_NAME,"mobile-next-matches")

        for match_item in v_match_items:

            i_num_matches =  i_num_matches + 1

            #get url of match
            match_url = match_item.get_attribute('href')
                
            his_match_list.append([match_url])

        # sometimes not all matches of a page are loaded
        # each page should have 50 matches, as long it's not the last page
        # so a warning is printed, if it's not the last page and less
        # than 50 matches were found
        print('found {} matches on page {}'.format(i_num_matches,v_page))

        if (v_page != (i_num_pages - 1) and i_num_matches < 50):
            print('WARNING: less than 50 matches found for page {}. Matches might be missing.'.format(v_page))
            

        browser.quit()
    

        
    #close browser
    try:
        print('browser quit')
        #browser.quit() # close all widows
    except:
        pass
    

    return his_match_list



#
# function to get the 1x2 odds for a single match url
# match page is same for next and historic matches
#

def oddsportal_football_match_url_1x2_odds(match_url):

    lst_data = []

    #build 1x2 url
    v_match_1x2_url = match_url[0] + "#1X2"

    print('Scraping 1x2 odds from ', v_match_1x2_url)

    try:
        browser.quit() # close all widows
    except:
        pass
        
    #call 1x2 website
    browser = init_browser()
    browser.get(v_match_1x2_url)

    print('...waiting 4 seconds')
    time.sleep(4)

    #get match date and extract datetime
    match_date_str = browser.find_element(By.XPATH, '//*[@id="app"]/div/div[1]/div/main/div[2]/div[3]/div[2]/div[1]/div[2]').text
    #in case "today" or "tomorrow" are part of the string
    if "Tomorrow" in match_date_str:
        # Tomorrow, 14 Apr 2023, 20:30
        #match_date_str = match_date_str.replace("Tomorrow, ","")
        match_date_dt = datetime.strptime(match_date_str, "Tomorrow, %d %b %Y, %H:%M")
    elif "Today" in match_date_str:
        # Today, 14 Apr 2023, 20:30
        #match_date_str = match_date_str.replace("Today, ","")
        match_date_dt = datetime.strptime(match_date_str, "Today, %d %b %Y, %H:%M")
    elif "Yesterday" in match_date_str:
        # Today, 14 Apr 2023, 20:30
        #match_date_str = match_date_str.replace("Today, ","")
        match_date_dt = datetime.strptime(match_date_str, "Yesterday, %d %b %Y, %H:%M")
    else:
        # Sunday, 16 Apr 2023, 15:30
        match_date_dt = datetime.strptime(match_date_str, "%A, %d %b %Y, %H:%M")

    #print("match_date_dt",match_date_dt)

    #get home team and away team
    home_team = browser.find_element(By.XPATH, '//*[@id="app"]/div/div[1]/div/main/div[2]/div[3]/div[1]/div[1]/div/div[1]/p').text
    away_team = browser.find_element(By.XPATH, '//*[@id="app"]/div/div[1]/div/main/div[2]/div[3]/div[1]/div[3]/div[1]/p').text
    
    #print("home_team",home_team)
    #print("away_team",away_team)

    #get elements with bookies and loop over rows
    # -> iterator to go through xpath
    v_bookie_iterator = 2
    
    while v_bookie_iterator > 0:

        #print('v_bookie_iterator',v_bookie_iterator)
        
        #build xpath values to get
        #the different values for each bookie
        v_line_xpath = '//*[@id="app"]/div/div[1]/div/main/div[2]/div[4]/div[1]/div/div[' + str(v_bookie_iterator) + ']'
        v_home_odd_xpath = '//*[@id="app"]/div/div[1]/div/main/div[2]/div[4]/div[1]/div/div[' + str(v_bookie_iterator) + ']/div[2]/div/div'
        v_draw_odd_xpath = '//*[@id="app"]/div/div[1]/div/main/div[2]/div[4]/div[1]/div/div[' + str(v_bookie_iterator) + ']/div[3]/div/div'
        v_away_odd_xpath = '//*[@id="app"]/div/div[1]/div/main/div[2]/div[4]/div[1]/div/div[' + str(v_bookie_iterator) + ']/div[4]/div/div'
        v_tooltip_box_xpath = '//*[@id="app"]/div/div[1]/div/main/div[2]/div[4]/div[1]/div/div[2]'

        bookie_line = browser.find_element(By.XPATH, v_line_xpath)

        #try to get bookie name
        #if it's not possible, it's the end of the list
        try:
            bookie_name = bookie_line.find_element(By.TAG_NAME,'img').get_attribute('title')
            home_odd = browser.find_element(By.XPATH, v_home_odd_xpath).text
            draw_odd = browser.find_element(By.XPATH, v_draw_odd_xpath).text
            away_odd = browser.find_element(By.XPATH, v_away_odd_xpath).text

            #print('bookie_name',bookie_name)
            #print('home_odd',home_odd)
            #print('draw_odd',draw_odd)
            #print('away_odd',away_odd)

            lst_data.append([match_date_dt, home_team, away_team, bookie_name, home_odd, draw_odd, away_odd])

# tooltip with odd movement currently not yet working
#                data = browser.find_element(By.XPATH, v_home_odd_xpath)
#                hov = ActionChains(browser).move_to_element(data).click()
#                hov.perform()
#                
#                #loop over home-odds
#                v_odd_iterator = 1
#
#                while v_odd_iterator > 0:
#                    print('v_odd_iterator',v_odd_iterator)
#                    
#
#                    v_odd_date_xpath = '//*[@id="app"]/div/div[1]/div/main/div[2]/div[4]/div[1]/div/div[2]/div[2]/div/div/div[1]/div[' + str(v_odd_iterator) + ']'
#                    v_odd_value_xpath = '//*[@id="app"]/div/div[1]/div/main/div[2]/div[4]/div[1]/div/div[2]/div[2]/div/div/div[2]/div[' + str(v_odd_iterator) + ']'
#
#                    try:
#
#                        odd_date = browser.find_element(By.XPATH, v_odd_date_xpath).text
#                        odd_value = browser.find_element(By.XPATH, v_odd_value_xpath).text
#
#                        print('odd_date',odd_date)
#                        print('odd_value',odd_value)
#
#                        v_odd_iterator = v_odd_iterator + 1
#
#                    except:
#                        #element not found -> end loop
#                        print('tool tip loop break')
#                        break                      

            v_bookie_iterator = v_bookie_iterator + 1

        except:
            #element not found -> end loop
            break

    #close browser
    try:
        print('browser quit')
        #browser.quit() # close all widows
    except:
        pass

    return lst_data



#
# get 1x2 odds for next football
# matches
#

def oddsportal_football_next_matches_1x2_odds(country = 'germany', division = 'bundesliga'):

    lst_data = []

    #get url list for next matches and
    #loop over all matches
    df_match_list = oddsportal_football_next_matches_list(country, division)

    for match_url in df_match_list:
        
        # get 1x2 odds from each match url
        lst_data.append(oddsportal_football_match_url_1x2_odds(match_url))        


    # transform list to data frame
    df_data = pd.DataFrame(lst_data, columns=['match_date', 'home_team', 'away_team','bookie_name','home_odd','draw_odd','away_odd'])


    return df_data



#
# get 1x2 odds for historic football
# matches
#

def oddsportal_football_hist_matches_1x2_odds(country = 'germany', division = 'bundesliga', season = '2023-2022'):

    lst_data = []

    #get url list for next matches and
    #loop over all matches
    df_match_list = oddsportal_football_hist_matches_list(country, division,season)

    print('num matches list:',len(df_match_list))

    for match_url in df_match_list:
            
        # get 1x2 odds from each match url
        lst_data.extend(oddsportal_football_match_url_1x2_odds(match_url))        

    # transform list to data frame
    df_data = pd.DataFrame(lst_data, columns=['match_date', 'home_team', 'away_team','bookie_name','home_odd','draw_odd','away_odd'])


    return df_data