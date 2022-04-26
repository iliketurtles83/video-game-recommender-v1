''' Flask app that takes in a game title and returns the top 10 similar games '''

# import libraries
from flask import Flask, render_template, redirect, url_for
from flask_bootstrap import Bootstrap
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired
import pickle

app = Flask(__name__)

# Flask-WTF requires an encryption key - the string can be anything
app.config['SECRET_KEY'] = 'C2HWGVoMGfNTBsrYQg8EcMrdTimkZfAb'

# Flask-Bootstrap requires this line
Bootstrap(app)

gamesinfo_df = pd.read_csv('../data/steam_gameinfo.csv')
games = gamesinfo_df['name'].tolist()

# load pickle knn model
knn = pickle.load(open('../models/knn_model.pkl', 'rb'))

# load pickle cosine similarity model

class NameForm(FlaskForm):
    name = StringField('Which actor is your favorite?', validators=[DataRequired()])
    submit = SubmitField('Submit')

if __name__ == '__main__':
    app.run(debug=True)

