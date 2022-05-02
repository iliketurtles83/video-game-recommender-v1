# Video Game Recommender v1
### A simple Video Game Recommendation System using Steam data and Machine Learning

Too many games, not enough time! I love websites that recommend me stuff even if I dont always agree with their suggestions.
So for my final project at Lighthouse, I decided to make my own simple video game recommendation system based on data from Steam.

At the moment, the system is an ensemble model of collaborative filtering and content-based filtering at best. True hybrid would be nice.

For now, i have both ipynb and py files uploaded. The notebook files should run fine but py files are a work in progress.

#### Data Collection and Scraping (steam_api)
Using a set of Steam IDs from steamid.uk, I was able to get the user playtime data via Steam API. Steam made all profiles private by default in 2018 and thus only 20% of those IDs came back with data. Enter recursion. I grabbed some random IDs from the working ones and recursively checked these users' friends, friends of friends and so on (depth = 6 seemed ok). This gave me some additional playtimes. I would not recommend getting playtime data for users on the various Steam fan site toplists. There is a high chance they have ridiculously playtime hours due to in-game content farming (or something else fishy). Then for all the steam games the users had played, I got game metadata from Steam API.

#### Data Preparation (steam_data_prep)
Had to wrangle that data. I removed high playtimes and it seemed okay because the dataset didnt get much smaller. Due to Counter-Strike flavors being so popular, I removed those playtimes as well or otherwise my system would have recommended CS to everybody. Also, playtime_2weeks was not available for many users so I decided to drop that column.
For the game metadata, genres and tags were encoded. To add to that, natural language processing methods were applied to the description column. I cleaned the texts using NLTK and then vectorize the words and their frequencies using TF-IDF.

#### Algo Benchmarking (benchmark)
Code by Susan Li to benchmark different algorithms for collaborative filtering. Thank you Susan! Link for her gist and article in the code. Because I wanted this recommender system to be not user-to-user based, i opted for KNNWithZScore. Maybe do a user-based SVD version in the future?

#### Models, Evaluation and Predictions (model_main)
Lots of stuff happening here. For collaborative filtering, I did the Grid Search to find best hyperparameters for KNNWithZscore. Then split the data to a train and test set and evaluate the model. Build some functions around it to translate between raw id's and inner ids and to get 10 recommendations based on user input.
For content-based filtering, create a cosine similarity matrix based on the joined genre, tags and description vectors. Then a function to retrieve top 10 items with the closest similarity.

#### Flask Deployment (games_flask)
A Flask app for deployment. I would not recommend actually deploying this online as it is buggy and insecure.

#### Known bugs
- If you enter 'Hitman™', the collaborative recommend function will crash. WIP

So long, and thanks for all the fish!

P.S.: Wasn't sure if Steam would like it if I upload my collected datasets to github so at the moment the data folder is empty.
