import query_mysql
import query_bigquery
import query_mongo
from config import *
from flask_restful import Resource, reqparse
from flask import request, json
from datetime import datetime
from tool import VariableDictionary

all_speices = query_mongo.get_all_species()
all_prey = query_mysql.get_preys()
all_behavior = query_mysql.get_behaviors()
all_event = query_mysql.get_events()
var_dict = VariableDictionary(all_speices, all_prey, all_behavior, all_event)


class PendingDetectedMedia(Resource):
    def get(self, perch_mount_id):
        peding_detected = query_mysql.get_date_pending_detected_media_by_id(
            perch_mount_id
        )
        peding_empty = query_mysql.get_date_pending_empty_media_by_id(perch_mount_id)

        detected_seq = []
        empty_seq = []

        for medium in peding_detected:
            detected_seq.append(
                (medium.medium_date.strftime(DATE_FROMAT), medium.pending_count)
            )

        for medium in peding_empty:
            empty_seq.append(
                (medium.medium_date.strftime(DATE_FROMAT), medium.pending_count)
            )

        data = {
            "detected_seq": detected_seq,
            "empty_seq": empty_seq,
        }

        return data


class OccurenceUpdate(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument("rows", type=str)

    def get(self, medium_date, object_id):
        occurrences = query_bigquery.get_occurrence_by_object_id(medium_date, object_id)
        rows = []
        for row in occurrences:
            r = dict(row)
            r["common_name_by_ai"] = (
                "" if not r["common_name_by_ai"] else r["common_name_by_ai"]
            )
            r["path"] = query_mongo.get_path_by_object_id(row["object_id"])
            r["medium_datetime"] = r["medium_datetime"].strftime(DATETIME_FROMAT)
            rows.append(r)
        return rows

    def post(self, medium_date, object_id):
        rows = json.loads(self.parser.parse_args()["rows"])
        for row in rows:
            row["taxon_order_by_ai"] = (
                var_dict.query_taxon_order(row["common_name_by_ai"])
                if row["common_name_by_ai"]
                else None
            )
            row["taxon_order_by_human"] = var_dict.query_taxon_order(
                row["common_name_by_human"]
            )
            row["xmin"] = float(row["xmin"])
            row["xmax"] = float(row["xmax"])
            row["ymin"] = float(row["ymin"])
            row["ymax"] = float(row["ymax"])

        query_bigquery.delete_occurrence_by_id(medium_date, object_id)
        results = query_bigquery.insert_occurrences(rows)
        return {"message": results}


class User(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument("email", type=str, required=True)
    parser.add_argument("position_id", type=int, required=True)
    parser.add_argument("admin", type=bool, required=True)

    def get(self, user_id):
        return {"user_id": user_id}

    def post(self, user_id):
        data = self.parser.parse_args()
        query_mysql.update_user(
            user_id, data["email"], data["admin"], data["position_id"]
        )
        return {"user_id": user_id, "message": "update successed"}


class FeatureMedia(Resource):
    def delete(self, feature_medium_id):
        query_mysql.delete_featured_medium(feature_medium_id)
        return {"object_id": feature_medium_id, "message": "medium deleted"}


class ClaimPerchMount(Resource):
    def post(self, perch_mount_id: int, member_id: int):
        query_mysql.update_perch_mount_claim(perch_mount_id, member_id)

    def delete(self, perch_mount_id: int, member_id: int):
        query_mysql.update_perch_mount_claim(perch_mount_id, None)


class PriorityPerchMount(Resource):
    def post(self, perch_mount_id: int, priority: int):
        priority = priority == 1
        query_mysql.update_perch_mount_priority(perch_mount_id, priority)
