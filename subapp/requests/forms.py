from flask_wtf import FlaskForm
from wtforms import DateField
from wtforms.fields import SubmitField, RadioField, IntegerField
from wtforms.validators import DataRequired, NumberRange


class RequestForm(FlaskForm):
    """
    Form for creating a new request.
    """
    date_requested = DateField('Date Requested', format='%Y-%m-%d', validators=[DataRequired()])
    isSwap = RadioField(coerce=bool, choices=[(True, 'Yes'), (False, 'No')], validators=[DataRequired()])
    bonus = IntegerField("Bonus")
    submit = SubmitField('Submit')
    