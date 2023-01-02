
import os
import time
import pandas as pd
import requests as re

# import our api key and steam id
STEAM_API_KEY = os.environ['STEAM_API']
HOST_STEAM_ID = os.environ['STEAM_ID']

GET_OWNED_GAMES_URL = 'http://api.steampowered.com/IPlayerService/GetOwnedGames/v0001/'
GET_OWNED_REQUEST_PARAMS = {
    'key': STEAM_API_KEY, 
    'steamid': HOST_STEAM_ID, 
    'format': 'json'
    }
GET_FRIENDLIST_URL = 'http://api.steampowered.com/ISteamUser/GetFriendList/v0001/'
USER_PLAYTIME_PATH = '../data/steam_playtime.csv'

# get playtime data. if it doesn't exist create it with columns appid, steam_id, playtime_2weeks, playtime_forever
if os.path.exists(USER_PLAYTIME_PATH):
    playtime_df = pd.read_csv(USER_PLAYTIME_PATH)
else:
    playtime_df = pd.DataFrame(columns = ['appid', 'steam_id', 'playtime_2weeks', 'playtime_forever'])


def get_userids_from_steamid_uk() -> pd.DataFrame:
    ''' 
    parse the csv files from https://steamid.uk/downloads/
    and return a dataframe with all the userids 
    :return: dataframe with unique userids from steamid.uk
    '''
    # read in the csv files
    source1 = 'https://steamid.uk/downloads/3digitURLhistory04_06_2019.csv'
    source2 = 'https://steamid.uk/downloads/3digitURLhistory16_04_2019.csv'
    source3 = 'https://steamid.uk/downloads/3digitURLhistory18_01_2020.csv'
    source4 = 'https://steamid.uk/downloads/3digitURLhistory18_03_2019.csv'
    source5 = 'https://steamid.uk/downloads/3digitURLhistory26_02_2019.csv'

    # make csv to dataframes
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

    # return unique ids
    return history.drop_duplicates()

def parse_playtime_json(steamid, json_data) -> list:
    ''' Get games from the json data and return a list of dicts '''
    user_playtimes = [] 
    # parse req_json fields for games user has played
    for game in json_data['response']['games']:
        if game['playtime_forever'] > 0:
            appid = game['appid']
            playtime_forever = game['playtime_forever']
            # if key playtime_2weeks exists
            if 'playtime_2weeks' in game:
                playtime_2weeks = game['playtime_2weeks']
            else:
                playtime_2weeks = 0
            user_playtimes.append({'appid': appid, 
                                    'steam_id': steamid, 
                                    'playtime_2weeks': playtime_2weeks, 
                                    'playtime_forever': playtime_forever})
    return user_playtimes


def get_user_playtimes(steamid) -> list[dict]:
    ''' function to get steam users playtime data '''
    # if steamid is in playtime_df, return empty list
    if steamid in playtime_df['steam_id'].values:
        return []

    url_params = {'key': STEAM_API_KEY, 'steamid': steamid, 'format': 'json'}
    url_request = re.get(GET_OWNED_GAMES_URL, params=url_params)
    time.sleep(1)

    if url_request.status_code != 200:
        print(url_request.status_code, end=" ")
        return []
    else:
        request_json_data = url_request.json()
        if 'games' in request_json_data['response']:
            print('g', end='')
            user_playtimes = parse_playtime_json(steamid, request_json_data)
            return user_playtimes
        else:
            return []


def friends_games(steamid, depth = 0) -> list[dict]:
    ''' Get friends steam id's recursively, depth set to 6 '''
    if depth == 2:
        return []
    time.sleep(4)

    # getting game data for this friend
    user_playtime = get_user_playtimes(steamid)    

    # get friends list for this friend
    getfriendparams = {'key': STEAM_API_KEY, 'steamid': steamid, 'relationship': 'all', 'format': 'json'}
    url_request = re.get(GET_FRIENDLIST_URL, params=getfriendparams)
    time.sleep(1)
    # if status_code is not 200, return
    if url_request.status_code != 200:
        print(url_request.status_code, end=" ")
    else:
        req_json = url_request.json()
        if 'friendslist' in req_json:
            for friend in req_json['friendslist']['friends']:
                friendsteamid = friend['steamid']
                # run friends_games on this friend
                friend_data = friends_games(friendsteamid, depth+1)
                if friend_data:
                    user_playtime.extend(friend_data)
    return user_playtime