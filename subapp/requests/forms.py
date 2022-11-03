from flask_wtf import FlaskForm
from wtforms import DateField, Form
from wtforms.fields import SubmitField, RadioField, IntegerField, SelectField, BooleanField, SelectMultipleField
from wtforms.validators import DataRequired
from wtforms.widgets import CheckboxInput, ListWidget


class MultiCheckboxField(SelectMultipleField):
    widget = ListWidget(prefix_label=False)
    option_widget = CheckboxInput()


class RequestForm(FlaskForm):
    """
    Form for creating a new request.
    """
    isSwap = RadioField('Is Swap', choices=[
                        ('True', 'Yes'), ('False', 'No')], validators=[DataRequired()])
    date_requested = DateField(
        'Date Requested', format='%Y-%m-%d', validators=[DataRequired()])
    bonus = IntegerField("Bonus")
    swaps = MultiCheckboxField('Shift', validate_choice=False)
    submit = SubmitField('Submit')
