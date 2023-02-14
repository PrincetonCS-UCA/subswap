from flask_wtf import FlaskForm
from wtforms.validators import DataRequired
from wtforms.widgets import ListWidget, CheckboxInput
from wtforms.fields import SubmitField, FileField, StringField, SelectMultipleField
from flask_wtf.file import FileRequired, FileAllowed


class MultiCheckboxField(SelectMultipleField):
    """
    A multiple-select, except displays a list of checkboxes.

    Iterating the field will produce subfields, allowing custom rendering of
    the enclosed checkbox fields.
    """
    widget = ListWidget(prefix_label=False)
    option_widget = CheckboxInput()

class AddScheduleForm(FlaskForm):
    """
    Form for creating a new request.
    """
    cos226 = FileField('COS2xx Schedule', validators=[FileRequired(), FileAllowed(['csv'], 'CSV files only!')])
    cos126 = FileField('COS126 Schdeule', validators=[FileRequired(), FileAllowed(['csv'], 'CSV files only!')])
    submit = SubmitField('Submit')

class AddUserForm(FlaskForm):
    """
    Form for adding a new user or editing an existing one.
    """
    netid = StringField('netid', validators=[DataRequired()])
    roles = SelectMultipleField('roles', choices=[], validators=[DataRequired()])
    shifts = SelectMultipleField('shifts', choices=[])
    submit = SubmitField('Submit')



