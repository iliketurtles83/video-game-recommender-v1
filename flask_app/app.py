''' Flask app that takes in a game title and returns the top 10 similar games '''

from flask import Flask, render_template, request
from flask_bootstrap import Bootstrap
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired
from utils.utils import recommend_content

import os

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
    # if request
    name = request.args.get('name')
    form = NameForm()
    title = ""
    message = ""
    if form.validate_on_submit():
        title = form.name.data
    elif name != None:
        title = name
    if title:
        similar_games = recommend_content(title)
        if similar_games:
            message = "Games similar to " + title
            return render_template('index.html', form=form, message=message, similar_games=similar_games)
        else:
            message = "That game is not in our database."
            return render_template('index.html', form=form, message=message)
    return render_template('index.html', form=form, message=message)

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)

