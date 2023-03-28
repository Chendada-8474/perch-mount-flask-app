from pymongo import MongoClient
from bson import ObjectId
import json
import math

mongo_client = MongoClient("localhost", 27017)
database = mongo_client["perch_mount"]
species_collection = database["species"]
file_collection = database["file"]


def get_all_species():
    all_species = species_collection.find({})
    return all_species


def look_up_species(taxon_order):
    species = species_collection.find_one({"taxon_order": taxon_order})
    return species


def get_path_by_object_id(object_id: str):
    path = file_collection.find_one({"_id": ObjectId(object_id)})["path"]
    return path


if __name__ == "__main__":
    sp = look_up_species(11742)
    print(sp)
