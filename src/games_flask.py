''' Flask app that takes in a game title and returns the top 10 similar games '''

# import libraries
from flask import Flask, Response, request, render_template
import json
import pandas as pd
from wtforms import StringField, Form
import pickle

app = Flask(__name__)

gamesinfo_df = pd.read_csv('data/steam_gameinfo.csv')
games = gamesinfo_df['name'].tolist()

# load pickle model
knn_model = pickle.load(open('models/knn_model.pkl', 'rb'))

games =['aa', 'bb']

class SearchForm(Form):
    autocomp = StringField('Enter Game', id='game_autocomplete')

@app.route('/_autocomplete', methods=['GET'])
def autocomplete():
    return Response(json.dumps(games), mimetype='application/json')

@app.route('/', methods=['GET', 'POST'])
def index():
    form = SearchForm(request.form)
    return render_template("index.html", form=form)

if __name__ == '__main__':
    app.run(debug=True)

