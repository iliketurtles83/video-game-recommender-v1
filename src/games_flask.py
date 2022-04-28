''' Flask app that takes in a game title and returns the top 10 similar games '''

# import libraries
from flask import Flask, render_template, redirect, url_for
from flask_bootstrap import Bootstrap
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired
import pandas as pd
import pickle

app = Flask(__name__)

# Flask-WTF requires an encryption key - the string can be anything
app.config['SECRET_KEY'] = 'C2HWGVoMGfNTBsrYQg8EcMrdTimkZfAb'

# Flask-Bootstrap requires this line
Bootstrap(app)

# get games info
gamesinfo_df = pd.read_csv('/home/berry/Lighthouse/Projects/video-game-recommender-v1/data/steam_gameinfo.csv')

# load pickle knn model
knn = pickle.load(open('/home/berry/Lighthouse/Projects/video-game-recommender-v1/models/knn_model.pkl', 'rb'))

# load trainset
trainset = pickle.load(open('/home/berry/Lighthouse/Projects/video-game-recommender-v1/models/trainset.pkl', 'rb'))

# load pickle cosine similarity model
cosine_sim = pickle.load(open('/home/berry/Lighthouse/Projects/video-game-recommender-v1/models/cosine_sim.pkl', 'rb'))

# Construct a reverse map of indices and game titles
indices = pd.Series(gamesinfo_df.index, index=gamesinfo_df['name'])

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
    return gamesinfo_df['name'].iloc[game_indices].tolist()

# function that takes a game title and returns top 10 for both
def combined_recom(title):
    # get recommended games from knn
    knn_recom = recommend_knn(title)
    # get recommended games from content based
    cont_recom = recommend_content(title)
    # print knn_recom
    return knn_recom, cont_recom

class NameForm(FlaskForm):
    name = StringField('Enter game name: ', validators=[DataRequired()])
    submit = SubmitField('Submit')

# route for home page
@app.route('/', methods=['GET', 'POST'])
def index():
    # you must tell the variable 'form' what you named the class, above
    # 'form' is the variable name used in this template: index.html
    form = NameForm()
    message = ""
    if form.validate_on_submit():
        title = form.name.data
        if title in gamesinfo_df['name'].values:
            collabr, contentr = combined_recom(title)
            message = "Here are the top 10 recommendations for " + title
            return render_template('index.html', form=form, message=message, collabr=collabr, contentr=contentr)
        else:
            message = "That game is not in our database."
            return render_template('index.html', form=form, message=message)
    return render_template('index.html', form=form, message=message)

if __name__ == '__main__':
    app.run(debug=True)

