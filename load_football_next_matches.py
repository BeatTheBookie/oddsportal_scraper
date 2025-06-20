import json
import pandas as pd
import boto3
import io
import re
from datetime import datetime
from oddsportal_scraper import *  # load oddsportal scrapper

# for env variables
from dotenv import load_dotenv
import os

load_dotenv()


AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
AWS_REGION = os.getenv("AWS_REGION")


# AWS S3 Pfad

S3_BUCKET = 'btb-raw-layer'
S3_BASE_PATH = 'oddsportal/current_odds/1x2/'

# S3 Client erstellen mit expliziter Authentifizierung
s3_client = boto3.client(
    's3',
    aws_access_key_id=AWS_ACCESS_KEY_ID,
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
    region_name=AWS_REGION
)


# Hilfsfunktion zum "Säubern" von Text für Dateinamen
def clean_filename(text):
    return re.sub(r'\W+', '_', text.strip().lower())

#read config file
with open(r'C:\Users\andre\OneDrive\betting_db\050_repos\oddsportal_scraper\football_next_matches.config', 'r') as f:
#with open('football_next_matches.config', 'r') as f:
    config_data = json.load(f)

    for element in config_data:
        print("Executing configuration:", element)

        # get configuration
        v_country = element['country']
        v_league = element['league']

        # scrape odds
        df_next_matches_1x2_odds = oddsportal_football_next_matches_1x2_odds(v_country, v_league)

        # add load timestamp
        df_next_matches_1x2_odds['load_ts'] = datetime.datetime.utcnow().isoformat()

        #print(df_next_matches_1x2_odds)

        # prepare filename
        clean_country = clean_filename(v_country)
        clean_league = clean_filename(v_league)
        file_name = f"{clean_country}_{clean_league}.json"
        s3_key = f"{S3_BASE_PATH}{file_name}"

        # convert DataFrame to JSON string
        json_buffer = io.StringIO()
        df_next_matches_1x2_odds.to_json(json_buffer, orient="records", lines=True)

        # upload to S3
        s3_client.put_object(Bucket=S3_BUCKET, Key=s3_key, Body=json_buffer.getvalue())

        print(f"✅ Uploaded {file_name} to s3://{S3_BUCKET}/{s3_key}")