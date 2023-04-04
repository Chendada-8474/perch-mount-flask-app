SECTION_TABLE_NAME = "perch-mount-376408.perch_mount_db.sections"
OCCURRENCE_TABLE_NAME = "perch-mount-376408.perch_mount_db.occurrence_test"
RAW_MEDIA_TABLE_NAME = "perch-mount-376408.perch_mount_db.raw_media_test"

DATETIME_FROMAT = "%Y-%m-%d %H:%M:%S"
DATE_FROMAT = "%Y-%m-%d"

INDIVIDUAL_COL_NAME = (
    "taxon_order_by_ai",
    "taxon_order_by_human",
    "main_behavior_ch",
    "main_behavior_eng",
    "secondary_behavior_ch",
    "secondary_behavior_eng",
    "prey_ch",
    "prey_eng",
    "adult",
    "tagged",
    "transmitter",
    "xmin",
    "xmax",
    "ymin",
    "ymax",
    "featured",
)

MEDIUM_COL_NAME = ("medium_datetime", "medium_date", "object_id")


from datetime import datetime, timezone, date

raw_media = [
    {
        "medium_datetime": datetime(2021, 10, 27, 5, 43, 30, tzinfo=timezone.utc),
        "medium_date": date(2021, 10, 27),
        "perch_mount_id": 1,
        "perch_mount_name": "九地樹林",
        "detected_date": "2023-03-25",
        "object_id": "64168e9a697b9520481c7f18",
        "file_issue": None,
        "path": "img/img004.jpg",
    },
    {
        "medium_datetime": datetime(2021, 10, 28, 5, 29, 8, tzinfo=timezone.utc),
        "medium_date": date(2021, 10, 28),
        "perch_mount_id": 1,
        "perch_mount_name": "九地樹林",
        "detected_date": "2023-03-25",
        "object_id": "64168e9a697b9520481c7f30",
        "file_issue": None,
        "path": "img/img004.jpg",
    },
    {
        "medium_datetime": datetime(2021, 10, 28, 17, 50, 20, tzinfo=timezone.utc),
        "medium_date": date(2021, 10, 28),
        "perch_mount_id": 1,
        "perch_mount_name": "九地樹林",
        "detected_date": "2023-03-25",
        "object_id": "64168e9a697b9520481c7f34",
        "file_issue": None,
        "path": "img/img004.jpg",
    },
    {
        "medium_datetime": datetime(2021, 10, 28, 17, 50, 21, tzinfo=timezone.utc),
        "medium_date": date(2021, 10, 28),
        "perch_mount_id": 1,
        "perch_mount_name": "九地樹林",
        "detected_date": "2023-03-25",
        "object_id": "64168e9a697b9520481c7f35",
        "file_issue": None,
        "path": "img/img004.jpg",
    },
    {
        "medium_datetime": datetime(2021, 10, 28, 5, 29, 11, tzinfo=timezone.utc),
        "medium_date": date(2021, 10, 28),
        "perch_mount_id": 1,
        "perch_mount_name": "九地樹林",
        "detected_date": "2023-03-25",
        "object_id": "64168e9a697b9520481c7f32",
        "file_issue": None,
        "path": "img/img004.jpg",
    },
    {
        "medium_datetime": datetime(2021, 10, 28, 17, 50, 19, tzinfo=timezone.utc),
        "medium_date": date(2021, 10, 28),
        "perch_mount_id": 1,
        "perch_mount_name": "九地樹林",
        "detected_date": "2023-03-25",
        "object_id": "64168e9a697b9520481c7f33",
        "file_issue": None,
        "path": "img/img004.jpg",
    },
    {
        "medium_datetime": datetime(2021, 10, 28, 5, 29, 9, tzinfo=timezone.utc),
        "medium_date": date(2021, 10, 28),
        "perch_mount_id": 1,
        "perch_mount_name": "九地樹林",
        "detected_date": "2023-03-25",
        "object_id": "64168e9a697b9520481c7f31",
        "file_issue": None,
        "path": "img/img004.jpg",
    },
    {
        "medium_datetime": datetime(2021, 10, 29, 5, 25, 50, tzinfo=timezone.utc),
        "medium_date": date(2021, 10, 29),
        "perch_mount_id": 1,
        "perch_mount_name": "九地樹林",
        "detected_date": "2023-03-25",
        "object_id": "64168e9a697b9520481c80b8",
        "file_issue": None,
        "path": "img/img004.jpg",
    },
    {
        "medium_datetime": datetime(2021, 10, 29, 5, 34, 4, tzinfo=timezone.utc),
        "medium_date": date(2021, 10, 29),
        "perch_mount_id": 1,
        "perch_mount_name": "九地樹林",
        "detected_date": "2023-03-25",
        "object_id": "64168e9a697b9520481c80bc",
        "file_issue": None,
        "path": "img/img004.jpg",
    },
    {
        "medium_datetime": datetime(2021, 10, 29, 5, 25, 49, tzinfo=timezone.utc),
        "medium_date": date(2021, 10, 29),
        "perch_mount_id": 1,
        "perch_mount_name": "九地樹林",
        "detected_date": "2023-03-25",
        "object_id": "64168e9a697b9520481c80b7",
        "file_issue": None,
        "path": "img/img004.jpg",
    },
    {
        "medium_datetime": datetime(2021, 11, 2, 17, 12, 43, tzinfo=timezone.utc),
        "medium_date": date(2021, 11, 2),
        "perch_mount_id": 1,
        "perch_mount_name": "九地樹林",
        "detected_date": "2023-03-25",
        "object_id": "64168e9a697b9520481c8505",
        "file_issue": None,
        "path": "img/img004.jpg",
    },
]
