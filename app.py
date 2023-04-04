from config import *
from pathlib import Path
from datetime import datetime, timezone, date
from tool import SpeciesTrie, PMOccurrences, PMRawMedia
from form import SectionSelectForm
from query_mysql import get_perch_mount_names
from flask import Flask, render_template, send_from_directory, jsonify, request
from query_mongo import get_all_species, get_path_by_object_id
from query_bigquery import (
    get_occurrence_by_section,
    get_section_condition,
    get_unempty_check_occurrence_by_section,
)

import pandas as pd
import json

app = Flask(__name__)
app.config["SECRET_KEY"] = "key"
species_trie = SpeciesTrie(get_all_species())


@app.route("/", methods=["GET", "POST"])
def index():
    section_select_form = SectionSelectForm()
    perch_mount_names = get_perch_mount_names()

    return render_template(
        "index.html",
        section_select_form=section_select_form,
        perch_mount_names=perch_mount_names,
    )


@app.route("/empty_check/<string:perch_mount_name>/<string:check_date>")
def empty_check(perch_mount_name, check_date):
    start_time, end_time = get_section_condition(perch_mount_name, check_date)

    if not start_time or not end_time:
        return render_template(
            "perch_mount_not_found.html",
            perch_mount_name=perch_mount_name,
            check_date=check_date,
        )
    raw_media = get_unempty_check_occurrence_by_section(
        perch_mount_name,
        start_time,
        end_time,
    )

    raw_media = PMRawMedia(raw_media)
    # print(raw_media.raw_media)

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
        print(data, perch_mount_name, check_date)
    return render_template(
        "empty_check_done.html",
        perch_mount_name=perch_mount_name,
        check_date=check_date,
    )


@app.route("/review/<string:perch_mount_name>/<string:check_date>")
def review(perch_mount_name, check_date):
    global species_trie
    # start_time, end_time = get_section_condition(perch_mount_name, check_date)
    # if not start_time or not end_time:
    #     return render_template(
    #         "perch_mount_not_found.html",
    #         perch_mount_name=perch_mount_name,
    #         check_date=check_date,
    #     )

    # occurrences = get_occurrence_by_section(perch_mount_name, start_time, end_time)
    # start_time = datetime.strptime("2022-03-31 15:45:00", DATETIME_FROMAT)
    # end_time = datetime.strptime("2022-04-09 13:54:00", DATETIME_FROMAT)
    # occurrences = get_occurrence_by_section("土庫南側", start_time, end_time)
    # occurrences = PMOccurrences(occurrences)

    # occurrences[
    #     "path"
    # ] = "https://github.com/Chendada-8474/DetectiveKite/blob/main/sample/img004.jpg?raw=true"
    # occurrences["path"] = occurrences.apply(
    #     lambda df: get_path_by_object_id(df["object_id"]), axis=1
    # )
    species_trie = SpeciesTrie(get_all_species())
    test = {
        1: {"individual": ["Light-vented Bulbul", "Black-winged Kite"]},
        2: {"individual": ["Black-winged Kite"]},
        3: {"individual": ["Grey Treepie"]},
    }

    return render_template(
        "review.html",
        perch_mount_name=perch_mount_name,
        check_date=check_date,
        occurrences=test,
    )


@app.route("/_species_prediction", methods=["GET", "POST"])
def species_perdiction():
    word = request.form.get("species-input")
    results = species_trie.search(word)
    return jsonify(results)


@app.route("/uploads/<path:path>")
def download_file(path):
    print(path)
    path = Path(path)
    file_name = path.name
    dir_name = path.parent
    dir_name = "//" + str(dir_name)
    # file_name = "5a4613ac_高屏溪白茅草_20230211_115944.JPG"
    # dir_name = "\\Birdlab-Nas\棲架資料\棲架資料庫\高屏溪白茅草\高屏溪白茅草_20230211_20230309"
    return send_from_directory(dir_name, file_name, as_attachment=True)


if __name__ == "__main__":
    app.run(debug=True)
