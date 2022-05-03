''' Data preparation for Steam datasets'''

# import libraries
import pandas as pd
import string
import ast
import re
import nltk
from nltk.stem.porter import PorterStemmer
from sklearn.preprocessing import MultiLabelBinarizer
from sklearn.feature_extraction.text import TfidfVectorizer

''' PLAYTIME DATA PREP '''
# load steam_playtime.csv
users_df = pd.read_csv('data/steam_playtime.csv')

# drop counterstrike i.e. rows where appid is 730, 10 or 240
users_df = users_df[~users_df['appid'].isin([730, 10, 240])]

# drop user playtimes over a 150k minutes
# probably people who mine in-game content using scripts
users_df = users_df[users_df['playtime_forever'] < 100000]

# remove user playtimes under 60 minutes
users_df = users_df[users_df['playtime_forever'] > 60]

# drop playtime_2weeks column, not much there
users_df = users_df.drop(columns = ['playtime_2weeks'])


''' GAME DATA PREP '''
# load steam_app_metadata.csv
games_df = pd.read_csv('data/steam_app_metadata.csv')

# make genres and categories into lists
games_df['categories'] = games_df['categories'].apply(ast.literal_eval)
games_df['genres'] = games_df['genres'].apply(ast.literal_eval)

# instantiate multilabelbinarizer
mlb = MultiLabelBinarizer()

# encode categories 
games_df = games_df.join(pd.DataFrame(mlb.fit_transform(games_df.pop('categories')),
                          columns=mlb.classes_,
                          index=games_df.index))
# encode genres
games_df = games_df.join(pd.DataFrame(mlb.fit_transform(games_df.pop('genres')),
                          columns=mlb.classes_,
                          index=games_df.index))


# process description column for NLP
# fill 'description' column NaN with empty string
games_df['description'] = games_df['description'].fillna('')

stopwords = nltk.corpus.stopwords.words('english')
porter = PorterStemmer()

# function to clean text
def clean_text(text):
    # remove tags
    text = re.sub(r'<.*?>',' ',text)
    # remove URL links
    text = re.sub(r'http\S+', ' ', text)
    # remove non-breaking space
    text = text.replace(u'\xa0', u' ')
    # remove hex
    text = re.sub(r'[^\x00-\x7f]',r'', text)
    # remove punctuation
    text = text.translate(str.maketrans('', '', string.punctuation))
    # remove numbers
    text = re.sub(r'[0-9]+', '', text)
    # make lowercase
    text = text.lower()
    # tokenize text
    tokens = nltk.word_tokenize(text)
    # remove stopwords
    tokens = [w for w in tokens if w not in stopwords]
    # stem words
    tokens = [porter.stem(w) for w in tokens]
    # make tokens into string
    text = ' '.join(tokens)
    # return clean text
    return text

# apply clean_text function to description column
games_df['description'] = games_df['description'].apply(clean_text)

# make description column into string
games_df['description'] = games_df['description'].astype(str)

# instantiate tfidfvectorizer
tfidf = TfidfVectorizer(max_features=1500, lowercase=False, min_df=5, ngram_range=(1,3))

# fit tfidfvectorizer to description column
tfidf_matrix = tfidf.fit_transform(games_df['description'])

# make matrix into dataframe
tfidf_df = pd.DataFrame(tfidf_matrix.toarray(), columns=tfidf.get_feature_names())

# merge tfidf_df with games_df
games_df = pd.concat([games_df, tfidf_df], axis=1)

''' Save dataframes and other stuff '''
# make a dataframe from appid, name, developer and publisher. for our recommendations
# i have to go by location because 'name' is possibly a tf-idf term now
gameinfo_df = games_df.iloc[:, [0,1,3,4]]

# save gameinfo_df to csv
gameinfo_df.to_csv('data/steam_gameinfo.csv', index=False)

# drop rows from users_df where appid is not in games_df
# play time for games is still in user profiles even if a game is no longer on steam
users_df = users_df[users_df['appid'].isin(games_df['appid'])]

# save users_df to csv
users_df.to_csv('data/steam_playtime_clean.csv', index=False)

# drop name, developer, publisher and description from games_df
games_df = games_df.drop(columns = ['name', 'developer', 'publisher', 'description'])

# save games_df to csv
games_df.to_csv('data/steam_app_metadata_clean.csv', index=False)


