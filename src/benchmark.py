''' 
Benchmark from https://gist.github.com/susanli2016/e0cdcf1bca69a2b144fd8c04f30b522f#file-benchmark-py
It appeared in https://towardsdatascience.com/building-and-testing-recommender-systems-with-surprise-step-by-step-d4ba702ef80b
'''
# import libraries
import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.preprocessing import RobustScaler
from surprise import Reader, Dataset
from surprise.model_selection import cross_validate

# import our processed datasets
users_df = pd.read_csv('data/steam_playtime_clean.csv')

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

# import surprise algos for benchmark
from surprise import SVD, SlopeOne, SVDpp, KNNBasic, KNNBaseline, NormalPredictor, KNNWithMeans, KNNWithZScore, BaselineOnly, CoClustering

benchmark = []
# Iterate over all algorithms
for algorithm in [SVD(), SVDpp(), SlopeOne(), NormalPredictor(), KNNBaseline(), KNNBasic(), KNNWithMeans(), KNNWithZScore(), BaselineOnly(), CoClustering()]:
    # Perform cross validation
    results = cross_validate(algorithm, data, measures=['RMSE'], cv=3, verbose=False)
    
    # Get results & append algorithm name
    tmp = pd.DataFrame.from_dict(results).mean(axis=0)
    tmp = tmp.append(pd.Series([str(algorithm).split(' ')[0].split('.')[-1]], index=['Algorithm']))
    benchmark.append(tmp)
    
pd.DataFrame(benchmark).set_index('Algorithm').sort_values('test_rmse')    