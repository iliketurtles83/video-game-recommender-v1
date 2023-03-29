# Video Game Recommendation System using Steam data and Machine Learning

Too many games, not enough time! I love websites that recommend me stuff even if I dont always agree with their suggestions.
So for my final project at Lighthouse, I decided to make my own simple video game recommendation system based content-based and collaborative filtering using data from Steam.

## Roadmap
- [x] Ensemble model using KNNWithZscore and cosine similarity
- [x] Flask app
- [x] Hybrid model using the above methods
- [ ] SVDpp instead of KNNWithZscore
- [ ] Neural Network
- [ ] Flask app ready for deployment on the web

For now, both ipynb and py files uploaded. The notebook files should run fine but py files were for learning and testing purposes and have not been update for a while.

## [Notebooks](notebooks)

### [User Playtimes](notebooks/scrape_user_playtimes.ipynb) and [Metadata](notebooks/scrape_game_metadata.ipynb) Scraping
Using a set of Steam IDs from steamid.uk, I was able to get the user playtime data via Steam API. Steam made all profiles private by default in 2018 and thus only 20% of those IDs came back with data. Enter recursion. I grabbed some random IDs from the working ones and recursively checked these users' friends, friends of friends and so on (depth = 5 seemed ok). This gave me some additional playtimes. I would not recommend getting playtime data for users on the various Steam fan site toplists. There is a high chance they have ridiculous playtime hours due to in-game content farming (or something else fishy). Then for all the steam games the users had played, I also got the game metadata from Steam API.

### [Data Preparation](notebooks/data_preparation.ipynb)
Had to wrangle that data. Really high and low playtimes were removed. Due to Counter-Strike flavors being so popular, I removed those playtimes as well. Also, playtime_2weeks was not available for many users so that column was dropped.
For the game metadata, genres and tags were encoded and description was preprocessed using natural language processing.

### [Ensemble Model](notebooks/model_ensemble.ipynb)
For collaborative filtering, Grid Search is used to find the best hyperparameters for KNNWithZscore. Then split the data to a train and test set and evaluate the model. Build some functions around it to translate between raw id's and inner ids and to get recommendations based when given a game title.
For content-based filtering, descriptions are vectorized using TF-IDF. Then previously encoded genres and tags are latched on to those vectors. A cosine similarity matrix is created based on the joined genre, tags and description vectors. Similarly, a function is provided to get recommendations based on metadata. 
A combined recommendation function is available that takes similarity vectors from both matrices and calculates a weighted average on the fly. 
The downside of this implementation is that two separate models need to be stored and it takes up a lot of space. Also it is not a true hybrid.

### [Hybrid Model](notebooks/model_hybrid.ipynb)
A modified and improved version of the ensemble model. Different scalers for playtime data are tried out and it seems that simple normalizing yields the best RMSE. From the KNNWithZScore model, a KNN similarity matrix is built and reindexed to match the cosine similarity matrix. A single weighted matrix is then created based on the two matrices. In order to save space when storing the model for deployment, matrix entries are converted from float64 to float16. Currently working on a method to save even more space by taking advantage of matrix symmetricity and storing it in an array. This might mean more overhead when retrieving the similarities.

### [SVDpp model](notebooks/model_svd.ipynb)
WIP.

### [Keras Neural Network Model](notebooks/model_tensor.ipynb)
WIP. For now just a model based on collaborative filtering that was adapted from Keras website.

### [Algo Benchmarking](notebooks/model_benchmark.ipynb)
Code by Susan Li to benchmark different algorithms for collaborative filtering. Thank you Susan! Link for her gist and article in the code. Because I wanted this recommender system to be not user-to-user based, i opted for KNNWithZScore.

### [Flask Deployment](flask_app)
A Flask app for deployment. Not yet meant for online deployment. TODO: wrap it in gunicorn and nginx.

So long, and thanks for all the fish!

P.S.: Wasn't sure if Steam would like it if I upload my collected datasets to github so at the moment the data folder is empty.
