from flask_wtf import FlaskForm
from wtforms import DateField
from wtforms.fields import SubmitField
from wtforms.validators import DataRequired
# ----------------------------------------------------------------------


class RequestForm(FlaskForm):
    """
    Form for creating a new request.
    """
    date_requested = DateField(
        'Date Requested', format='%Y-%m-%d', validators=[DataRequired()])
    submit = SubmitField('Submit')
# ----------------------------------------------------------------------
