from flask import Flask, render_template, redirect, url_for
from flask_bootstrap import Bootstrap
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired

app = Flask(__name__)

# Flask-WTF requires an encryption key - the string can be anything
app.config['SECRET_KEY'] = 'C2HWGVoMGfNTBsrYQg8EcMrdTimkZfAb'

# Flask-Bootstrap requires this line
Bootstrap(app)

class NameForm(FlaskForm):
    name = StringField('Which actor is your favorite?', validators=[DataRequired()])
    submit = SubmitField('Submit')

@app.route('/', methods=['GET', 'POST'])
def index():
    names = {"783dhfuisdhfuihdufasdhfsd", "asdfa"}
    # you must tell the variable 'form' what you named the class, above
    # 'form' is the variable name used in this template: index.html
    form = NameForm()
    message = ""
    if form.validate_on_submit():
        name = form.name.data
        if name == "a":
            # empty the form field
            form.name.data = ""
            # id = get_id(ACTORS, name)
            # redirect the browser to another route and template
            return redirect("https://campusvirtual.urv.cat")
        else:
            message = "That actor is not in our database."
    return render_template('index.html', names=names, form=form, message=message)

if __name__ == "__main__":
    app.run()