from flask_wtf import FlaskForm
from flask_wtf.form import _Auto
from query_mysql import (
    get_positions,
    get_habitats,
    get_projects,
    get_behaviors,
    get_featured_species,
    get_featured_behaviors,
    get_perch_mount_names,
)
from wtforms import (
    StringField,
    DateField,
    SubmitField,
    SelectField,
    EmailField,
    FloatField,
    SelectMultipleField,
    TextAreaField,
    IntegerField,
)
from wtforms.validators import (
    DataRequired,
    Length,
    NumberRange,
    NoneOf,
    ValidationError,
)

postion_options = [
    (position.position_id, position.position_ch_name) for position in get_positions()
]

habitat_selection = [
    (habitat.habitat_id, f"{habitat.habitat_ch_name} ({habitat.habitat_eng_name})")
    for habitat in get_habitats()
]
project_options = [(0, "-- 選擇計畫 --")] + [
    (project.project_id, project.project_name) for project in get_projects()
]

behavior_options = [(b, b) for b in get_featured_behaviors()]
featured_species_options = [(sp, sp) for sp in get_featured_species()]
perch_mount_names_options = [(name, name) for name in get_perch_mount_names()]


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
        "棲地類型",
        choices=[(0, "-- 選擇棲地 --")] + habitat_selection,
        validators=[NumberRange(min=1)],
        coerce=int,
    )
    note = TextAreaField("備註")
    project_id = SelectField(
        "計畫",
        choices=project_options,
        validators=[NumberRange(min=1)],
        coerce=int,
    )
    submit_perch_mount = SubmitField("新增")

    def update_project_options(self, project_options):
        self.project_id.choices = project_options


class LayerPerchMountForm(FlaskForm):
    layer_perch_mount_name = StringField()
    layer_project_id = IntegerField()
    layer_habitat_id = IntegerField()
    layer_latitude = FloatField()
    layer_longitude = FloatField()
    layer = SelectField(
        "選擇分層",
        choices=[("", "-- 選擇分層"), ("upper", "上層"), ("middle", "中層"), ("lower", "下層")],
        validators=[NoneOf("")],
    )
    layer_note = TextAreaField()
    layer_submit_perch_mount = SubmitField("新增")


class MemberFrom(FlaskForm):
    user_name = StringField("使用者名稱", validators=[DataRequired()])
    last_name = StringField("姓氏", validators=[DataRequired()])
    first_name = StringField("名字", validators=[DataRequired()])
    phone_number = StringField(
        "電話", validators=[DataRequired(), Length(min=10, max=10)]
    )
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


class EventForm(FlaskForm):
    event_ch_name = StringField("事件中文", validators=[DataRequired()])
    event_eng_name = StringField("事件英文", validators=[DataRequired()])
    submit_button = SubmitField("新增")


class ProjectFrom(FlaskForm):
    project_name = StringField("計畫名稱", validators=[DataRequired()])
    submit_project = SubmitField("新增")


class FeatureFilterForm(FlaskForm):
    start_date = DateField("開始日期", validators=[DataRequired()])
    end_date = DateField("結束日期", validators=[DataRequired()])
    behavior = SelectMultipleField("行為", choices=behavior_options)
    species = SelectMultipleField("物種", choices=featured_species_options)
    perch_mount_names = SelectMultipleField("棲架", choices=perch_mount_names_options)
    submit_filter = SubmitField("搜尋")

    def update_option(
        self, behavior_options, species_options, perch_mount_names_options
    ):
        self.behavior.choices = behavior_options
        self.species.choices = species_options
        self.perch_mount_names.choices = perch_mount_names_options
