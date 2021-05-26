from flask import Flask, render_template  # , redirect, url_for
from flask_bootstrap import Bootstrap
from flask_wtf import FlaskForm
from wtforms import SubmitField, SelectField  # StringField,
from wtforms.validators import DataRequired
import wtforms
import xmlrpc.client
import re

p = re.compile('Process-(\d+)')

proxy = xmlrpc.client.ServerProxy('http://localhost:9000')

app = Flask(__name__)

# Flask-WTF requires an encryption key - the string can be anything
app.config['SECRET_KEY'] = 'C2HWGVoMGfNTBsrYQg8EcMrdTimkZfAb'

# Flask-Bootstrap requires this line
Bootstrap(app)


class RequiredIfFieldEqualTo(wtforms.validators.Optional):
    # a validator which makes a field optional if
    # another field has a desired value

    def __init__(self, other_field_name, value, *args, **kwargs):
        self.other_field_name = other_field_name
        self.value = value
        super(RequiredIfFieldEqualTo, self).__init__(*args, **kwargs)

    def __call__(self, form, field):
        other_field = form._fields.get(self.other_field_name)
        if other_field is None:
            raise Exception('no field named "%s" in form' % self.other_field_name)
        if other_field.data != self.value:
            super(RequiredIfFieldEqualTo, self).__call__(form, field)


class NameForm(FlaskForm):
    function = SelectField('Function', choices=['', 'Put Task', 'Create Worker', 'Eliminate Worker'],
                           validators=[DataRequired()])
    task = SelectField('Task', choices=['', 'CountingWords', 'WordCount'],
                       validators=[RequiredIfFieldEqualTo('function', 'Put Task')])
    file = wtforms.fields.TextField('File', validators=[RequiredIfFieldEqualTo('function', 'Put Task')])
    worker = SelectField('Worker',
                         validators=[RequiredIfFieldEqualTo('function', 'Eliminate Worker')])
    submit = SubmitField('Submit')


@app.route('/', methods=['GET', 'POST'])
def index():
    # you must tell the variable 'form' what you named the class, above
    # 'form' is the variable name used in this template: index.html
    form = NameForm()
    form.worker.choices = proxy.workersList()
    message = ""
    if form.validate_on_submit():
        function = form.function.data
        task = form.task.data+","+str(proxy.get_task())+";"
        for i in form.file.data.split(','):
            task += "http://localhost:8000/"+i+","
        task = task[:-1]
        if function == 'Put Task':
            proxy.put_task(task)
            message = 'Tasca ' + str(task) + ' afegida'
            proxy.inc_task()
        if function == 'Create Worker':
            id = proxy.create_worker()
            message = 'Node ' + str(id) + ' creat'
            form.worker.choices = proxy.workersList()
        if function == 'Eliminate Worker':
            try:
                proxy.eliminate_worker(p.match(form.worker.data).group(1))
            except:
                message = 'Node eliminat'
            form.worker.choices = proxy.workersList()
    return render_template('index.html', form=form, message=message)


if __name__ == "__main__":
    app.run()
