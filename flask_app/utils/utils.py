import pandas as pd
import pickle
from os import path

SITE_ROOT = path.realpath(path.dirname(__file__))

# get games info
games_df = pd.read_csv(path.join(SITE_ROOT, '../../data/steam_app_metadata.csv'))

# load pickle knn model
knn = pickle.load(open(path.join(SITE_ROOT, '../../models/knn_model.pkl'), 'rb'))

# load trainset
trainset = pickle.load(open(path.join(SITE_ROOT, '../../models/trainset.pkl'), 'rb'))

# load pickle cosine similarity model
cosine_sim = pickle.load(open(path.join(SITE_ROOT, '../../models/cosine_sim.pkl'), 'rb'))

# Construct a reverse map of indices and game titles
indices = pd.Series(games_df.index, index=games_df['name'])

# function that takes game title and returns the inner id
def get_appid(title):
    steam_id = games_df[games_df['name'] == title].iloc[0]['appid']
    inner_id = trainset.to_inner_iid(steam_id)
    return inner_id

# function that takes innerid and returns the game title
def get_title(appid):
    steam_id = trainset.to_raw_iid(appid)
    title = games_df[games_df['appid'] == steam_id].iloc[0]['name']
    return title

# function that takes a game title and returns 10 nearest neighbours
def recommend_knn(title):
    '''Get top 10 recommended games for a user based on KNN
    
    Args:
        title (str): Game title
        
    Returns:
        list: Top 10 recommended games
    '''
    # get inner id for game
    inner_id = get_appid(title)
    # get nearest neighbours
    neighbors = knn.get_neighbors(inner_id, k=10)
    # get game titles for those neighbours
    titles = [get_title(i) for i in neighbors]
    return titles

def recommend_content(title, cosine_sim = cosine_sim):
    '''Get top 10 recommended games using content-based filtering
    
    Args:
        title (str): Game title
        
    Returns:
        list: Top 10 recommended games
    '''
    # get index for our movie
    idx = indices[title]
    
    # get pairwise similarity scores of all movies w.r.t to our movie
    sim_scores = list(enumerate(cosine_sim[idx]))
    
    # sort scores based on similarity
    sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)
    
    # get scores for 10 similar movies, not including the game itself
    sim_scores = sim_scores[1:11]
    
    # get the game indices
    game_indices = [i[0] for i in sim_scores]
    
    # return the titles
    return games_df['name'].iloc[game_indices].tolist()

# function that takes a game title and returns top 10 for both
def combined_recom(title):
    if title not in games_df['name'].values:
        return None
    else:
        # get recommended games from knn
        knn_recom = recommend_knn(title)
        # get recommended games from content based
        cont_recom = recommend_content(title)
        
        return knn_recom, cont_recom