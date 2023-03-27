from flask_wtf import FlaskForm
from wtforms import StringField, DateField, SubmitField, SelectField
from wtforms.validators import DataRequired


class SectionSelectForm(FlaskForm):
    perch_mount_name = StringField(
        "棲架名稱",
        validators=[DataRequired(message="Not Null")],
    )
    check_date = DateField(validators=[DataRequired(message="Not Null")])
    submit_button = SubmitField("Review")
