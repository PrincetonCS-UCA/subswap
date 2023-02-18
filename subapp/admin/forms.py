from flask_wtf import FlaskForm
from wtforms.fields import SubmitField, FileField, BooleanField
from wtforms.validators import DataRequired
from flask_wtf.file import FileAllowed
from wtforms.widgets import CheckboxInput


class AddScheduleForm(FlaskForm):
    """
    Form for creating a new request.
    """
    cos2xx = FileField('COS2xx Schedule', validators=[FileAllowed(['csv'], 'CSV files only!')])
    cos126 = FileField('COS126 Schdeule', validators=[FileAllowed(['csv'], 'CSV files only!')])
    clear_db = BooleanField('Clear DB', default=False, widget=CheckboxInput())
    submit = SubmitField('Submit')

    def validate(self, extra_validators=None):
        if super().validate(extra_validators):
            if not (self.cos126.data or self.cos2xx.data):
                self.cos2xx.errors.append('Upload at least one file')
                return False
            else:
                return True

        return False
