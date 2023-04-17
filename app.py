from pathlib import Path
from form import (
    SectionSelectForm,
    MemberFrom,
    CameraForm,
    BehaviorFrom,
    PreyForm,
    PerchMountForm,
)

from datetime import datetime, timezone, date

from tool import (
    SpeciesTrie,
    PMOccurrences,
    PMRawMedia,
    CommonNameChecker,
    move_file_to_empty_dir_by_ids,
)
from config import *
from flask import Flask, render_template, send_from_directory, jsonify, request
import json
import query_bigquery
import query_mysql
import query_mongo

app = Flask(__name__)
app.config["SECRET_KEY"] = "key"
all_speices = query_mongo.get_all_species()
species_trie = SpeciesTrie(all_speices)
all_speices = query_mongo.get_all_species(
    field=["chinese_common_name", "english_common_name", "taxon_order"]
)
common_name_converter = CommonNameChecker(all_speices)


@app.route("/", methods=["GET", "POST"])
def index():
    section_select_form = SectionSelectForm()
    perch_mount_names = query_mysql.get_perch_mount_names()

    return render_template(
        "index.html",
        section_select_form=section_select_form,
        perch_mount_names=perch_mount_names,
    )


@app.route("/empty_check/<string:perch_mount_name>/<string:check_date>")
def empty_check(perch_mount_name, check_date):
    start_time, end_time = query_bigquery.get_section_condition(
        perch_mount_name, check_date
    )

    if not start_time or not end_time:
        return render_template(
            "perch_mount_not_found.html",
            perch_mount_name=perch_mount_name,
            check_date=check_date,
        )
    raw_media = query_bigquery.get_unempty_check_occurrence_by_section(
        perch_mount_name,
        start_time,
        end_time,
    )

    raw_media = PMRawMedia(raw_media)

    if len(raw_media.raw_media) == 0:
        return render_template(
            "empty_check_done.html",
            perch_mount_name=perch_mount_name,
            check_date=check_date,
        )

    return render_template(
        "empty_check.html",
        perch_mount_name=perch_mount_name,
        raw_media=raw_media.raw_media,
        # raw_media=raw_media,
        check_date=check_date,
    )


@app.route("/empty_check_done", methods=["POST", "GET"])
def empty_check_done():
    perch_mount_name = None
    check_date = None
    if request.method == "POST":
        data = request.form["checked_data"]
        data = json.loads(data)
        perch_mount_name = request.form["perch_mount_name"]
        check_date = request.form["check_date"]

        all_object_ids = [object_id for object_id in data["empty_object_id"]]
        for row in data["fn_object_data"]:
            all_object_ids.append(row["object_id"])

        errors = query_bigquery.insert_not_empty_media(data["fn_object_data"])
        if errors:
            return render_template("error.html", errors=errors)

        try:
            query_bigquery.delete_raw_media_by_ids(all_object_ids)
            move_file_to_empty_dir_by_ids(data["empty_object_id"])
            # query_mongo.delete_many_files_by_ids(data["empty_object_id"])
        except Exception as e:
            return render_template("error.html", errors=e)

    return render_template(
        "empty_check_done.html",
        perch_mount_name=perch_mount_name,
        check_date=check_date,
    )


@app.route("/review/<string:perch_mount_name>/<string:check_date>")
def review(perch_mount_name, check_date):
    start_time, end_time = query_bigquery.get_section_condition(
        perch_mount_name, check_date
    )
    if not start_time or not end_time:
        return render_template(
            "perch_mount_not_found.html",
            perch_mount_name=perch_mount_name,
            check_date=check_date,
        )

    occurrences = query_bigquery.get_occurrence_by_section(
        perch_mount_name, start_time, end_time
    )
    occurrences = PMOccurrences(occurrences)
    behaviors = query_mysql.get_behaviors()

    return render_template(
        "review.html",
        perch_mount_name=perch_mount_name,
        check_date=check_date,
        behaviors=behaviors,
        # occurrences=occurrences,
        occurrences=occurrences.occurrence,
    )


@app.route("/review_done", methods=["POST", "GET"])
def review_done():
    if request.method == "POST":
        data = json.loads(request.form["review_data"])
    return render_template("review_done.html")


@app.route("/uploads/<path:path>")
def download_file(path):
    print(path)
    path = Path(path)
    file_name = path.name
    dir_name = path.parent
    dir_name = "//" + str(dir_name)
    return send_from_directory(dir_name, file_name, as_attachment=True)


@app.route("/perch_mount", methods=["GET", "POST"])
def perch_mount():
    perch_mount_form = PerchMountForm()

    if perch_mount_form.validate_on_submit():
        query_bigquery.insert_bq_perch_mount(perch_mount_form)
        pass

    perch_mounts = query_mysql.get_perch_mounts()
    return render_template(
        "perch_mount.html",
        perch_mounts=perch_mounts,
        perch_mount_form=perch_mount_form,
    )


@app.route("/member", methods=["GET", "POST"])
def member():
    member_form = MemberFrom()
    if member_form.validate_on_submit():
        query_mysql.insert_member(member_form)

    members = query_mysql.get_members()
    return render_template("member.html", members=members, member_form=member_form)


@app.route("/prey", methods=["GET", "POST"])
def prey():
    prey_form = PreyForm()
    if prey_form.validate_on_submit():
        query_mysql.insert_prey(prey_form)

    preys = query_mysql.get_preys()
    return render_template("prey.html", preys=preys, prey_form=prey_form)


@app.route("/camera", methods=["GET", "POST"])
def camera():
    camera_form = CameraForm()
    if camera_form.validate_on_submit():
        query_mysql.insert_camera(camera_form)
    cameras = query_mysql.get_cameras()
    return render_template("camera.html", cameras=cameras, camera_form=camera_form)


@app.route("/behavior", methods=["GET", "POST"])
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
            common_name_converter.check_common_name(common_name)
            if common_name
            else True
            for common_name in medium["chinese_common_name"]
        )
    return jsonify(media)


if __name__ == "__main__":
    app.run(debug=True)
