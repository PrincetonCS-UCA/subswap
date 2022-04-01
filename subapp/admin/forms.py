from flask_wtf import FlaskForm
from wtforms.fields import SubmitField, FileField
from flask_wtf.file import FileRequired, FileAllowed


class AddScheduleForm(FlaskForm):
    """
    Form for creating a new request.
    """
    cos226 = FileField('COS2xx Schedule', validators=[FileRequired(), FileAllowed(['csv'], 'CSV files only!')])
    cos126 = FileField('COS126 Schdeule', validators=[FileRequired(), FileAllowed(['csv'], 'CSV files only!')])
    submit = SubmitField('Submit')
    