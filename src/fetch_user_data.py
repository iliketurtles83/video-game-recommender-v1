''' Fetch user data using Steam API 
    DEPRECATED: after realizing that maintaining the 
    notebook files and python files creates too much overhead
    and the realization that data science python and regular python
    are two different animals, I decided to just use the notebooks. 
    That being said, it was a good practice in refactoring and cleaning code.
'''

from utils.utils import get_user_playtimes, get_userids_from_steamid_uk, friends_games
import pandas as pd
import os
from tqdm import tqdm
import time
import random

USER_PLAYTIME_PATH = '../data/steam_playtime.csv'

# import our api key and steam id
steam_api_key = os.environ['STEAM_API']
steam_id = os.environ['STEAM_ID']

# get playtime data. if it doesn't exist create it with columns appid, steam_id, playtime_2weeks, playtime_forever
if os.path.exists(USER_PLAYTIME_PATH):
    playtime_df = pd.read_csv(USER_PLAYTIME_PATH)
else:
    playtime_df = pd.DataFrame(columns = ['appid', 'steam_id', 'playtime_2weeks', 'playtime_forever'])

history = get_userids_from_steamid_uk()

# loop through data and get user playtimes, takes less than a day :)
for someid in tqdm(history['someid']):
    # check if steam_id is not in our dataframe already
    if someid not in playtime_df['steam_id'].values:
        valid_playtimes = get_user_playtimes(someid)
        playtime_df = playtime_df.append(valid_playtimes, ignore_index=True)


# parse through my friends
friends_games(steam_id)

# create a list of unique steam_id's from user_playtimes
steamids = list(set(playtime_df['steam_id']))

# loop that picks a random steam_id from steamids and runs friends_games on it
print('getting random recursively')
for i in range(10):
    random_steamid = random.choice(steamids)
    playtime_df = playtime_df.append(friends_games(random_steamid))
    time.sleep(5)

# save data to csv
playtime_df.to_csv(USER_PLAYTIME_PATH, index=False)
