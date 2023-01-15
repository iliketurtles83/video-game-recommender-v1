''' Flask app that takes in a game title and returns the top 10 similar games '''


from flask import Flask, render_template
from flask_bootstrap import Bootstrap
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired
from utils import combined_recom

import os
import pandas as pd
from os import path

SITE_ROOT = path.realpath(path.dirname(__file__))
# get games info
gamesinfo_df = pd.read_csv(path.join(SITE_ROOT, '../data/steam_gameinfo.csv'))

app = Flask(__name__)

# Flask-WTF requires an encryption key
SECRET_KEY = os.urandom(32)
app.config['SECRET_KEY'] = SECRET_KEY

# Flask-Bootstrap requires this line
Bootstrap(app)


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

