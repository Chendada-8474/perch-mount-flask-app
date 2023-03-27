import json


def get_species():
    with open("demo_data/species.json", encoding="utf-8") as f:
        species = json.load(f)
    return species
