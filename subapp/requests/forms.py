from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import (StringField, SubmitField, TextAreaField,
                     SelectMultipleField, HiddenField)
from wtforms.fields.core import RadioField
from wtforms.validators import DataRequired, Length
from wtforms.widgets import ListWidget, CheckboxInput

class RequestForm(FlaskForm):
    """
    Form for creating a new request.
    """
    isSwap = RadioField(coerce=bool, choices=[(True, 'Yes'), (False, 'No')])
    