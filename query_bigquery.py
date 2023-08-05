from config import *
from datetime import datetime
from query_mysql import (
    get_habitat_by_id,
    get_project_by_id,
    get_id_by_perch_mount_name,
)
from google.cloud import bigquery
import pandas as pd
import os

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = BIGQUERY_KEY_PATH
client = bigquery.Client()


def get_occurrence_by_object_id(medium_date: str, object_id: str):
    query = f"""
        SELECT
            common_name_by_ai,
            taxon_order_by_human,
            common_name_by_human,
            medium_datetime,
            prey,
            tagged,
            ring_number,
            file_type,
            xmin,
            xmax,
            ymin,
            ymax,
            perch_mount_name,
            object_id,
        FROM {OCCURRENCE_TABLE_NAME}
        WHERE
            object_id = '{object_id}' AND
            DATE(medium_datetime) = '{medium_date}'
        """

    query_job = client.query(query)
    return query_job.result()


def get_section_condition(perch_mount_name, check_date):
    query = f"""
    SELECT start_time, end_time
    FROM `{SECTION_TABLE_NAME}`
    WHERE perch_mount_name = '{perch_mount_name}' and check_date = '{check_date}'
    """
    query_job = client.query(query)
    start_time = end_time = None
    for row in query_job:
        start_time = row["start_time"]
        end_time = row["end_time"]
    return start_time, end_time


def get_occurrence_by_section(
    perch_mount_name, start_time: datetime, end_time: datetime, limit=99999
):
    start_date = start_time.strftime(DATE_FROMAT)
    end_date = end_time.strftime(DATE_FROMAT)
    start_datetime = start_time.strftime(DATETIME_FROMAT)
    end_datetime = end_time.strftime(DATETIME_FROMAT)
    query = f"""
    SELECT * FROM `{OCCURRENCE_TABLE_NAME}`
    WHERE
        perch_mount_name = '{perch_mount_name}' and
        medium_date >= '{start_date}' and
        medium_date <= '{end_date}' and
        medium_datetime >= '{start_datetime}' and
        medium_datetime <= '{end_datetime}' and
        taxon_order_by_human IS NULL
    LIMIT {limit}
    """
    return client.query(query)


def get_any_occurrences(perch_mount_name, limit=500):
    query = f"""
    SELECT * FROM `{OCCURRENCE_TABLE_NAME}`
        WHERE
        perch_mount_name = '{perch_mount_name}' and
        taxon_order_by_human IS NULL
    LIMIT {limit}
    """
    return client.query(query)


def insert_occurrences(raw_media):
    errors = client.insert_rows_json(OCCURRENCE_TABLE_NAME, raw_media)
    return errors


def insert_perch_mount(variable_table):
    perch_mount_id = get_id_by_perch_mount_name(variable_table["perch_mount_name"])
    habitat = get_habitat_by_id(variable_table["habitat_id"])
    note = variable_table["note"] if variable_table["note"] else None
    row = [
        {
            "perch_mount_name": variable_table["perch_mount_name"],
            "perch_mount_id": perch_mount_id,
            "latitude": variable_table["latitude"],
            "longitude": variable_table["longitude"],
            "habitat_ch": habitat.habitat_ch_name,
            "habitat_eng": habitat.habitat_eng_name,
            "project": get_project_by_id(variable_table["project_id"]).project_name,
            "note": note,
        }
    ]
    errors = client.insert_rows_json(PERCH_MOUNT_TABLE_NAME, row)
    return errors


def insert_events(events):
    errors = client.insert_rows_json(EVENT_TABLE_NAMW, events)
    return errors


def insert_operation(
    user: str,
    operation: str,
    processed_amount: int,
    perch_mount_name: str,
):
    now = datetime.now().strftime("%Y-%m-%dT%H:%M:%S.%fZ")
    operation = {
        "user": user,
        "operation": operation,
        "processed_amount": processed_amount,
        "perch_mount_name": perch_mount_name,
        "operation_timestamp": now,
    }
    errors = client.insert_rows_json(OPERATION_TABLE_NAMW, [operation])
    return errors


def delete_occurences_by_ids(object_ids: list):
    n = len(object_ids)
    object_ids = tuple(object_ids)
    if not n:
        return
    elif n == 1:
        object_ids = str(object_ids).replace(",", "")
    statement = f"""
    DELETE FROM `{OCCURRENCE_TABLE_NAME}`
    WHERE object_id IN {object_ids};
    """
    query_job = client.query(statement)
    query_job.result()


def update_checker(perch_mount_name, check_date, checker, col="reviewer"):
    statement = f"""
    UPDATE `{SECTION_TABLE_NAME}`
    SET {col} = '{checker}'
    WHERE 
        perch_mount_name = '{perch_mount_name}' AND
        check_date = '{check_date}'
    """
    query_job = client.query(statement)
    query_job.result()


def update_perch_mount_status(perch_mount_id, status):
    statement = f"""
    UPDATE `{PERCH_MOUNT_TABLE_NAME}`
    SET terminated = {status}
    WHERE
        perch_mount_id = {perch_mount_id}
    """
    query_job = client.query(statement)
    query_job.result()


def occurrence_for_insert(data, perch_mount_name, var_dict):
    occurrence = []
    for medium in data["occurrences"]:
        if medium["is_image"]:
            medium["file_type"] = "image"
        else:
            medium["file_type"] = "video"
            medium["xmax"] = None
            medium["xmin"] = None
            medium["ymax"] = None
            medium["ymin"] = None

        for individual in medium["individuals"]:
            if individual["common_name_by_ai"]:
                individual["taxon_order_by_ai"] = var_dict.query_taxon_order(
                    individual["common_name_by_ai"]
                )
            else:
                individual["taxon_order_by_ai"] = None

            individual["taxon_order_by_human"] = var_dict.query_taxon_order(
                individual["common_name_by_human"]
            )

            temp_indi = individual.copy()
            temp_medium = medium.copy()
            temp_medium["perch_mount_name"] = perch_mount_name
            temp_medium.pop("individuals")
            temp_medium.pop("is_image")
            occurrence.append(temp_indi | temp_medium)
    return occurrence


def event_for_insert(data: list, perch_mount_name, vardict):
    events = []
    for event in data:
        event["event_chinese"] = vardict.query_event_name(
            int(event["event_id"]), lang="ch"
        )
        event["event_english"] = vardict.query_event_name(
            int(event["event_id"]), lang="eng"
        )
        event["perch_mount_name"] = perch_mount_name
        events.append(event)
    return events


def delete_occurrence_by_id(medium_date: str, object_id: str):
    statement = f"""
    DELETE FROM `{OCCURRENCE_TABLE_NAME}`
    WHERE
        DATE(medium_datetime) = '{medium_date}' and
        object_id = '{object_id}';
    """
    query_job = client.query(statement)
    query_job.result()


if __name__ == "__main__":
    insert_operation()
