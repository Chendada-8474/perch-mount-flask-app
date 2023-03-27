from flask import Flask, render_template
from form import SectionSelectForm
from query_mongo import *

app = Flask(__name__)
app.config["SECRET_KEY"] = "key"
species = get_species()


@app.route("/", methods=["GET", "POST"])
def index():
    section_select_form = SectionSelectForm()
    if section_select_form.validate_on_submit():
        return "success"

    return render_template(
        "index.html",
        section_select_form=section_select_form,
    )


@app.route("/<string:perch_mount_name>/<string:check_date>")
def review(perch_mount_name, check_date):
    species = get_species()
    return render_template(
        "review.html",
        perch_mount_name=perch_mount_name,
        check_date=check_date,
        species=species,
    )


if __name__ == "__main__":
    app.run(debug=True)
