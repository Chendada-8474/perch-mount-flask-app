from config import *
from datetime import datetime
from query_mysql import (
    get_habitat_by_id,
    get_projects_by_id,
    get_projects_by_id,
    get_id_by_perch_mount_name,
)
from google.cloud import bigquery
import pandas as pd
import os

os.environ[
    "GOOGLE_APPLICATION_CREDENTIALS"
] = "./connect_config/perch-mount-376408-db870716f115.json"
client = bigquery.Client()


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
    perch_mount_name, start_time: datetime, end_time: datetime
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
        medium_datetime <= '{end_datetime}'
    """
    return client.query(query)


def get_unempty_check_occurrence_by_section(perch_mount_name, start_time, end_time):
    start_date = start_time.strftime(DATE_FROMAT)
    end_date = end_time.strftime(DATE_FROMAT)
    start_datetime = start_time.strftime(DATETIME_FROMAT)
    end_datetime = end_time.strftime(DATETIME_FROMAT)
    query = f"""
    SELECT * FROM `{RAW_MEDIA_TABLE_NAME}`
    WHERE
        perch_mount_name = '{perch_mount_name}' and
        medium_date >= '{start_date}' and
        medium_date <= '{end_date}' and
        medium_datetime >= '{start_datetime}' and
        medium_datetime <= '{end_datetime}' and
        detected_date IS NOT NULL
    """

    return client.query(query)


def insert_not_empty_media(raw_media):
    errors = client.insert_rows_json(OCCURRENCE_TABLE_NAME, raw_media)
    return errors


def insert_bq_perch_mount(perch_mount_form):
    perch_mount_id = get_id_by_perch_mount_name(perch_mount_form.perch_mount_name.data)
    habitat = get_habitat_by_id(perch_mount_form.habitat_id.data)
    project_names = [
        project.project_name
        for project in get_projects_by_id(perch_mount_form.project_id.data)
    ]
    row = [
        {
            "perch_mount_name": perch_mount_form.perch_mount_name.data,
            "perch_mount_id": perch_mount_id,
            "latitude": perch_mount_form.latitude.data,
            "longitude": perch_mount_form.longitude.data,
            "longitude": perch_mount_form.longitude.data,
            "habitat_ch": habitat.habitat_ch_name,
            "habitat_eng": habitat.habitat_eng_name,
            "project": project_names,
            "note": perch_mount_form.note.data,
        }
    ]
    print(row)
    # client.insert_rows_json(PERCH_MOUNT_TABLE_NAME, row)
    return


def delete_raw_media_by_ids(object_ids):
    n = len(object_ids)
    object_ids = tuple(object_ids)
    if not n:
        return
    elif n == 1:
        object_ids = str(object_ids).replace(",", "")
    statement = f"""
    DELETE FROM `{RAW_MEDIA_TABLE_NAME}`
    WHERE object_id IN {object_ids};
    """
    query_job = client.query(statement)
    query_job.result()


if __name__ == "__main__":
    start_time = datetime.strptime("2022-03-31 15:45:00", DATETIME_FROMAT)
    end_time = datetime.strptime("2022-04-09 13:54:00", DATETIME_FROMAT)
    print(start_time, end_time)
    test = get_occurrence_by_section("土庫南側", start_time, end_time)
    print(list(test))
    # for t in test:
    #     print(dict(t))
    #     break
    # test.to_csv("./demo_data/occurence_in_demo_section.csv", index=False)
