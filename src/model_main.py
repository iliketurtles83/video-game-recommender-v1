''' Video Game Recommendation System based on SteamSpy and Steam Datasets 
    - Uses a collaborative filtering approach to recommend games '''

# import libraries
import numpy as np
import pandas as pd
import pickle
from sklearn.preprocessing import StandardScaler
from sklearn.preprocessing import RobustScaler
from surprise import Reader, Dataset, KNNWithZScore, SVD
from surprise.model_selection import cross_validate
from surprise.model_selection import train_test_split
from surprise import accuracy
from surprise.model_selection import GridSearchCV
from sklearn.metrics.pairwise import cosine_similarity

# import our processed datasets
users_df = pd.read_csv('../data/steam_playtime_clean.csv')
games_df = pd.read_csv('../data/steam_app_metadata_clean.csv')
gamesinfo_df = pd.read_csv('../data/gameinfo.csv')


''' COLLABORATIVE FILTERING FOR USER PLAYTIME DATA '''
# first do robustscaler to minimize outliers
scaler = RobustScaler(with_centering=True, with_scaling=True, quantile_range=(25.0, 75.0), copy=True)
users_df['playtime_forever'] = scaler.fit_transform(users_df['playtime_forever'].array.reshape(-1,1))

# use StandardScaler to scale user playtimes
scaler = StandardScaler()
users_df['playtime_forever'] = scaler.fit_transform(users_df['playtime_forever'].values.reshape(-1, 1))

# instantiate surprise.Reader()
reader = Reader()

# make surprise dataset
data = Dataset.load_from_df(users_df[['steam_id', 'appid', 'playtime_forever']], reader)

# make a training and test set
trainset, testset = train_test_split(data, test_size=0.25)

''' KNN WITH ZSCORE '''

# set up gridsearch param_grid for KNNWithZScore
knn_param_grid = {'k': [5, 10, 20, 50, 100]}

# do gridsearch for knn
grid_search = GridSearchCV(KNNWithZScore, knn_param_grid, cv=5)

grid_search.fit(trainset)

# print best params for grid search
print('Best params: ', grid_search.best_params)

# print best score for grid search
print('Score: ', grid_search.best_score_)

# make knn model with best params from gridsearch
knn = KNNWithZScore(k=300, sim_options={'name': 'pearson_baseline', 'user_based': False})

# fit the training data and test with our test set
predictions = knn.fit(trainset).test(testset)

# get accuracy
accuracy.rmse(predictions)

# build a full trainset now
trainset = data.build_full_trainset()

# instantiate new knn
knn = KNNWithZScore(k=300, sim_options={'name': 'pearson_baseline', 'user_based': False})

# fit the knn
knn.fit(trainset)

# save model in pickle
pickle.dump(knn, open('../models/knn_model.pkl', 'wb'))

# function that takes game title and returns the inner id
def get_appid(title):
    steam_id = gamesinfo_df[gamesinfo_df['name'] == title].iloc[0]['appid']
    inner_id = trainset.to_inner_iid(steam_id)
    return inner_id

# function that takes innerid and returns the game title
def get_title(appid):
    steam_id = trainset.to_raw_iid(appid)
    title = gamesinfo_df[gamesinfo_df['appid'] == steam_id].iloc[0]['name']
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
    # return titles
    return titles


''' CONTENT-BASED FILTERING FOR GAME DATA '''

# make a matrix out of games_df without the appid column
matrix = games_df.drop(['appid'], axis=1).as_matrix()

# make a cosine similarity matrix
cosine_sim = cosine_similarity(matrix, matrix)

# Construct a reverse map of indices and game titles
indices = pd.Series(games_df.index, index=games_df['name'])

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
    return gamesinfo_df['name'].iloc[game_indices]


# function that takes a game title and returns
def combined_recom(title):
    # get recommended games from knn
    knn_recom = recommend_knn(title)
    # get recommended games from content based
    cont_recom = recommend_content(title)
    # print knn_recom
    print('Best games based on user data:')
    print(knn_recom)
    print('Best games based on game data:')
    print(cont_recom)
