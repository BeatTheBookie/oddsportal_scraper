
import time
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import numpy as np
import pandas as pd
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager



#define browser + close possible open windows
global browser



#
# function to provide the list of
# match urls for next matches
#

def oddsportal_football_next_matches_list(country = 'germany', division = 'bundesliga'):

    #variables
    df_next_match_list=[]

    #create url for current fixtures
    v_url = 'https://www.oddsportal.com/football/{}/{}/'.format(country,division)

    print('Scraping next matches from ',v_url)    

    try:
        browser.quit() # close all widows
    except:
        pass

    print('...downloading webdriver (if not yet happened)')
    browser = webdriver.Chrome(executable_path=ChromeDriverManager().install())
    browser.get(v_url)

    print('...waiting 4 seconds')
    time.sleep(4)

    #get links to single matches
    print('...getting links of single matches')
    v_match_items = browser.find_elements_by_class_name("mobile-next-matches")

    for match_item in v_match_items:

        #get url of match
        match_url = match_item.get_attribute('href')
            
        df_next_match_list.append([match_url])

    browser.quit()

    return df_next_match_list


#
# get 1x2 odds for next football
# matches
#

def oddsportal_football_next_matches_1x2_odds(country = 'germany', division = 'bundesliga'):

    df_data = []

    #get url list for next matches and
    #loop over all matches
    df_match_list = oddsportal_football_next_matches_list(country, division)

    for match_url in df_match_list:
        
        #build 1x2 url
        v_match_1x2_url = match_url[0] + "#1X2"

        print('Scraping 1x2 odds from ', v_match_1x2_url)

        try:
            browser.quit() # close all widows
        except:
            pass
        
        #call 1x2 website
        browser = webdriver.Chrome(executable_path=ChromeDriverManager().install())
        browser.get(v_match_1x2_url)

        print('...waiting 4 seconds')
        time.sleep(4)

        #get match date and extract datetime
        match_date_str = browser.find_element(By.XPATH, '//*[@id="app"]/div/div[1]/div/main/div[2]/div[3]/div[2]/div[1]/div[2]').text
        match_date_dt = datetime.strptime(match_date_str, "%A, %d %b %Y, %H:%M")

        print("match_date_dt",match_date_dt)

        #get home team and away team
        home_team = browser.find_element(By.XPATH, '//*[@id="app"]/div/div[1]/div/main/div[2]/div[3]/div[1]/div[1]/div/div[1]/p').text
        away_team = browser.find_element(By.XPATH, '//*[@id="app"]/div/div[1]/div/main/div[2]/div[3]/div[1]/div[3]/div[1]/p').text
        
        print("home_team",home_team)
        print("away_team",away_team)

        #get elements with bookies and loop over rows
        # -> iterator to go through xpath
        v_bookie_iterator = 2
        
        while v_bookie_iterator > 0:

            print('v_bookie_iterator',v_bookie_iterator)
            
            #build xpath values to get
            #the different values for each bookie
            v_line_xpath = '//*[@id="app"]/div/div[1]/div/main/div[2]/div[4]/div[1]/div/div[' + str(v_bookie_iterator) + ']'
            v_home_odd_xpath = '//*[@id="app"]/div/div[1]/div/main/div[2]/div[4]/div[1]/div/div[' + str(v_bookie_iterator) + ']/div[2]/div/div/p'
            v_draw_odd_xpath = '//*[@id="app"]/div/div[1]/div/main/div[2]/div[4]/div[1]/div/div[' + str(v_bookie_iterator) + ']/div[3]/div/div/p'
            v_away_odd_xpath = '//*[@id="app"]/div/div[1]/div/main/div[2]/div[4]/div[1]/div/div[' + str(v_bookie_iterator) + ']/div[4]/div/div/p'
            v_tooltip_box_xpath = '//*[@id="app"]/div/div[1]/div/main/div[2]/div[4]/div[1]/div/div[2]'

            bookie_line = browser.find_element(By.XPATH, v_line_xpath)

            #try to get bookie name
            #if it's not possible, it's the end of the list
            try:
                bookie_name = bookie_line.find_element(By.TAG_NAME,'img').get_attribute('title')
                home_odd = browser.find_element(By.XPATH, v_home_odd_xpath).text
                draw_odd = browser.find_element(By.XPATH, v_draw_odd_xpath).text
                away_odd = browser.find_element(By.XPATH, v_away_odd_xpath).text

                print('bookie_name',bookie_name)
                print('home_odd',home_odd)
                print('draw_odd',draw_odd)
                print('away_odd',away_odd)

                data = browser.find_element(By.XPATH, v_home_odd_xpath)
                hov = ActionChains(browser).move_to_element(data).click()
                hov.perform()

                #action to open tool tips for odds
                #actions = ActionChains(browser)

                # hover tool tip for home odds
                #actions.move_to_element(browser.find_element(By.XPATH, v_home_odd_xpath)).click().perform()

                #loop over home-odds
                v_odd_iterator = 1

                while v_odd_iterator > 0:
                    
                    print('v_odd_iterator',v_odd_iterator)

                    v_odd_date_xpath = '//*[@id="app"]/div/div[1]/div/main/div[2]/div[4]/div[1]/div/div[2]/div[2]/div/div/div[1]/div[' + str(v_odd_iterator) + ']'
                    v_odd_value_xpath = '//*[@id="app"]/div/div[1]/div/main/div[2]/div[4]/div[1]/div/div[2]/div[2]/div/div/div[2]/div[' + str(v_odd_iterator) + ']'

                    try:

                        odd_date = browser.find_element(By.XPATH, v_odd_date_xpath).text
                        odd_value = browser.find_element(By.XPATH, v_odd_value_xpath).text

                        print('odd_date',odd_date)
                        print('odd_value',odd_value)

                        v_odd_iterator = v_odd_iterator + 1

                    except:
                        #element not found -> end loop
                        print('tool tip loop break')
                        break                      

                v_bookie_iterator = v_bookie_iterator + 1

            except:
                #element not found -> end loop
                break
        
                
        print('bookmakers read')


        #df_data.append([match_date_str])

        break 


    #close browser
    try:
        print('browser quit')
        #browser.quit() # close all widows
    except:
        pass

    return df_data