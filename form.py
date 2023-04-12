from flask_wtf import FlaskForm
from query_mysql import get_positions, get_habitats, get_projects
from wtforms import (
    StringField,
    DateField,
    SubmitField,
    SelectField,
    EmailField,
    FloatField,
    SelectMultipleField,
    TextAreaField,
)
from wtforms.validators import DataRequired

postion_options = [
    (position.position_id, position.position_ch_name) for position in get_positions()
]

habitat_selection = [
    (habitat.habitat_id, f"{habitat.habitat_ch_name} ({habitat.habitat_eng_name})")
    for habitat in get_habitats()
]

project_options = [
    (project.project_id, project.project_name) for project in get_projects()
]


class SectionSelectForm(FlaskForm):
    perch_mount_name = StringField(
        "棲架名稱",
        validators=[DataRequired()],
    )
    check_date = DateField(validators=[DataRequired()])
    review_button = SubmitField("Review")


class PerchMountForm(FlaskForm):
    perch_mount_name = StringField("棲架名稱", validators=[DataRequired()])
    latitude = FloatField("緯度", validators=[DataRequired()])
    longitude = FloatField("經度", validators=[DataRequired()])
    habitat_id = SelectField(
        "棲地類型", choices=habitat_selection, validators=[DataRequired()], coerce=int
    )
    project_id = SelectMultipleField(
        "計畫 (可多選)", choices=project_options, validators=[DataRequired()], coerce=int
    )
    note = TextAreaField("備註")
    submit_button = SubmitField("新增")


class MemberFrom(FlaskForm):
    user_name = StringField("使用者名稱", validators=[DataRequired()])
    last_name = StringField("姓氏", validators=[DataRequired()])
    first_name = StringField("名字", validators=[DataRequired()])
    phone_number = StringField("電話")
    email = EmailField("Email")
    position_id = SelectField("職稱", choices=postion_options)
    submit_button = SubmitField("新增")


class BehaviorFrom(FlaskForm):
    behavior_ch_name = StringField("行為中文", validators=[DataRequired()])
    behavior_eng_name = StringField("行為英文", validators=[DataRequired()])
    submit_button = SubmitField("新增")


class PreyForm(FlaskForm):
    prey_ch_name = StringField("獵物中文", validators=[DataRequired()])
    prey_eng_name = StringField("獵物英文", validators=[DataRequired()])
    submit_button = SubmitField("新增")


class CameraForm(FlaskForm):
    camera_name = StringField("相機型號", validators=[DataRequired()])
    submit_button = SubmitField("新增")
