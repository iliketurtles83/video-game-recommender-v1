''' Steam API requests to collect metadata for our datasets '''

# import libraries
import pandas as pd
import os
import requests as re
import time
from tqdm import tqdm
import random

# import our api key and steam id
steam_api_key = os.environ['STEAM_API']
steam_id = os.environ['STEAM_ID']

''' USER PLAYTIME DATA '''
# create our playtime dataframe with columns appid, steam_id, playtime_2weeks, playtime_forever
playtime_df = pd.DataFrame(columns = ['appid', 'steam_id', 'playtime_2weeks', 'playtime_forever'])

# set up url
owned_url = 'http://api.steampowered.com/IPlayerService/GetOwnedGames/v0001/'
ownedparams = {'key': steam_api_key, 'steamid': steam_id, 'format': 'json'}

# function to get steam users playtime data 
def user_playtimes(steamid):
    # global playtime_df
    global playtime_df
    # check if we parsed this one, i.e. steam_id is not in our dataframe steam_id column
    if steamid not in playtime_df['steam_id'].values:
        urlparams = {'key': steam_api_key, 'steamid': steamid, 'format': 'json'}
        url_request = re.get(owned_url, params=urlparams)
        time.sleep(1)
        # if status_code is not 200, return
        if url_request.status_code != 200:
            print (url_request.status_code, end=" ")
            return
        else:
            req_json = url_request.json()
            if 'games' in req_json['response']:
                print ('p', end='') # p for parsing
                # parse req_json fields for games user has played
                for game in req_json['response']['games']:
                    if game['playtime_forever'] > 0:
                        appid = game['appid']
                        playtime_forever = game['playtime_forever']
                        # if key playtime_2weeks exists
                        if 'playtime_2weeks' in game:
                            playtime_2weeks = game['playtime_2weeks']
                        else:
                            playtime_2weeks = 0
                        # append to dataframe
                        playtime_df = playtime_df.append({'appid': appid, 
                                                          'steam_id': steamid, 
                                                          'playtime_2weeks': playtime_2weeks, 
                                                          'playtime_forever': playtime_forever},
                                                         ignore_index=True)
            else:
                return

# url for getting friend list steam id's
getfriendlist_url = 'http://api.steampowered.com/ISteamUser/GetFriendList/v0001/'
getfriendparams = {'key': steam_api_key, 'steamid': steam_id, 'relationship': 'friend', 'format': 'json'}

# function to get friends steam id's recursively, recursive depth set to 6
def friends_games(steamid, depth = 0):
    if depth == 6:
        return
    getfriendparams = {'key': steam_api_key, 'steamid': steamid, 'relationship': 'all', 'format': 'json'}
    url_request = re.get(getfriendlist_url, params=getfriendparams)
    time.sleep(1)
    # if status_code is not 200, return
    if url_request.status_code != 200:
        print(url_request.status_code, end=" ")
        return
    else:
        req_json = url_request.json()
        if 'friendslist' in req_json:
            for friend in req_json['friendslist']['friends']:
                steamid = friend['steamid']
                # get playtime data for this friend
                user_playtimes(steamid)
                # run friends_games on this friend
                friends_games(steamid, depth+1)
                time.sleep(2)
        else:
            return

# parse through my friends
friends_games(steam_id)

# parse the csv files from https://steamid.uk/downloads/
source1 = 'https://steamid.uk/downloads/3digitURLhistory04_06_2019.csv'
source2 = 'https://steamid.uk/downloads/3digitURLhistory16_04_2019.csv'
source3 = 'https://steamid.uk/downloads/3digitURLhistory18_01_2020.csv'
source4 = 'https://steamid.uk/downloads/3digitURLhistory18_03_2019.csv'
source5 = 'https://steamid.uk/downloads/3digitURLhistory26_02_2019.csv'
history1 = pd.read_csv(source1, header=None, usecols=[1], names=['someid'])
history2 = pd.read_csv(source2, header=None, usecols=[1], names=['someid'])
history3 = pd.read_csv(source3, header=None, usecols=[1], names=['someid'])
history4 = pd.read_csv(source4, header=None, usecols=[1], names=['someid'])
history5 = pd.read_csv(source5, header=None, usecols=[0], names=['someid'])

# append all the csv files together
history = history1
history = history.append(history2)
history = history.append(history3)
history = history.append(history4)
history = history.append(history5)

# remove duplicates
history = history.drop_duplicates()

# loop through data and get user playtimes
for someid in tqdm(history['someid']):
    user_playtimes(someid)


# create a list of unique steam_id's from user_playtimes, takes less than a day :)
steamids = list(set(playtime_df['steam_id']))

# loop that picks a random steam_id from steamids and runs friends_games on it
for i in range(10):
    random_steamid = random.choice(steamids)
    friends_games(random_steamid)
    time.sleep(5)

# save data to csv
playtime_df.to_csv('data/steam_playtime.csv', index=False)


''' GAME METADATA '''
# make dataframe of unique appids from playtime_df
appid_df = pd.DataFrame(playtime_df['appid'].unique(), columns=['appid'])

# create an app df with columns appid, name, description, developr, publisher, metascore, genres
app_df = pd.DataFrame(columns = ['appid', 'name', 'description', 'developer', 'publisher', 'categories', 'genres'])

# create list of appids that dont work out during parsing
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

# also store bad apps if we want to run the above loop again
badapps_df.to_csv('data/bad_apps.csv', index=False)

