from google.cloud import bigquery
from config import *
from datetime import datetime
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
