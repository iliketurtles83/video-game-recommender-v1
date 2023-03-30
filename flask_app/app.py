''' Flask app that takes in a game title and returns the top 10 similar games '''

from flask import Flask, render_template
from flask_bootstrap import Bootstrap5
from flask_wtf import FlaskForm, CSRFProtect
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired
from utils.utils import recommend_content
import os

csrf = CSRFProtect()
app = Flask(__name__)

SECRET_KEY = os.urandom(32)
app.config['SECRET_KEY'] = SECRET_KEY

csrf.init_app(app)
Bootstrap5(app)


class NameForm(FlaskForm):
    name = StringField('Enter game name: ', validators=[DataRequired()])
    submit = SubmitField('Submit')

# route for home page
@app.route('/', methods=['GET', 'POST'])
def index():
    ''' 
    Displays a form to enter a game title.
    Displays results if form is submitted.
    '''
    form = NameForm()
    if form.validate_on_submit():
        title = form.name.data
        similar_games = recommend_content(title)
        if similar_games:
            return render_template('index.html', form=form, game=title, similar_games=similar_games)
        else:
            message = "That game is not in our database."
            return render_template('index.html', form=form, message=message)
    return render_template('index.html', form=form)

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)

