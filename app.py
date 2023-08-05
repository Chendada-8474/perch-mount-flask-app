from PIL import Image
from io import BytesIO
from pathlib import Path
from form import (
    MemberFrom,
    CameraForm,
    BehaviorFrom,
    PreyForm,
    PerchMountForm,
    EventForm,
    ProjectFrom,
    LayerPerchMountForm,
    FeatureFilterForm,
)

from tool import (
    SpeciesTrie,
    ReviewMedia,
    EmptyCheckMedia,
    VariableDictionary,
    move_file_to_empty_dir_by_ids,
    create_empty_move_tasks,
)
from config import *
from flask import (
    Flask,
    render_template,
    send_file,
    send_from_directory,
    jsonify,
    redirect,
    url_for,
    send_file,
    request,
)
from flask_restful import Api
from flask_login import login_required, login_user, logout_user
from login import *
from datetime import datetime
import os
import json
import query_bigquery
import query_mysql
import query_mongo
import api_resource

app = Flask(__name__)
app.config["SECRET_KEY"] = "key"
login_manager.init_app(app)

all_speices = query_mongo.get_all_species()
species_trie = SpeciesTrie(all_speices)
all_speices = query_mongo.get_all_species(
    field=["chinese_common_name", "english_common_name", "taxon_order"]
)
all_prey = query_mysql.get_preys()
all_behavior = query_mysql.get_behaviors()
all_event = query_mysql.get_events()
var_dict = VariableDictionary(all_speices, all_prey, all_behavior, all_event)

api = Api(app)


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template("login.html")
    users = get_users_login_info()
    user_name = request.form["user_name"]
    if (
        user_name in users
        and request.form["phone_number"] == users[user_name]["phone_number"]
    ):
        user = User()
        user.id = user_name
        login_user(user)
        return redirect(url_for("index"))
    return "Bad login"


@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("login"))


@app.route("/", methods=["GET", "POST"])
@login_required
def index():
    perch_mount_names = query_mysql.get_perch_mount_names()

    return render_template(
        "index.html",
        perch_mount_names=perch_mount_names,
    )


@app.route(
    "/empty_check/<string:perch_mount_name>/<string:start_datetime>/<string:end_datetime>"
)
@login_required
def empty_check(perch_mount_name, start_datetime, end_datetime):
    perch_mounts = query_mysql.get_perch_mount_names()
    if perch_mount_name not in perch_mounts:
        return render_template(
            "perch_mount_not_found.html", perch_mount_name=perch_mount_name
        )

    if start_datetime == "any":
        start_datetime = EARLEIST_DATETIME
    if end_datetime == "any":
        end_datetime = DATETIME_NOW

    empty_media = query_mysql.get_empty_media(
        perch_mount_name,
        start_datetime=start_datetime,
        end_datetime=end_datetime,
        limit=MEDIA_PER_PAGE_EMPTY_CHECK,
    )

    empty_media = EmptyCheckMedia(empty_media)

    if len(empty_media) == 0:
        return render_template(
            "empty_check_done.html",
            perch_mount_name=perch_mount_name,
            start_datetime=start_datetime,
            end_datetime=end_datetime,
            num_media=len(empty_media),
        )

    return render_template(
        "empty_check.html",
        perch_mount_name=perch_mount_name,
        empty_media=empty_media.json,
        start_datetime=start_datetime,
        end_datetime=end_datetime,
    )


@app.route("/empty_check_done", methods=["POST", "GET"])
@login_required
def empty_check_done():
    perch_mount_name = None
    check_date = None
    if request.method == "POST":
        data = request.form["checked_data"]
        data = json.loads(data)
        empty_checker = request.form["empty_checker"]
        perch_mount_name = request.form["perch_mount_name"]
        check_date = request.form["check_date"]

        all_object_ids = [object_id for object_id in data["empty_object_id"]]
        for row in data["fn_object_data"]:
            all_object_ids.append(row["object_id"])

        query_mysql.insert_detected_media(data["fn_object_data"])
        query_mysql.update_check_media(all_object_ids)
        move_file_errors = move_file_to_empty_dir_by_ids(data["empty_object_id"])
        query_mongo.delete_many_files_by_ids(data["empty_object_id"])

        operation_errors = query_bigquery.insert_operation(
            empty_checker, "empty_check", len(all_object_ids), perch_mount_name
        )
        if operation_errors:
            return render_template(
                "error.html", errors=operation_errors + move_file_errors
            )

    return render_template(
        "empty_check_done.html",
        perch_mount_name=perch_mount_name,
        check_date=check_date,
    )


@app.route(
    "/review/<string:perch_mount_name>/<string:start_datetime>/<string:end_datetime>"
)
@login_required
def review(perch_mount_name, start_datetime, end_datetime):
    perch_mounts = query_mysql.get_perch_mount_names()
    behaviors = query_mysql.get_behaviors()
    if perch_mount_name not in perch_mounts:
        return render_template(
            "perch_mount_not_found.html", perch_mount_name=perch_mount_name
        )

    if start_datetime == "any":
        start_datetime = EARLEIST_DATETIME
    if end_datetime == "any":
        end_datetime = DATETIME_NOW

    occurrences = query_mysql.get_detected_occurrences(
        perch_mount_name,
        start_datetime=start_datetime,
        end_datetime=end_datetime,
        limit=MEDIA_PER_PAGE_REVIEW,
    )

    if not len(occurrences):
        return render_template(
            "review_done.html",
            perch_mount_name=perch_mount_name,
            check_date="",
        )

    media = ReviewMedia(occurrences)
    events = query_mysql.get_events()

    return render_template(
        "review.html",
        perch_mount_name=perch_mount_name,
        start_datetime=start_datetime,
        end_datetime=end_datetime,
        behaviors=behaviors,
        events=events,
        media=media,
    )


@app.route("/review_done", methods=["POST", "GET"])
@login_required
def review_done():
    if request.method == "POST":
        data = json.loads(request.form["review_data"])
        reviewer = request.form["reviewer"]
        perch_mount_name = request.form["perch_mount_name"]
        check_date = request.form["check_date"]
        num_media = request.form["num_media"]

        if query_mysql.is_media_reviewed([o["object_id"] for o in data["occurrences"]]):
            return render_template(
                "error.html", errors=["你送了一個已經重複的資料，請確認現在沒有其他人在跟你看一樣的棲架"]
            )

        events = query_bigquery.event_for_insert(
            data["event_media"], perch_mount_name, var_dict
        )
        occurrences = query_bigquery.occurrence_for_insert(
            data, perch_mount_name, var_dict
        )

        if occurrences:
            occurrence_errors = query_bigquery.insert_occurrences(occurrences)
            if occurrence_errors:
                return render_template("error.html", errors=occurrence_errors)
            query_mysql.reviewed_detected_media([o["object_id"] for o in occurrences])

        query_mysql.insert_feature_media(data["featured_media"], perch_mount_name)
        query_mysql.reviewed_detected_media(
            [d["object_id"] for d in data["featured_media"]]
        )
        # create_empty_move_tasks(data["empty_media_ids"])

        errors = move_file_to_empty_dir_by_ids(data["empty_media_ids"])
        print(errors)
        query_mysql.reviewed_detected_media(data["empty_media_ids"])

        if events:
            event_errors = query_bigquery.insert_events(data["event_media"])
        else:
            event_errors = []
        if event_errors:
            return render_template("error.html", errors=event_errors)
        query_mysql.reviewed_detected_media(
            [d["object_id"] for d in data["event_media"]]
        )

        operation_errors = query_bigquery.insert_operation(
            reviewer, "review", num_media, perch_mount_name
        )
        if operation_errors:
            return render_template("error.html", errors=event_errors)

        for occurrence in occurrences:
            query_mongo.species_called(occurrence["taxon_order_by_human"])

    return render_template(
        "review_done.html",
        perch_mount_name=perch_mount_name,
        check_date=check_date,
    )


@app.route("/pending")
def pending():
    count = query_mysql.get_pending_perch_mounts()
    num_unempty_checked = query_mysql.get_num_unempty_check_media()
    num_unreviewed = query_mysql.get_num_unreviewed_media()
    projects = query_mysql.get_projects()
    ai_tasks = os.listdir(NEW_TASKS_DESTINATION)
    return render_template(
        "pending.html",
        count=count,
        projects=projects,
        ai_tasks=ai_tasks,
        num_unreviewed=num_unreviewed,
        num_unempty_checked=num_unempty_checked,
    )


@app.route("/uploads/<path:path>")
def download_file(path):
    _, extension = os.path.splitext(path)
    # path = "//" + path
    if extension.lower()[1:] in IMAGE_EXTENSIONS:
        image_io = BytesIO()
        image = Image.open(path)
        image.thumbnail((960, 540))
        image.save(image_io, "JPEG")
        image_io.seek(0)
        return send_file(image_io, mimetype="image/jpeg")
    elif extension.lower()[1:] in VIDEO_EXTENSIONS:
        dir_path = os.path.dirname(path)
        file_name = os.path.basename(path)
        return send_from_directory(dir_path, file_name)


@app.route("/perch_mount", methods=["GET", "POST"])
@login_required
def perch_mount():
    layer_perch_mount_form = LayerPerchMountForm()
    perch_mount_form = PerchMountForm()
    projects = query_mysql.get_projects()

    project_options = [(0, "-- 選擇計畫 --")] + [
        (p.project_id, p.project_name) for p in projects
    ]
    perch_mount_form.update_project_options(project_options)
    project_from = ProjectFrom()

    if project_from.submit_project.data and project_from.validate_on_submit():
        query_mysql.insert_project(project_from)
        projects = query_mysql.get_projects()
        project_options = [(0, "-- 選擇計畫 --")] + [
            (p.project_id, p.project_name) for p in projects
        ]
        perch_mount_form.update_project_options(project_options)

    if (
        perch_mount_form.submit_perch_mount.data
        and perch_mount_form.validate_on_submit()
    ):
        variable_table = {
            "perch_mount_name": perch_mount_form.perch_mount_name.data,
            "habitat_id": perch_mount_form.habitat_id.data,
            "project_id": perch_mount_form.project_id.data,
            "latitude": perch_mount_form.latitude.data,
            "longitude": perch_mount_form.longitude.data,
            "note": perch_mount_form.note.data,
        }
        query_mysql.insert_perch_mount(variable_table)
        errors = query_bigquery.insert_perch_mount(variable_table)
        if errors:
            return render_template("error.html", errors=errors)

    if (
        layer_perch_mount_form.layer_submit_perch_mount.data
        and layer_perch_mount_form.validate_on_submit()
    ):
        t = {"upper": "上層", "middle": "中層", "lower": "下層"}
        layer_perch_mount_form.layer_perch_mount_name.data += t[
            layer_perch_mount_form.layer.data
        ]
        variable_table = {
            "perch_mount_name": layer_perch_mount_form.layer_perch_mount_name.data,
            "habitat_id": layer_perch_mount_form.layer_habitat_id.data,
            "project_id": layer_perch_mount_form.layer_project_id.data,
            "latitude": layer_perch_mount_form.layer_latitude.data,
            "longitude": layer_perch_mount_form.layer_longitude.data,
            "note": layer_perch_mount_form.layer_note.data,
            "layer": layer_perch_mount_form.layer.data,
        }
        query_mysql.insert_perch_mount(variable_table)
        errors = query_bigquery.insert_perch_mount(variable_table)
        if errors:
            return render_template("error.html", errors=errors)

    perch_mounts = query_mysql.get_perch_mounts()
    return render_template(
        "perch_mount.html",
        perch_mounts=perch_mounts,
        projects=projects,
        perch_mount_form=perch_mount_form,
        layer_perch_mount_form=layer_perch_mount_form,
        project_from=project_from,
    )


@app.route("/update", methods=["GET", "POST"])
@login_required
def update():
    return render_template("update.html")


@app.route("/member", methods=["GET", "POST"])
@login_required
def member():
    member_form = MemberFrom()
    if member_form.validate_on_submit():
        query_mysql.insert_member(member_form)
    positions = query_mysql.get_positions()
    members = query_mysql.get_members()
    return render_template(
        "member.html", members=members, member_form=member_form, positions=positions
    )


@app.route("/prey", methods=["GET", "POST"])
@login_required
def prey():
    prey_form = PreyForm()
    if prey_form.validate_on_submit():
        query_mysql.insert_prey(prey_form)

    preys = query_mysql.get_preys()
    return render_template("prey.html", preys=preys, prey_form=prey_form)


@app.route("/camera", methods=["GET", "POST"])
@login_required
def camera():
    camera_form = CameraForm()
    if camera_form.validate_on_submit():
        query_mysql.insert_camera(camera_form)
    cameras = query_mysql.get_cameras()
    return render_template("camera.html", cameras=cameras, camera_form=camera_form)


@app.route("/behavior", methods=["GET", "POST"])
@login_required
def behavior():
    behavior_form = BehaviorFrom()
    if behavior_form.validate_on_submit():
        query_mysql.insert_behavior(behavior_form)

    behaviors = query_mysql.get_behaviors()
    return render_template(
        "behavior.html",
        behaviors=behaviors,
        behavior_form=behavior_form,
    )


@app.route("/event", methods=["GET", "POST"])
@login_required
def event():
    event_form = EventForm()
    if event_form.validate_on_submit():
        query_mysql.insert_event(event_form)
    events = query_mysql.get_events()
    return render_template(
        "event.html",
        events=events,
        event_form=event_form,
    )


@app.route("/species_input_predict", methods=["POST", "GET"])
def species_input_predict():
    phrase = request.get_data(as_text=True)
    predictions = species_trie.search(phrase) if phrase else []
    predictions = [
        [p[1], p[2]] for p in sorted(predictions, reverse=True, key=lambda x: x[0])
    ]
    return jsonify(predictions)


@app.route("/check_common_name", methods=["POST", "GET"])
def check_common_name():
    media = request.get_json()
    for medium in media:
        medium["valid"] = all(
            var_dict.has_common_name(common_name) if common_name else True
            for common_name in medium["chinese_common_name"]
        )
    return jsonify(media)


@app.route("/lookup_common_name", methods=["POST", "GET"])
def lookup_common_name():
    common_names = request.get_json()
    taxon_orders = []
    for name in common_names:
        if var_dict.has_common_name(name):
            taxon_orders.append(var_dict.from_ch[name])
        else:
            taxon_orders.append(None)
    return taxon_orders


@app.route("/update_perch_mount_status", methods=["POST", "GET"])
def update_perch_mount_status():
    data = request.get_json()
    status = int(data["status"])
    perch_mount_id = int(data["perch_mount_id"])
    query_bigquery.update_perch_mount_status(
        perch_mount_id, "true" if status else "false"
    )
    query_mysql.update_perch_mount_status(perch_mount_id, status)
    return {"perch_mount_id": perch_mount_id, "terminated": status}


@app.route("/feature", methods=["GET"])
@login_required
def feature():
    feature_filter_form = FeatureFilterForm()
    featured_media = query_mysql.get_all_featured_media()
    behaviors = list(
        set((medium.behavior, medium.behavior) for medium in featured_media)
    )
    species = list(set((medium.species, medium.species) for medium in featured_media))
    perch_mount_names = list(
        set(
            (medium.perch_mount_name, medium.perch_mount_name)
            for medium in featured_media
        )
    )

    feature_filter_form.update_option(behaviors, species, perch_mount_names)

    return render_template(
        "feature.html",
        feature_filter_form=feature_filter_form,
    )


@app.route("/feature_media", methods=["GET", "POST"])
def feature_media():
    data = request.get_json()
    results = query_mysql.get_featured_media(data)

    media = []
    for medium in results:
        info = medium[0].__dict__
        info["featured_by"] = medium[1].first_name if medium[1] else None
        media.append(info)

    # media = [medium[0].__dict__ for medium in results]
    for medium in media:
        medium["path"] = query_mongo.get_path_by_object_id(medium["object_id"])
        medium.pop("_sa_instance_state")
    return jsonify(media)


@app.route("/download_medium/<string:object_id>", methods=["GET", "POST"])
def download_medium(object_id):
    path = query_mongo.get_path_by_object_id(object_id)
    return send_file(path, as_attachment=True)


api.add_resource(
    api_resource.PendingDetectedMedia, "/pending_media/<int:perch_mount_id>"
)

api.add_resource(
    api_resource.OccurenceUpdate,
    "/update_medium/<string:medium_date>/<string:object_id>",
)

api.add_resource(api_resource.User, "/user/<int:user_id>")

api.add_resource(api_resource.FeatureMedia, "/featured/<int:feature_medium_id>")

api.add_resource(
    api_resource.ClaimPerchMount,
    "/claim_perch_mount/<int:perch_mount_id>/<int:member_id>",
)

api.add_resource(
    api_resource.PriorityPerchMount,
    "/perch_mount_priority/<int:perch_mount_id>/<int:priority>",
)

if __name__ == "__main__":
    app.debug = True
    app.run()
