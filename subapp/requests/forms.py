from flask_wtf import FlaskForm
from flask_login import current_user
from subapp.models import Shift
from wtforms import DateField, FieldList, FormField, Form
from wtforms.fields import SubmitField, RadioField, IntegerField, SelectField, BooleanField
from wtforms.validators import DataRequired


class SwapDateForm(Form):
    """Subform.

    CSRF is disabled for this subform (using `Form` as parent class) because
    it is never used by itself.
    """
    shift = SelectField('Shift', choices=[], coerce=int,
                        validators=[DataRequired()])
    date = DateField('Date', validators=[DataRequired()])


class RequestForm(FlaskForm):
    """
    Form for creating a new request.
    """
    isSwap = RadioField('Is Swap', choices=[
                        ('True', 'Yes'), ('False', 'No')], validators=[DataRequired()])
    date_requested = DateField(
        'Date Requested', format='%Y-%m-%d', validators=[DataRequired()])
    bonus = IntegerField("Bonus")
    swaps = FieldList(FormField(SwapDateForm), min_entries=5)
    submit = SubmitField('Submit')
