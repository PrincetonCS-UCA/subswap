from flask_wtf import FlaskForm
from wtforms import DateField, Form
from wtforms.fields import SubmitField, IntegerField
from wtforms.validators import DataRequired


class RequestForm(FlaskForm):
    """
    Form for creating a new request.
    """
    date_requested = DateField(
        'Date Requested', format='%Y-%m-%d', validators=[DataRequired()])
    bonus = IntegerField("Bonus")
    submit = SubmitField('Submit')
