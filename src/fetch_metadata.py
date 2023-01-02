''' Fetch game metadata Steam API '''

import pandas as pd
import os
import requests as re
import time
from tqdm import tqdm
import random

USER_PLAYTIME_PATH = 'data/steam_playtime.csv'
APP_METADATA_PATH = 'data/steam_app_metadata.csv'
BAD_APPS_PATH = 'data/bad_apps.csv'

# import our api key and steam id
steam_api_key = os.environ['STEAM_API']
steam_id = os.environ['STEAM_ID']

playtime_df = pd.read_csv(USER_PLAYTIME_PATH)

# make dataframe of unique appids from playtime_df
appid_df = pd.DataFrame(playtime_df['appid'].unique(), columns=['appid'])

# get game metadata. if it doesn't exist, create one
# with columns appid, name, description, developr, publisher, metascore, genres
if os.path.exists(APP_METADATA_PATH):
    app_df = pd.read_csv(APP_METADATA_PATH)
else:
    app_df = pd.DataFrame(columns = ['appid', 'name', 'description', 'developer', 'publisher', 'categories', 'genres'])

# list of appids that dont work out during parsing
if os.path.exists(BAD_APPS_PATH):
    badapps_df = pd.read_csv(BAD_APPS_PATH)
else:
    badapps_df = pd.DataFrame(columns= ['appid'])

# set up url and params for app data
app_url = 'https://store.steampowered.com/api/appdetails?appids='
app_url_params = {'key': steam_api_key, 'format': 'json'}

# loop for getting game metadata, takes over a day
# time.sleep(4) did not give me any 429's. Maybe even 3 seconds would work?
for appid in tqdm(appid_df['appid']):
    appid = str(appid)
    req_url = app_url + appid
    # check if appid already in app_df
    if int(appid) not in app_df['appid'].values and int(appid) not in badapps_df['appid'].values:
        url_request = re.get(req_url, params=app_url_params)
        time.sleep(4)
        # if status_code is not 200, return
        if url_request.status_code != 200:
            print(url_request.status_code, end=" ")
        else:
            req_json = url_request.json()
            if req_json[appid]['success'] == True:
                # get metadata for this app
                name = req_json[appid]['data']['name']
                description = req_json[appid]['data']['detailed_description']
                # get developer if it exists
                if 'developers' in req_json[appid]['data']:
                    developer = req_json[appid]['data']['developers'][0]
                else:
                    developer = 'None'
                publisher = req_json[appid]['data']['publishers'][0]
                # loop through categories
                categories = []
                if 'categories' in req_json[appid]['data']:
                    for category in req_json[appid]['data']['categories']:
                        categories.append(category['description'])
                # loop through genres
                genres = []
                if 'genres' in req_json[appid]['data']:
                    for genre in req_json[appid]['data']['genres']:
                        genres.append(genre['description'])
                # append to dataframe
                app_df = app_df.append({'appid': int(appid),
                                        'name': name,
                                        'description': description,
                                        'developer': developer,
                                        'publisher': publisher,
                                        'categories': categories,
                                        'genres': genres},
                                        ignore_index=True)
            else:
                # add to badapps_df list
                badapps_df = badapps_df.append({'appid': int(appid)}, ignore_index=True)

# save app_df to csv
app_df.to_csv('data/steam_app_metadata.csv', index=False)