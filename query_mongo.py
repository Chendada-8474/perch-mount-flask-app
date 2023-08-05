from pymongo import MongoClient
from bson import ObjectId
import config

mongo_client = MongoClient("localhost", 27017)
database = mongo_client[config.MANGO_DATABASE_NAME]
species_collection = database[config.MANGO_SPECIES_COLLECTION_NAME]
file_collection = database[config.MANGO_FILE_COLLECTION_NAME]


def get_all_species(field={}):
    all_species = species_collection.find({}, field)
    return all_species


def look_up_species(taxon_order):
    species = species_collection.find_one({"taxon_order": taxon_order})
    return species


def get_path_by_object_id(object_id: str):
    object = file_collection.find_one({"_id": ObjectId(object_id)}, {"path": 1})
    if object:
        return object["path"]


def delete_many_files_by_ids(object_ids: list):
    for object_id in object_ids:
        file_collection.delete_one({"_id": ObjectId(object_id)})


def species_called(taxon_order):
    species_collection.update_one(
        {"taxon_order": taxon_order}, {"$inc": {"called_count": 1}}
    )


if __name__ == "__main__":
    sp = get_all_species(
        field=["chinese_common_name", "english_common_name", "taxon_order"]
    )
    for s in sp:
        print(s)
