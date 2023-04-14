
#
# export 1x2 odds for the next matches
#


from oddsportal_scraper import *

v_csv_path = 'c:/temp/export_test.csv'

df_next_matches_1x2_odds = oddsportal_football_next_matches_1x2_odds('germany','bundesliga')

#print(df_next_matches_1x2_odds)

df_next_matches_1x2_odds.to_csv(v_csv_path, sep=';', index=False)
