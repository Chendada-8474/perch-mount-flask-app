from flask import Flask, render_template, jsonify, request
from form import SectionSelectForm
from tool import SpeciesTrie
from query_mysql import get_perch_mount_names
from query_mongo import get_all_species, get_path_by_object_id
from query_bigquery import get_occurrence_by_section, get_section_condition

import pandas as pd

app = Flask(__name__)
app.config["SECRET_KEY"] = "key"
species_trie = SpeciesTrie(get_all_species())


@app.route("/", methods=["GET", "POST"])
def index():
    section_select_form = SectionSelectForm()
    perch_mount_names = get_perch_mount_names()
    if section_select_form.validate_on_submit():
        return "success"

    return render_template(
        "index.html",
        section_select_form=section_select_form,
        perch_mount_names=perch_mount_names,
    )


@app.route("/<string:perch_mount_name>/<string:check_date>")
def review(perch_mount_name, check_date):
    global species_trie

    # start_time, end_time = get_section_condition(perch_mount_name, check_date)
    # if not start_time or end_time:
    #     return render_template(
    #         "perch_mount_not_found.html",
    #         perch_mount_name=perch_mount_name,
    #         check_date=check_date,
    #     )
    # occurrences = get_occurrence_by_section(perch_mount_name, start_time, end_time)

    occurrences = pd.read_csv("./demo_data/occurence_in_demo_section.csv")
    occurrences["path"] = "img004.jpg"
    # occurrences[
    #     "path"
    # ] = "https://github.com/Chendada-8474/DetectiveKite/blob/main/sample/img004.jpg?raw=true"
    # occurrences["path"] = occurrences.apply(
    #     lambda df: get_path_by_object_id(df["object_id"]), axis=1
    # )

    species_trie = SpeciesTrie(get_all_species())

    return render_template(
        "review.html",
        perch_mount_name=perch_mount_name,
        check_date=check_date,
        occurrences=occurrences,
    )


@app.route("/_species_prediction", methods=["GET", "POST"])
def species_perdiction():
    word = request.form.get("species-input")
    results = species_trie.search(word)
    return jsonify(results)


if __name__ == "__main__":
    app.run(debug=True)
