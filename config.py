from datetime import datetime

SECTION_TABLE_NAME = "perch-mount-376408.perch_mount_db.section"
OCCURRENCE_TABLE_NAME = "perch-mount-376408.perch_mount_db.occurrence"
PERCH_MOUNT_TABLE_NAME = "perch-mount-376408.perch_mount_db.perch_mount"
EVENT_TABLE_NAMW = "perch-mount-376408.perch_mount_db.event"
OPERATION_TABLE_NAMW = "perch-mount-376408.perch_mount_db.user_operation"

IMAGE_EXTENSIONS = ("bmp", "jpg", "jpeg", "png", "tif", "tiff", "dng")
VIDEO_EXTENSIONS = ("mov", "avi", "mp4", "mpg", "mpeg", "m4v", "wmv", "mkv")

EMPTY_DES_DIR = "Z:/棲架資料庫/空拍"
BIGQUERY_KEY_PATH = "D:/python/perch-mount-flask-app/connect_config/perch-mount-376408-db870716f115.json"

DATETIME_FROMAT = "%Y-%m-%d %H:%M:%S"
DATE_FROMAT = "%Y-%m-%d"

EARLEIST_DATETIME = "2000-01-01 00:00:00"
DATETIME_NOW = datetime.now().strftime(DATETIME_FROMAT)

MEDIA_PER_PAGE_EMPTY_CHECK = 250
MEDIA_PER_PAGE_REVIEW = 100
BIRD_SP_TAXON_ID = 35133

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

MEDIUM_COL_NAME = (
    "medium_datetime",
    "medium_date",
    "object_id",
    "perch_mount_id",
    "perch_mount_name",
)

MANGO_DATABASE_NAME = "perch_mount"
MANGO_FILE_COLLECTION_NAME = "files"
MANGO_SPECIES_COLLECTION_NAME = "species"
# MANGO_DATABASE_NAME = "test_database"
# MANGO_FILE_COLLECTION_NAME = "test_file"
# MANGO_SPECIES_COLLECTION_NAME = "test_species"

NEW_TASKS_DESTINATION = "D:/python/perch-mount-schedule-detect/tasks/new_tasks"
