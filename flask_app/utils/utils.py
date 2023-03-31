import pandas as pd
import pickle
from os import path

SITE_ROOT = path.realpath(path.dirname(__file__))

# get games info
games_df = pd.read_csv(path.join(SITE_ROOT, 'steam_metadata_flask.csv'))

weighted_sim = pickle.load(open(path.join(SITE_ROOT, 'weighted_sim_compressed.pkl'), 'rb'))

# Construct a reverse map of indices and game titles
indices = pd.Series(games_df.index, index=games_df['name'])

def get_game_description(title):
    return games_df[games_df['name'] == title]['description'].values[0]

def get_game_genres(title):
    return games_df[games_df['name'] == title]['genres'].values[0]

def get_game_categories(title):
    return games_df[games_df['name'] == title]['categories'].values[0]

def recommend_content(title, sim_matrix = weighted_sim):
    '''Get top 10 recommended games using
    
    Args:
        title (str): Game title
        sim_matrix (numpy.ndarray): Similarity matrix
        
    Returns:
        list: Top 10 recommended games
    '''
    # get index for our game
    try:
        idx = indices[title]
    except KeyError:
        return None
    
    # get pairwise similarity scores of all games w.r.t to our game
    sim_scores = list(enumerate(sim_matrix[idx]))
    
    # sort scores based on similarity
    sorted_sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)
    
    # create a list of dictionaries with title, description and score
    content_similar_games = [{'title': indices.index[i[0]],
                            'description': get_game_description(indices.index[i[0]]),
                            'genres': get_game_genres(indices.index[i[0]]),
                            'categories': get_game_categories(indices.index[i[0]]),
                            'score': i[1]} for i in sorted_sim_scores[1:11]]

    return content_similar_games
