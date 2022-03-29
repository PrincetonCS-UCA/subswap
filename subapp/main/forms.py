from flask_wtf import FlaskForm
from wtforms import DateField
from wtforms.fields import SubmitField, BooleanField, IntegerField
from wtforms.validators import DataRequired, NumberRange


class RequestForm(FlaskForm):
    """
    Form for creating a new request.
    """
    date_requested = DateField('Date Requested', format='%Y-%m-%d', validators=[DataRequired()])
    isSwap = BooleanField("Swap", default=True)
    bonus = IntegerField("Bonus", validators=[DataRequired(), NumberRange(min=0)])
    submit = SubmitField('Submit')
    