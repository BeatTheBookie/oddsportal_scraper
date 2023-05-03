import json
from oddsportal_scraper import *


#read config file, which has to be in the same dircetory
with open('football_historic_matches.config', 'r') as f:
    config_data = json.load(f)

    for element in config_data:
        
        print("Executing following configuration: ", element)

        #get configuration for the single element
        v_country = element['country']
        v_league = element['league']
        v_season = element['season']
        v_csv_path = element['csv-path']

        #
        # export 1x2 odds for the next matches
        #

        df_historic_matches_1x2_odds = oddsportal_football_hist_matches_1x2_odds(v_country,v_league,v_season)

        df_historic_matches_1x2_odds.to_csv(v_csv_path, sep=';', index=False)
