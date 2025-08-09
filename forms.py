from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed, FileRequired
from wtforms import SubmitField


class UploadForm(FlaskForm):
    file = FileField(
        "Upload .dat file",
        validators=[
            FileRequired(),
            FileAllowed(['dat'], "Only .dat files are allowed!")
        ]
    )
    submit = SubmitField("Upload")
